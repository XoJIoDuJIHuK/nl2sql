import os
import csv
import json
import argparse
import pandas as pd
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

EVALUATOR_MODEL = "google/gemini-3-pro-preview"

SYSTEM_PROMPT_PATH = os.path.join("system_prompts", "GraphQLSystemPrompt.md")


class Evaluator:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        # Load the original system prompt to give the Judge context
        # about the specific database schema and math rules.
        if os.path.exists(SYSTEM_PROMPT_PATH):
            with open(SYSTEM_PROMPT_PATH, "r") as f:
                self.domain_context = f.read()
        else:
            print(
                "Warning: System prompt file not found. Evaluation might be less accurate."
            )
            self.domain_context = (
                "Context: Industrial Cluster Math Model and Postgres DB."
            )

    def construct_batch_evaluation_prompt(
        self, questions: List[str], answers: List[str]
    ) -> list:
        """
        Constructs a batch prompt for evaluating all responses at once.
        Returns a list of ratings (one per answer) and optionally reasonings.
        """

        judge_system_instruction = f"""
        You are an expert AI Auditor and SQL Architect.
        Your task is to evaluate the quality of responses provided by anonymous AI assistants.
        The assistants have access to a database through SQL adapter or external GraphQL server and are able to provide actual data from the database. In that case assess response quality (how relevant data is, how much unneccessary data is there, ...)

        ### The Domain Context
        The assistants were operating under the following constraints and schema:
        ---
        {self.domain_context}
        ---

        ### Scoring Criteria (1-10)
        - **10 (Perfect)**: Valid SQL/JSON/data response, adheres to all axioms, follows specific formatting constraints (e.g., return 0/1 for axioms), handles the math logic correctly.
        - **8-9**: Correct logic but minor formatting issues or verbose explanations when not asked.
        - **5-7**: Plausible SQL/JSON/data response but hallucinated table names or slight logic errors.
        - **1-4**: Invalid SQL, Hallucination, Python code instead of SQL, or complete failure to answer.

        ### Output Format
        Return ONLY a JSON object with two arrays:
        {{
            "ratings": [<integer 1-10 for answer 1>, <integer 1-10 for answer 2>, ...],
            "reasonings": ["<short explanation for answer 1>", "<short explanation for answer 2>", ...]
        }}

        The order of ratings and reasonings MUST match the order of the questions provided below.
        """

        # Build user content with all questions and answers
        qa_pairs = []
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            qa_pairs.append(
                f"""
### Pair {i}
**User Question:**
{q}

**Assistant's Response:**
{a}
---
"""
            )

        user_content = f"""
Evaluate the following question-answer pairs. Return ratings and reasonings for each pair in order.

{''.join(qa_pairs)}
"""

        return [
            {"role": "system", "content": judge_system_instruction},
            {"role": "user", "content": user_content},
        ]

    async def rate_responses_batch(
        self, questions: List[str], answers: List[str]
    ) -> List[Dict]:
        """
        Evaluate all responses in a single API call asynchronously.
        Returns a list of dicts with 'rating' and 'reasoning' for each answer.
        """
        messages = self.construct_batch_evaluation_prompt(questions, answers)

        try:
            response = await self.client.chat.completions.create(
                model=EVALUATOR_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temp for consistent grading
            )

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Content is None")
            result = json.loads(content)

            ratings = result.get("ratings", [])
            reasonings = result.get("reasonings", [])

            # Ensure we return one result per input
            results = []
            for i in range(len(answers)):
                results.append({
                    "rating": ratings[i] if i < len(ratings) else 0,
                    "reasoning": reasonings[i] if i < len(reasonings) else "Missing evaluation",
                })
            return results

        except Exception as e:
            print(f"Error calling Evaluator: {e}")
            return [{"rating": 0, "reasoning": f"Evaluation Failed: {e}"} for _ in answers]


def main():
    parser = argparse.ArgumentParser(description="Evaluate AI Model Results CSV")
    parser.add_argument("input_csv", help="Path to the test results CSV file")
    args = parser.parse_args()

    input_path = args.input_csv
    output_matrix_path = "evaluation_matrix.csv"
    output_details_path = "evaluation_details.csv"

    print(f"Reading data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print("Error: Input file not found.")
        return

    # Check required columns
    required_cols = ["Model", "Prompt_ID", "Prompt_Text", "Response"]
    if not all(col in df.columns for col in required_cols):
        print(f"Error: CSV must contain columns: {required_cols}")
        return

    evaluator = Evaluator()

    # Group by Model to process one model at a time
    grouped = df.groupby("Model")
    total_models = len(grouped)

    print(f"Starting batch evaluation using {EVALUATOR_MODEL}...")

    async def evaluate_all_models():
        results = []
        tasks = []
        model_info = []  # Store metadata to map results back

        current_model_idx = 0
        for model_name, group_data in grouped:
            current_model_idx += 1
            print(
                f"\n--- Preparing Model {current_model_idx}/{total_models} ({model_name}) ---"
            )

            # Collect all Q&A for this model
            questions = []
            answers = []
            prompt_ids = []

            for idx, row in group_data.iterrows():
                p_id = row["Prompt_ID"]
                question = row["Prompt_Text"]
                answer = str(row["Response"])

                questions.append(question)
                answers.append(answer)
                prompt_ids.append(p_id)

            # Store metadata for this batch
            start_idx = len(results)
            model_info.append({
                "model_name": model_name,
                "prompt_ids": prompt_ids,
                "answers": answers,
                "start_idx": start_idx,
            })

            # Create async task for this model's batch
            task = evaluator.rate_responses_batch(questions, answers)
            tasks.append(task)

        # Execute all evaluations concurrently
        print(f"\n--- Sending {len(tasks)} batch evaluation requests concurrently ---")
        eval_results_lists = await asyncio.gather(*tasks)

        # Process results
        for info, eval_results in zip(model_info, eval_results_lists):
            for p_id, answer, eval_result in zip(
                info["prompt_ids"], info["answers"], eval_results
            ):
                rating = eval_result.get("rating", 0)
                reason = eval_result.get("reasoning", "N/A")
                print(f"{info['model_name'][:20]:20} | Q:{p_id} | Score: {rating}/10")

                results.append(
                    {
                        "Model": info["model_name"],
                        "Prompt_ID": p_id,
                        "Rating": rating,
                        "Reasoning": reason,
                        "Original_Response": answer[:50] + "...",
                    }
                )

        return results

    # Run async evaluation
    results = asyncio.run(evaluate_all_models())

    # --- Generate Output ---

    # 1. Detailed CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_details_path, index=False)
    print(f"\nDetailed results saved to {output_details_path}")

    # 2. Pivot Matrix (Model x Question = Rating)
    matrix_df = results_df.pivot(index="Model", columns="Prompt_ID", values="Rating")

    # Calculate Average Score per Model
    matrix_df["Average_Score"] = matrix_df.mean(axis=1).round(2)

    # Sort by Average Score descending
    matrix_df = matrix_df.sort_values("Average_Score", ascending=False)

    matrix_df.to_csv(output_matrix_path)
    print(f"Rating Matrix saved to {output_matrix_path}")

    print("\n=== FINAL STANDINGS ===")
    print(matrix_df["Average_Score"])


if __name__ == "__main__":
    main()
