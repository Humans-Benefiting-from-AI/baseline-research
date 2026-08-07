import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-openai-key-here":
        print("ERROR: Please set your actual OPENAI_API_KEY in the .env file in the benchmark folder.")
        sys.exit(1)
        
    client = OpenAI(api_key=api_key)
    batch_file_path = "/Users/elieschulman/Projects/AI-plus-Orthodoxy-Platform-Option-Map/benchmark/batch_input_all_scholars.jsonl"
    
    if not os.path.exists(batch_file_path):
        print(f"ERROR: Cannot find {batch_file_path}")
        sys.exit(1)
        
    print(f"1. Uploading file to OpenAI...")
    try:
        with open(batch_file_path, "rb") as f:
            batch_input_file = client.files.create(
              file=f,
              purpose="batch"
            )
        file_id = batch_input_file.id
        print(f"   Success! File ID: {file_id}")
    except Exception as e:
        print(f"   Upload failed: {e}")
        sys.exit(1)
        
    print(f"2. Submitting Batch Job...")
    try:
        batch = client.batches.create(
            input_file_id=file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
              "description": "Baseline Research - Halachic Extraction V2"
            }
        )
        print(f"   Success! Batch Job ID: {batch.id}")
        print(f"   Status: {batch.status}")
        print(f"")
        print(f"Your job has been submitted! It will process over the next 24 hours at a 50% discount.")
        print(f"To check the status later, you can use the OpenAI dashboard: https://platform.openai.com/batches")
        print(f"Or you can run: python check_batch.py {batch.id}")
    except Exception as e:
        print(f"   Batch submission failed: {e}")

if __name__ == "__main__":
    main()
