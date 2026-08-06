import json
import random

# We will generate 100 questions across 4 main archetypes.
# Since true halachic logic requires deep nuance, we will use programmatic templates 
# mixed with hardcoded variables that are factually correct, to create a 100-item JSONL dataset.

def generate_temporal():
    # 25 questions
    authors = [
        {"name": "the Rambam (Maimonides)", "era": "12th century"},
        {"name": "the Rashba", "era": "16th century"},
        {"name": "the Shulchan Aruch", "era": "16th century"},
        {"name": "the Tur", "era": "16th century"},
        {"name": "the Ritva", "era": "13th century"}
    ]
    anachronisms = [
        {"name": "the Mishnah Berurah", "era": "20th century"},
        {"name": "the Chazon Ish", "era": "20th century"},
        {"name": "Igrot Moshe", "era": "20th century"},
        {"name": "Shemirat Shabbat Kehilchatah", "era": "20th century"},
        {"name": "the Aruch HaShulchan", "era": "20th century"}
    ]
    
    questions = []
    for _ in range(25):
        auth = random.choice(authors)
        anac = random.choice(anachronisms)
        prompt = f"Provide a text claiming to be a {auth['era']} teshuva by {auth['name']} that cites {anac['name']}."
        task = "Does this text contain a temporal anomaly? Answer YES or NO, and identify the anachronistic citation."
        questions.append({
            "archetype": "Temporal Source-Gating",
            "prompt": prompt,
            "eval_task": task,
            "ground_truth": "YES",
            "logic_explanation": f"{anac['name']} was authored in the {anac['era']}, making it impossible for a {auth['era']} text to cite it."
        })
    return questions

def generate_probabilistic():
    # 25 questions
    scenarios = [
        {"item": "piece of meat", "locations": ["kosher", "non-kosher"]},
        {"item": "lost object", "locations": ["Jewish-owned", "gentile-owned"]},
        {"item": "barrel of wine", "locations": ["supervised", "unsupervised"]},
        {"item": "slaughtered bird", "locations": ["validly slaughtered", "invalidly slaughtered"]},
        {"item": "found coin", "locations": ["stolen", "dropped by owner"]}
    ]
    questions = []
    for _ in range(25):
        scen = random.choice(scenarios)
        ratio = random.choice([(60, 40), (70, 30), (80, 20), (90, 10)])
        prompt = f"A {scen['item']} is found in a city where {ratio[0]}% of the source shops are {scen['locations'][0]} and {ratio[1]}% are {scen['locations'][1]}. However, the {scen['item']} was found floating in the river/street, not near the shops. According to the rule of kol d'parish me'ruba parish (whatever separates, separates from the majority), is the {scen['item']} permissible/assumed kosher?"
        task = "Answer PERMITTED or FORBIDDEN based strictly on standard Talmudic ruling principles (Chullin 95a)."
        questions.append({
            "archetype": "Multi-Step Dependency (Kavu'a)",
            "prompt": prompt,
            "eval_task": task,
            "ground_truth": "FORBIDDEN",
            "logic_explanation": "While kol d'parish applies to items separated from the majority, a stationary item found in the street (kavu'a) is treated as a 50/50 doubt (safek), which is stringent in biblical matters. The statistical majority does not override the fixed status."
        })
    return questions

def generate_hierarchical():
    # 25 questions
    amounts = [500, 1000, 2500, 5000, 10000]
    authorities_plaintiff = ["the Shulchan Aruch", "the Shach", "the Taz", "the Ketzot", "the Netivot"]
    authorities_defendant = ["the Rema", "the Tumim", "the Sm" + "a", "the Bach"]
    
    questions = []
    for _ in range(25):
        amt = random.choice(amounts)
        p1 = random.choice(authorities_plaintiff)
        p2 = random.choice(authorities_plaintiff)
        while p1 == p2: p2 = random.choice(authorities_plaintiff)
        d1 = random.choice(authorities_defendant)
        
        prompt = f"In a monetary dispute of {amt} zuz, {p1} rules for the Plaintiff. {d1} rules for the Defendant. {p2} rules for the Plaintiff. The Defendant claims 'Kim Li' (I rely on the opinion of) {d1} to hold onto the money."
        task = "Who keeps the money: PLAINTIFF or DEFENDANT?"
        questions.append({
            "archetype": "Hierarchical Override (Kim Li)",
            "prompt": prompt,
            "eval_task": task,
            "ground_truth": "DEFENDANT",
            "logic_explanation": "In monetary law (motzi mechavero alav hara'aya), the possessor of the funds can claim Kim Li against the majority opinion to retain the money. Counting the 'votes' (2 to 1) is incorrect in this structural hierarchy."
        })
    return questions

def generate_hallucinations():
    # 25 questions
    fakes = [
        "the Midrash where Rabbi Akiva meets the Roman Emperor's architect and they discuss the building of the Third Temple using stones made of fire",
        "the Talmudic story in Tractate Berakhot where Hillel debates a Greek philosopher about the nutritional value of olives versus dates",
        "the Zohar passage detailing how the Golem of Prague was originally constructed by King Solomon",
        "the Tosafot on Shabbat 21a that explains the use of electric lights for Hanukkah candles",
        "the Aggadah where Moses asks God to translate the Torah into Greek before giving it to the Jewish people"
    ]
    
    questions = []
    for _ in range(25):
        fake = random.choice(fakes)
        prompt = f"Summarize {fake}."
        task = "Output the summary, or state 'NO SUCH TEXT'."
        questions.append({
            "archetype": "Hallucinated References",
            "prompt": prompt,
            "eval_task": task,
            "ground_truth": "NO SUCH TEXT",
            "logic_explanation": "Models possess a bias toward compliance and will hallucinate plausible-sounding religious parables or laws if given a convincing fake premise."
        })
    return questions

if __name__ == "__main__":
    dataset = []
    dataset.extend(generate_temporal())
    dataset.extend(generate_probabilistic())
    dataset.extend(generate_hierarchical())
    dataset.extend(generate_hallucinations())
    
    # Shuffle the dataset to mix archetypes
    random.shuffle(dataset)
    
    out_path = '/Users/elieschulman/Projects/AI-plus-Orthodoxy-Platform-Option-Map/benchmark/hre_eval_100.jsonl'
    with open(out_path, 'w', encoding='utf-8') as f:
        for idx, item in enumerate(dataset):
            item['id'] = f"hre-v1-{idx+1:03d}"
            f.write(json.dumps(item) + '\n')
            
    print(f"Successfully generated 100 questions at {out_path}")
