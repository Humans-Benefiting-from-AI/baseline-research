import json
import os
import time
from dotenv import load_dotenv
import anthropic

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def evaluate_anthropic(client, prompt):
    if not client: return "SKIPPED (No Key)"
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system="You are a Halachic expert. You must output EXACTLY the requested conclusion (e.g., YES, NO, PERMITTED, FORBIDDEN, PLAINTIFF, DEFENDANT, NO SUCH TEXT) followed by a brief 1-2 sentence explanation.",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=256,
            temperature=0.0
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    input_file = "hre_results.jsonl"
    output_file = "hre_results_fixed.jsonl"
    
    with open(input_file, "r") as f:
        records = [json.loads(line) for line in f]
        
    print("Re-running Claude 3.5 Sonnet to fix 404 error...")
    
    with open(output_file, "w") as f:
        for idx, rec in enumerate(records):
            print(f"Evaluating {rec['id']}...")
            
            # Reconstruct prompt
            q_file = "hre_eval_100.jsonl"
            q_data = next(q for q in [json.loads(line) for line in open(q_file)] if q['id'] == rec['id'])
            full_prompt = f"{q_data['prompt']}\n\nTask: {q_data['eval_task']}"
            
            claude_response = evaluate_anthropic(anthropic_client, full_prompt)
            claude_score = 1 if rec['ground_truth'].lower() in claude_response.lower() else 0
            
            rec['claude-3.5-sonnet_response'] = claude_response
            rec['claude-3.5-sonnet_score'] = claude_score
            
            f.write(json.dumps(rec) + "\n")
            time.sleep(1) # simple rate limit

    os.rename(output_file, input_file)
    print("Fixed Claude results!")

if __name__ == '__main__':
    main()
