import os
import glob
import json
import tiktoken

def get_system_prompt(source_file):
    return f"""
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

def chunk_text(text, max_chars=15000):
    chunks = []
    for i in range(0, len(text), max_chars):
        chunks.append(text[i:i+max_chars])
    return chunks

def main():
    # All 3 scholar directories
    transcript_dirs = [
        "/Users/elieschulman/Projects/yutorah-local-pipeline/data/schwartz-ruvi-catalog/transcripts/clean",
        "/Users/elieschulman/Projects/yutorah-local-pipeline/data/schwartz-ruvi-catalog/transcripts/english",
        "/Users/elieschulman/Projects/yutorah-local-pipeline/data/twersky-catalog",
        "/Users/elieschulman/Projects/yutorah-local-pipeline/data/twersky-moshe-catalog"
    ]
    
    output_path = "/Users/elieschulman/Projects/AI-plus-Orthodoxy-Platform-Option-Map/benchmark/batch_input_all_scholars.jsonl"
    
    files = []
    for d in transcript_dirs:
        # Search recursively in the scholar folders to catch everything
        for root, _, _ in os.walk(d):
            files.extend(glob.glob(os.path.join(root, "*.txt")))
    
    unique_files = {os.path.basename(f): f for f in files}
    print(f"Found {len(unique_files)} unique transcript/text files across all 3 scholars.")
    
    request_count = 0
    total_estimated_tokens = 0
    enc = tiktoken.get_encoding("o200k_base")
    
    with open(output_path, 'w', encoding='utf-8') as out_f:
        for filename, filepath in unique_files.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                # Fallback if a file is weirdly encoded
                with open(filepath, 'r', encoding='latin-1') as f:
                    text = f.read()
                    
            chunks = chunk_text(text, max_chars=20000)
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 500:
                    continue
                
                request_count += 1
                system_prompt = get_system_prompt(filename)
                
                total_estimated_tokens += len(enc.encode(system_prompt)) + len(enc.encode(chunk))
                
                request_obj = {
                    "custom_id": f"req_{filename}_chunk_{i}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": "gpt-4o",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": chunk}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.0
                    }
                }
                out_f.write(json.dumps(request_obj) + '\n')
                
    print(f"\nPrepared Batch API input file: {output_path}")
    print(f"Total Requests (Chunks): {request_count}")
    print(f"Total Estimated Input Tokens: {total_estimated_tokens:,}")
    estimated_cost = (total_estimated_tokens / 1_000_000) * 2.50
    print(f"Estimated OpenAI Batch API Cost (Input): ${estimated_cost:.2f}")
    
    print("\nTo submit this batch to OpenAI, run:")
    print("python submit_batch.py")

if __name__ == "__main__":
    main()
