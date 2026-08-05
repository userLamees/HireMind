"""Measure whether the live grader ranks answers the way the dataset says it should.

synthetic_data_ollama.json holds 100 questions with three answers each, written to
be excellent (9), average (6), and poor (2). Those labels give us a known ordering
per question, so the grader can be checked against it: for every pair of answers to
the same question, does the grader score the better-labelled one higher?

That is the honest answer to "how do you know the score is correct?" — not proof of
absolute accuracy, but a measured check that the grader ranks quality correctly.

Run a small sample first; a full run is 300 model calls.

    python evaluate_grader.py --limit 10     # ~30 calls, a few minutes
    python evaluate_grader.py                # all 300

Reads the same MODEL_PROVIDER / OLLAMA_* / LLM_* environment variables the API uses.
"""
import argparse
import json
import os
import statistics
import sys
from time import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))
import analyzer  # noqa: E402

DATA = 'synthetic_data_ollama.json'
OUT = 'grader_evaluation.json'

TIERS = {9: 'excellent', 6: 'average', 2: 'poor'}


def evaluate(items):
    """Grade every scenario, keeping the label it was generated under."""
    graded = []
    total = sum(len(item['scenarios']) for item in items)
    done = 0
    started = time()

    for item in items:
        for scenario in item['scenarios']:
            done += 1
            label = scenario['score']
            print(f'  [{done}/{total}] {TIERS[label]:<9} {item["question"][:44]}…',
                  end=' ', flush=True)

            result = analyzer.analyze(
                item['question'],
                item['ideal_answer'],
                scenario['candidate_answer'],
                item['difficulty'],
            )

            graded.append({
                'question': item['question'],
                'category': item['category'],
                'difficulty': item['difficulty'],
                'expected_tier': label,
                'given_score': result['score'],
                'analysis_mode': result['analysis_mode'],
            })
            print(f'→ {result["score"]}'
                  f'{"" if result["analysis_mode"] == "model" else "  (FALLBACK)"}')

    return graded, time() - started


def report(graded):
    """Per-tier scores, and how often the grader got the ordering right."""
    heuristic = [g for g in graded if g['analysis_mode'] != 'model']
    if heuristic:
        print(f'\n⚠️  {len(heuristic)}/{len(graded)} answers fell back to the '
              f'heuristic — the model was unavailable for those. Fix that before '
              f'trusting these numbers.\n')

    by_tier = {}
    for g in graded:
        by_tier.setdefault(g['expected_tier'], []).append(g['given_score'])

    print('Score the grader gave, by the tier the answer was written as')
    print(f'{"tier":<12}{"n":<6}{"mean":<8}{"median":<8}{"min":<6}{"max"}')
    for tier in sorted(by_tier, reverse=True):
        s = by_tier[tier]
        print(f'{TIERS[tier]:<12}{len(s):<6}{statistics.mean(s):<8.1f}'
              f'{statistics.median(s):<8.0f}{min(s):<6}{max(s)}')

    # Group by question so pairs are compared within the same question only.
    per_question = {}
    for g in graded:
        per_question.setdefault(g['question'], []).append(g)

    concordant = discordant = tied = 0
    perfect_triples = complete_triples = 0

    for scenarios in per_question.values():
        for i in range(len(scenarios)):
            for j in range(i + 1, len(scenarios)):
                a, b = scenarios[i], scenarios[j]
                if a['expected_tier'] == b['expected_tier']:
                    continue
                better, worse = (a, b) if a['expected_tier'] > b['expected_tier'] else (b, a)
                if better['given_score'] > worse['given_score']:
                    concordant += 1
                elif better['given_score'] < worse['given_score']:
                    discordant += 1
                else:
                    tied += 1

        if len(scenarios) == 3:
            complete_triples += 1
            ordered = sorted(scenarios, key=lambda s: -s['expected_tier'])
            if ordered[0]['given_score'] > ordered[1]['given_score'] > ordered[2]['given_score']:
                perfect_triples += 1

    pairs = concordant + discordant + tied
    print(f'\nPairwise ordering  ({pairs} comparisons within questions)')
    print(f'  correct   {concordant:>4}  ({concordant / pairs:.1%})')
    print(f'  wrong     {discordant:>4}  ({discordant / pairs:.1%})')
    print(f'  tied      {tied:>4}  ({tied / pairs:.1%})')

    if complete_triples:
        print(f'\nFull ordering (excellent > average > poor, all three correct)')
        print(f'  {perfect_triples}/{complete_triples} questions '
              f'({perfect_triples / complete_triples:.1%})')

    return {
        'graded': len(graded),
        'fell_back_to_heuristic': len(heuristic),
        'mean_by_tier': {TIERS[t]: round(statistics.mean(s), 1) for t, s in by_tier.items()},
        'pairwise': {
            'comparisons': pairs,
            'correct': concordant,
            'wrong': discordant,
            'tied': tied,
            'accuracy': round(concordant / pairs, 4) if pairs else None,
        },
        'full_ordering': {
            'questions': complete_triples,
            'correct': perfect_triples,
            'accuracy': round(perfect_triples / complete_triples, 4) if complete_triples else None,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int,
                        help='grade only the first N questions (3 calls each)')
    args = parser.parse_args()

    with open(DATA, encoding='utf-8') as f:
        items = json.load(f)
    if args.limit:
        items = items[:args.limit]

    calls = sum(len(i['scenarios']) for i in items)
    print(f'Grading {len(items)} questions — {calls} model calls')
    print(f'Provider: {analyzer.MODEL_PROVIDER} · model: {analyzer.active_model()}')
    if not analyzer.model_available():
        print('\n⚠️  The model backend is unreachable. Every answer will fall back '
              'to the word-count heuristic and the results will be meaningless.\n')
    print()

    graded, elapsed = evaluate(items)

    print(f'\nDone in {elapsed / 60:.1f} minutes\n')
    summary = report(graded)

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'graded': graded}, f, ensure_ascii=False, indent=2)
    print(f'\nSaved to {OUT}')


if __name__ == '__main__':
    main()
