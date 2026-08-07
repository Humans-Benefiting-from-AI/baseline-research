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
    
    If you find such a mechanic in the text, extract it in the following JSON format:
    {
      "mechanic_name": "Name of the concept (e.g. Kavu'a, Kim Li)",
      "scenario": "A brief, 2-3 sentence hypothetical scenario that tests this mechanic.",
      "trap": "What would a purely statistical or simplistic LLM guess?",
      "ground_truth": "The correct Halachic ruling.",
      "explanation": "The scholar's precise structural reason for the ruling."
    }
    
    If no such specific structural mechanic exists in the text chunk, return an empty array [].
    Output ONLY a valid JSON array of objects.
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
        # Assuming the model wraps the array in an object like {"mechanics": [...]} to be valid json_object
        result = json.loads(response.choices[0].message.content)
        if isinstance(result, dict) and "mechanics" in result:
            return result["mechanics"]
        elif isinstance(result, list):
            return result
        return []
    except Exception as e:
        print(f"Error during extraction: {e}")
        return []

def main():
    transcript_path = "/Users/elieschulman/Projects/yutorah-local-pipeline/data/schwartz-ruvi-catalog/transcripts/english/schwartz_ruvi_003.txt"
    output_path = "/Users/elieschulman/Projects/AI-plus-Orthodoxy-Platform-Option-Map/benchmark/extracted_v2_mechanics.json"
    
    print(f"Reading {transcript_path}...")
    with open(transcript_path, 'r', encoding='utf-8') as f:
        full_text = f.read()
        
    # Take a 15,000 character slice from the middle of the document to find dense logic
    # (Since it's a massive 5MB file, we chunk it. For this POC, we grab one chunk).
    mid_point = len(full_text) // 2
    chunk = full_text[mid_point:mid_point + 15000]
    
    print("Extracting Halachic mechanics using GPT-4o...")
    mechanics = extract_logic(chunk)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mechanics, f, indent=2)
        
    print(f"Successfully extracted {len(mechanics)} mechanics. Saved to {output_path}")

if __name__ == "__main__":
    main()
