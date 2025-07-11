import os
import sys
from pathlib import Path
from openai import AzureOpenAI
from get_diff import get_file_diff_between_branches
from dotenv import load_dotenv

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")



with open(Path(__file__).parent.resolve() / "instructions/code_review.txt", "r", encoding="utf-8", errors="ignore") as file:
    INSTRUCTIONS = file.read()

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


def main(diff_data):

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
        if update.choices:
            print(update.choices[0].delta.content or "", end="")

    client.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python main.py source_branch target_branch file_path")
        sys.exit(1)
    diff_data = get_file_diff_between_branches(sys.argv[1], sys.argv[2], sys.argv[3])
    main(diff_data)
