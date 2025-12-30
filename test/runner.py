import asyncio
import csv
import logging
import time
from datetime import datetime

from main import MCPClient
from test.prompts import PROMPTS_TO_TEST

# Configuration
OUTPUT_CSV = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# List of models to test (OpenRouter IDs)
MODELS_TO_TEST = [
    # "openai/gpt-4o",
    # "openai/gpt-4o-mini",
    # "openai/gpt-5",
    "openai/gpt-5-mini",
    "openai/gpt-5-nano",
    # # "anthropic/claude-4.5-sonnet",  # apparently does not support function calling
    "deepseek/deepseek-chat",
    "deepseek/deepseek-v3.2",
    # "deepseek/deepseek-r1-0528",
    # "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-flash-lite",
]


# Configure Logging for the test runner specifically
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRunner")


async def test_model(model_name: str) -> list[dict]:
    """Run all prompts for a single model. Returns list of result rows."""
    results = []
    logger.info(f"--- Starting tests for Model: {model_name} ---")

    try:
        client = MCPClient(system_prompt_filename="GraphQLSystemPrompt.md")

        # DYNAMICALLY OVERRIDE THE MODEL
        # This overrides the hardcoded self.model in the __init__
        client.model = model_name

        # Connect to server
        logger.info(f"Connecting to MCP server for {model_name}...")
        await client.connect_to_server()

        for prompt_data in PROMPTS_TO_TEST:
            p_id = prompt_data["id"]
            p_cat = prompt_data["category"]
            p_text = prompt_data["text"]

            logger.info(f"[{model_name}] Running Prompt {p_id} ({p_cat})...")

            start_time = time.time()
            result_text = ""
            error_text = ""
            success = False

            try:
                # process_query is the main entry point
                result_text = await client.process_query(p_text)
                success = True
            except Exception as e:
                error_text = str(e)
                logger.error(f"[{model_name}] Error processing prompt {p_id}: {e}")

            end_time = time.time()
            duration = round(end_time - start_time, 2)

            # Collect result
            results.append(
                {
                    "Model": model_name,
                    "Prompt_ID": p_id,
                    "Prompt_Category": p_cat,
                    "Prompt_Text": p_text,
                    "Success": success,
                    "Time_Sec": duration,
                    "Response": result_text.replace(
                        "\n", "\\n"
                    ),  # Escape newlines for CSV safety
                    "Error": error_text,
                }
            )

            # Optional: small sleep to avoid rate limits
            await asyncio.sleep(1)

        await client.cleanup()
        logger.info(f"--- Completed tests for Model: {model_name} ---")

    except Exception as e:
        logger.critical(
            f"Failed to initialize or connect with model {model_name}: {e}"
        )

    return results


async def run_tests():
    # Prepare CSV file
    fieldnames = [
        "Model",
        "Prompt_ID",
        "Prompt_Category",
        "Prompt_Text",
        "Success",
        "Time_Sec",
        "Response",
        "Error",
    ]

    # Run all models in parallel, but prompts within each model are serialized
    tasks = [test_model(model_name) for model_name in MODELS_TO_TEST]
    all_results = await asyncio.gather(*tasks)

    # Flatten results and write to CSV
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for model_results in all_results:
            for row in model_results:
                writer.writerow(row)

    logger.info(f"Testing complete. Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(run_tests())
