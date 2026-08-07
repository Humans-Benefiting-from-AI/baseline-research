import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_batch.py <batch_id>")
        sys.exit(1)
        
    batch_id = sys.argv[1]
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    batch = client.batches.retrieve(batch_id)
    print(f"Batch ID: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"Completed Requests: {batch.request_counts.completed}")
    print(f"Failed Requests: {batch.request_counts.failed}")
    print(f"Total Requests: {batch.request_counts.total}")
    
    if batch.status == "completed":
        print("\nJob is COMPLETE. To download results:")
        print(f"output_file_id = '{batch.output_file_id}'")
        print("You can download it using the OpenAI dashboard or via the API.")
        
if __name__ == "__main__":
    main()
