import os
import glob
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_logic(text_chunk, source_file):
    system_prompt = f"""
    You are an expert at extracting formal logical structures from Halachic texts.
    Your goal is to find instances where the scholar explains a specific *Halachic mechanic*—especially places where a structural rule overrides a statistical probability, a specific hierarchy of authority is invoked, or a common assumption/translation trap is overturned by a precise legal distinction.
    
    Return a JSON object with a key "mechanics" containing an array of objects:
    {{
      "mechanics": [
        {{
          "archetype": "Name of the concept (e.g. Linguistic Trap, Kavu'a, Kim Li)",
          "prompt": "A brief, 2-3 sentence hypothetical scenario that tests this mechanic, ending with a specific question.",
          "eval_task": "What the AI should output (e.g. 'Answer PERMITTED or FORBIDDEN' or 'Answer YES or NO').",
          "trap": "What would a simplistic or purely statistical AI guess?",
          "ground_truth": "The exact required string answer.",
          "logic_explanation": "The scholar's precise structural reason for the ruling. Cite '{source_file}'."
        }}
      ]
    }}
    If no deep mechanics are present, return {{"mechanics": []}}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_chunk}
            ],
            response_format={ "type": "json_object" },
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content).get("mechanics", [])
    except Exception as e:
        print(f"Error during extraction on {source_file}: {e}")
        return []

def main():
    transcript_dir = "/Users/elieschulman/Projects/yutorah-local-pipeline/data/schwartz-ruvi-catalog/transcripts/english"
    output_path = "/Users/elieschulman/Projects/AI-plus-Orthodoxy-Platform-Option-Map/benchmark/hre_eval_v2.jsonl"
    
    files = glob.glob(os.path.join(transcript_dir, "*.txt"))
    all_questions = []
    
    print(f"Found {len(files)} English transcript files.")
    
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"Processing {filename}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
            
        # To avoid massive API costs and timeouts during this run, we sample the first 2 chunks of 15,000 chars
        # from each file. In a full production run, this would loop over the entire length.
        chunks = [
            full_text[0:15000],
            full_text[15000:30000] if len(full_text) > 15000 else ""
        ]
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 1000:
                continue
            
            print(f"  Extracting from chunk {i+1}...")
            mechanics = extract_logic(chunk, filename)
            for m in mechanics:
                all_questions.append(m)
            
            time.sleep(1) # simple rate limit
            
    print(f"\nWriting {len(all_questions)} extracted questions to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, q in enumerate(all_questions):
            q['id'] = f"hre-v2-expert-{idx+1:03d}"
            f.write(json.dumps(q) + '\n')
            
    print("V2 Extraction Complete!")

if __name__ == "__main__":
    main()
