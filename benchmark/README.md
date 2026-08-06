# Halachic Reasoning Evaluation (HRE) Harness

This directory contains the 100-question JSONL dataset and the Python evaluation harness used to run the tests against frontier AI models (OpenAI's `gpt-4o` and Anthropic's `claude-3.5-sonnet`).

## How to Run the Benchmark

1. Navigate to this directory:
   ```bash
   cd benchmark
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   Create a `.env` file in this directory and add your keys:
   ```env
   OPENAI_API_KEY=sk-your-openai-key
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
   ```

4. Execute the evaluation script:
   ```bash
   python run_evals.py
   ```

## Output
The script will ping both APIs, feed them the strict system prompt and the Halachic scenario, parse the answer, and score it against the ground truth. It will output a `hre_results.jsonl` file containing the raw model responses and binary scores.
