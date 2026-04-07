"""Sprint 10 analysis: find exact gap to 80.0 and plan rewrite targets."""
import subprocess, re, json, sys

def main():
    result = subprocess.run(
        [sys.executable, 'scripts/quality_scorer.py', '--report-only'],
        capture_output=True, text=True, encoding='utf-8'
    )
    output = result.stdout + result.stderr

    # Parse per-domain lines
    lines = output.split('\n')
    domain_data = []
    for line in lines:
        m = re.match(r'\s+(\S+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)/(\d+)/(\d+)/(\d+)', line)
        if m:
            domain_data.append({
                'domain': m.group(1),
                'count': int(m.group(2)),
                'avg': float(m.group(3)),
                'min': float(m.group(4)),
                'max': float(m.group(5)),
                's': int(m.group(6)),
                'a': int(m.group(7)),
                'b': int(m.group(8)),
                'c': int(m.group(9)),
            })

    total_docs = sum(d['count'] for d in domain_data)
    total_score = sum(d['count'] * d['avg'] for d in domain_data)
    current_avg = total_score / total_docs
    target_avg = 80.0
    gap = total_docs * target_avg - total_score

    print(f'Total docs: {total_docs}')
    print(f'Current avg: {current_avg:.2f}')
    print(f'Target avg: {target_avg}')
    print(f'Gap: {gap:.0f} points')
    print()

    # Domains sorted by avg (worst first)
    domain_data.sort(key=lambda d: d['avg'])
    print('Worst 15 domains:')
    for d in domain_data[:15]:
        print(f'  {d["domain"]:30s}  count={d["count"]:3d}  avg={d["avg"]:.1f}  min={d["min"]:.1f}')

    # Estimate: if we rewrite the bottom 80 docs (at ~73-75) to score ~85,
    # each gains ~11 points. 80 * 11 = 880 > 630 gap
    print(f'\nStrategy: rewrite bottom 80 docs (gain ~11 pts each)')
    print(f'Expected gain: 80 * 11 = 880 points (need {gap:.0f})')
    print(f'Projected avg: {(total_score + 880) / total_docs:.2f}')

if __name__ == '__main__':
    main()
