import os
import csv
import json
import time
import asyncio
import argparse
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EVALUATOR_MODEL = "google/gemini-3-pro-preview"

SYSTEM_PROMPT_PATH = os.path.join("system_prompts", "GraphQLSystemPrompt.md")


class Evaluator:
    def __init__(self):
        self.client = OpenAI(
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

    def construct_evaluation_prompt(self, question: str, answer: str) -> list:
        """
        Constructs the prompt for the Judge.
        Crucially, this does NOT include the model name (Anonymous).
        """

        judge_system_instruction = f"""
        You are an expert AI Auditor and SQL Architect.
        Your task is to evaluate the quality of a response provided by an anonymous AI assistant.
        The assistant has access to a database through SQL adapter or external GraphQL server and is able to provide actual data from the database. In that case assess response quality (how relevant data is, how much unneccessary data is there, ...)
        
        ### The Domain Context
        The assistant was operating under the following constraints and schema:
        ---
        {self.domain_context}
        ---

        ### Scoring Criteria (1-10)
        - **10 (Perfect)**: Valid SQL/JSON/data response, adheres to all axioms, follows specific formatting constraints (e.g., return 0/1 for axioms), handles the math logic correctly.
        - **8-9**: Correct logic but minor formatting issues or verbose explanations when not asked.
        - **5-7**: Plausible SQL/JSON/data response but hallucinated table names or slight logic errors.
        - **1-4**: Invalid SQL, Hallucination, Python code instead of SQL, or complete failure to answer.
        
        ### Output Format
        Return ONLY a JSON object:
        {{
            "rating": <integer 1-10>,
            "reasoning": "<short explanation>"
        }}
        """

        user_content = f"""
        ### The User Question
        {question}

        ### The Assistant's Response
        {answer}
        
        Evaluate this response.
        """

        return [
            {"role": "system", "content": judge_system_instruction},
            {"role": "user", "content": user_content},
        ]

    def rate_response(self, question: str, answer: str) -> dict:
        messages = self.construct_evaluation_prompt(question, answer)

        try:
            response = self.client.chat.completions.create(
                model=EVALUATOR_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temp for consistent grading
            )

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Content is None for answer %s" % answer)
            return json.loads(content)
        except Exception as e:
            print(f"Error calling Evaluator: {e}")
            return {"rating": 0, "reasoning": "Evaluation Failed"}


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
    results = []

    # Group by Model to process one model at a time
    grouped = df.groupby("Model")

    total_models = len(grouped)
    current_model_idx = 0

    print(f"Starting evaluation using {EVALUATOR_MODEL}...")

    for model_name, group_data in grouped:
        current_model_idx += 1
        print(
            f"\n--- Processing Model {current_model_idx}/{total_models} (Anonymous ID: M-{current_model_idx}) ---"
        )

        # Iterate through rows for this model
        for idx, row in group_data.iterrows():
            p_id = row["Prompt_ID"]
            question = row["Prompt_Text"]
            answer = str(row["Response"])  # Ensure string

            print(f"   Evaluating Q: {p_id}...", end="", flush=True)

            # Rate the response
            eval_result = evaluator.rate_response(question, answer)
            rating = eval_result.get("rating", 0)
            reason = eval_result.get("reasoning", "N/A")

            print(f" Score: {rating}/10")

            # Store Result
            results.append(
                {
                    "Model": model_name,
                    "Prompt_ID": p_id,
                    "Rating": rating,
                    "Reasoning": reason,
                    "Original_Response": answer[:50] + "...",  # Truncate for summary
                }
            )

            # Small sleep to be polite to the API rate limit
            time.sleep(1)

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
