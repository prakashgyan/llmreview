import os
import sys
import argparse
from pathlib import Path
from openai import AzureOpenAI
from get_diff import get_file_diff_between_branches
from dotenv import load_dotenv



def prompt_for_env_if_missing(dotenv_path=".llmreviewcfg"):
    if not os.path.exists(dotenv_path):
        print("First-time setup: Please enter the following Azure OpenAI configuration details:")
        env_vars = {
            "AZURE_OPENAI_ENDPOINT": input("Azure OpenAI Endpoint: ").strip(),
            "AZURE_OPENAI_MODEL_NAME": input("Azure OpenAI Model Name: ").strip(),
            "AZURE_OPENAI_DEPLOYMENT_NAME": input("Azure OpenAI Deployment Name: ").strip(),
            "AZURE_OPENAI_API_KEY": input("Azure OpenAI API Key: ").strip(),
        }

        with open(dotenv_path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print(f"✅ Configuration saved to {dotenv_path}\n")

    load_dotenv(dotenv_path)

prompt_for_env_if_missing()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2024-12-01-preview"

REVIEW_LOCATION = "reviews"
os.makedirs(REVIEW_LOCATION, exist_ok=True)

with open(Path(__file__).parent.resolve() / "instructions/code_review.txt", "r", encoding="utf-8", errors="ignore") as file:
    INSTRUCTIONS = file.read()


client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


def main(diff_data, file_path):

    response = client.chat.completions.create(
        stream=True,
        messages=[
            {
                "role": "system",
                "content": INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": diff_data,
            }
        ],
        max_tokens=4096,
        temperature=0.1,
        top_p=0.1,
        model=deployment,
    )

    for update in response:
        full_content = ""
        if update.choices:
            print(update.choices[0].delta.content or "", end="")
            # Collect the entire response content
            full_content += update.choices[0].delta.content or ""

        # Save the complete content to a file
        review_file = os.path.join(REVIEW_LOCATION, f"{os.path.basename(file_path)}.md")
        with open(review_file, "a", encoding="utf-8") as out_file:
            out_file.write(full_content)
    print(f"\nReview saved to {review_file}")

    client.close()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""
        Compare a file between two git branches and get a review using LLM and our coding standard.
        refer https://dev.azure.com/FrieslandCampina/fc-da-azure-data-analytics-platform/_wiki/wikis/Data%20and%20Analytics/17968/Coding-Standards-and-Best-Practices
        """
    )
    parser.add_argument(
        "source_branch",
        type=str,
        help="The name of the source git branch"
    )
    parser.add_argument(
        "target_branch",
        type=str,
        help="The name of the target git branch"
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the file for which to compute the diff"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    diff_data = get_file_diff_between_branches(
        args.source_branch,
        args.target_branch,
        args.file_path
    )
    main(diff_data, args.file_path)
    # file = "src/main.py"
    # main(get_file_diff_between_branches("feature/core_items", "master", file), file)
