import json
import re

md_path = '../data/raw_registry.md'
json_path = '../data/registry.json'

with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

projects = []
in_table = False

for line in lines:
    line = line.strip()
    # Check if we are in the main table
    if line.startswith('| # | Project | Category'):
        in_table = True
        continue
    if in_table and line.startswith('| ---'):
        continue
    
    if in_table and line.startswith('|'):
        cols = [col.strip() for col in line.split('|')[1:-1]]
        if len(cols) >= 9 and cols[0].isdigit():
            project = {
                'id': int(cols[0]),
                'name': cols[1],
                'category': cols[2],
                'maturity': cols[3],
                'link': cols[4],
                'description': cols[5],
                'core_feature': cols[6],
                'differentiator': cols[7],
                'variation_ideas': cols[8]
            }
            projects.append(project)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(projects, f, indent=2, ensure_ascii=False)

print(f"Successfully parsed {len(projects)} projects into JSON.")
