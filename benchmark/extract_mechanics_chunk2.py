import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_logic(text_chunk):
    system_prompt = """
    You are an expert at extracting formal logical structures from Halachic texts.
    Your goal is to find instances where the scholar explains a specific *Halachic mechanic*—especially places where a structural rule overrides a statistical probability, where a specific hierarchy of authority is invoked, or where a common assumption is overturned by a precise legal distinction.
    
    Return a JSON object with a key "mechanics" containing an array of objects:
    {
      "mechanics": [
        {
          "mechanic_name": "Name of the concept",
          "scenario": "A brief, 2-3 sentence hypothetical scenario that tests this mechanic.",
          "trap": "What would a simplistic AI guess?",
          "ground_truth": "The correct Halachic ruling.",
          "explanation": "The scholar's precise structural reason for the ruling based on the text."
        }
      ]
    }
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
        print(f"Error during extraction: {e}")
        return []

def main():
    transcript_path = "/Users/elieschulman/Projects/yutorah-local-pipeline/data/schwartz-ruvi-catalog/transcripts/english/schwartz_ruvi_003.txt"
    output_path = "/Users/elieschulman/Projects/AI-plus-Orthodoxy-Platform-Option-Map/benchmark/extracted_v2_mechanics.json"
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        full_text = f.read()
        
    # Try the first 20,000 characters (often contains the thesis/core shiur topic)
    chunk = full_text[:20000]
    
    print("Extracting Halachic mechanics using GPT-4o (Chunk 1/Start of text)...")
    mechanics = extract_logic(chunk)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mechanics, f, indent=2)
        
    print(f"Successfully extracted {len(mechanics)} mechanics. Saved to {output_path}")

if __name__ == "__main__":
    main()
