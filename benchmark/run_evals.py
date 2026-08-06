import json
import os
import time
from dotenv import load_dotenv

# Try to import SDKs (User will need to pip install these to run it)
try:
    from openai import OpenAI
    import anthropic
except ImportError:
    print("Please install requirements: pip install -r requirements.txt")
    exit(1)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def evaluate_openai(client, prompt):
    if not client: return "SKIPPED (No Key)"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Halachic expert. You must output EXACTLY the requested conclusion (e.g., YES, NO, PERMITTED, FORBIDDEN, PLAINTIFF, DEFENDANT, NO SUCH TEXT) followed by a brief 1-2 sentence explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def evaluate_anthropic(client, prompt):
    if not client: return "SKIPPED (No Key)"
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
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
    print("Starting Halachic Reasoning Evaluation (HRE) Harness...")
    
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

    if not openai_client and not anthropic_client:
        print("WARNING: Neither OPENAI_API_KEY nor ANTHROPIC_API_KEY found in environment. The run will be skipped.")
    
    input_file = "hre_eval_100.jsonl"
    output_file = "hre_results.jsonl"
    
    results = []
    
    with open(input_file, "r", encoding="utf-8") as f:
        questions = [json.loads(line) for line in f]
    
    print(f"Loaded {len(questions)} questions. Beginning evaluation (this may take a few minutes if rate limited)...")
    
    with open(output_file, "w", encoding="utf-8") as out_f:
        for idx, q in enumerate(questions):
            print(f"Evaluating {q['id']} ({q['archetype']})...")
            
            full_prompt = f"{q['prompt']}\n\nTask: {q['eval_task']}"
            
            gpt4o_response = evaluate_openai(openai_client, full_prompt)
            claude_response = evaluate_anthropic(anthropic_client, full_prompt)
            
            # Simple keyword matching for automated scoring (in a real run, an LLM-as-a-judge or exact regex is used)
            gpt4o_score = 1 if q['ground_truth'].lower() in gpt4o_response.lower() else 0
            claude_score = 1 if q['ground_truth'].lower() in claude_response.lower() else 0
            
            result_item = {
                "id": q["id"],
                "archetype": q["archetype"],
                "ground_truth": q["ground_truth"],
                "gpt-4o_response": gpt4o_response,
                "gpt-4o_score": gpt4o_score,
                "claude-3.5-sonnet_response": claude_response,
                "claude-3.5-sonnet_score": claude_score
            }
            
            out_f.write(json.dumps(result_item) + "\n")
            results.append(result_item)
            
            # Sleep slightly to respect basic rate limits
            time.sleep(1)
            
    print(f"Evaluation complete. Results saved to {output_file}")
    
if __name__ == "__main__":
    main()
