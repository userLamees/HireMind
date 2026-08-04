import requests
import json
import pandas as pd
from time import time

# Load data
df = pd.read_csv('Software_Questions.csv', encoding='latin1')
df_clean = df.drop_duplicates(subset=['Question'], keep='first').copy()
df_clean['Category'] = df_clean['Category'].replace('General Program', 'General Programming')
df_clean['Category'] = df_clean['Category'].replace('Database and SQL', 'Database Systems')

print(f"✅ {len(df_clean)} سؤال محمّل")

# Ollama API
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:7b-instruct"

def call_ollama(prompt, temperature=0.7, max_tokens=256):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
            "num_predict": max_tokens
        }, timeout=60)
        
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {str(e)}"

def generate_excellent_answer(question, ideal_answer):
    prompt = f"""You are an expert technical interviewer. Generate an EXCELLENT answer (Score: 9-10).

Question: {question}

Answer:"""
    return call_ollama(prompt, temperature=0.3)

def generate_average_answer(question, ideal_answer):
    prompt = f"""You are an expert technical interviewer. Generate an AVERAGE answer (Score: 5-7).

Question: {question}

Answer:"""
    return call_ollama(prompt, temperature=0.7)

def generate_poor_answer(question, ideal_answer):
    prompt = f"""You are an expert technical interviewer. Generate a POOR answer (Score: 1-3).

Question: {question}

Answer:"""
    return call_ollama(prompt, temperature=1.2)

def generate_feedback(question, candidate_answer, score):
    prompt = f"""Professional feedback for this answer.

Question: {question}
Answer: {candidate_answer}
Score: {score}/10

Feedback:"""
    return call_ollama(prompt, temperature=0.5, max_tokens=150)

def generate_all_scenarios(question, ideal_answer):
    scenarios = []
    
    print("  → Excellent...", end=" ", flush=True)
    excellent_ans = generate_excellent_answer(question, ideal_answer)
    excellent_feedback = generate_feedback(question, excellent_ans, 9)
    scenarios.append({
        "score": 9,
        "candidate_answer": excellent_ans,
        "feedback": excellent_feedback
    })
    print("✓")
    
    print("  → Average...", end=" ", flush=True)
    average_ans = generate_average_answer(question, ideal_answer)
    average_feedback = generate_feedback(question, average_ans, 6)
    scenarios.append({
        "score": 6,
        "candidate_answer": average_ans,
        "feedback": average_feedback
    })
    print("✓")
    
    print("  → Poor...", end=" ", flush=True)
    poor_ans = generate_poor_answer(question, ideal_answer)
    poor_feedback = generate_feedback(question, poor_ans, 2)
    scenarios.append({
        "score": 2,
        "candidate_answer": poor_ans,
        "feedback": poor_feedback
    })
    print("✓")
    
    return scenarios

sample_questions = df_clean.sample(100, random_state=42)
synthetic_data = []

print("\n🚀 Starting Synthetic Data Generation for 100 questions\n")

start = time()

for idx, (i, row) in enumerate(sample_questions.iterrows(), 1):
    question = row['Question']
    ideal_answer = row['Answer']
    category = row['Category']
    difficulty = row['Difficulty']
    
    print(f"[{idx}/100] {question[:50]}...")
    
    scenarios = generate_all_scenarios(question, ideal_answer)
    
    synthetic_data.append({
        "question": question,
        "ideal_answer": ideal_answer,
        "category": category,
        "difficulty": difficulty,
        "scenarios": scenarios
    })
    print()

with open('synthetic_data_ollama.json', 'w', encoding='utf-8') as f:
    json.dump(synthetic_data, f, ensure_ascii=False, indent=2)

elapsed = time() - start

print(f"\n✅ Done!")
print(f"⏱️  Time: {elapsed/60:.1f} minutes")
print(f"✅ Data saved: synthetic_data_ollama.json")
