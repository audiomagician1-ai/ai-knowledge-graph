"""Find bottom-scoring RAG docs for targeted rewrite sprint."""
import os, re, json

RAG_ROOT = os.path.join(os.path.dirname(__file__), '..', 'data', 'rag')

def score_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    length = len(content)
    lines = content.split('\n')
    s = 0
    
    # Length (0-25)
    if length >= 4000: s += 25
    elif length >= 3000: s += 20
    elif length >= 2000: s += 15
    elif length >= 1000: s += 10
    elif length >= 500: s += 5
    
    # Structure (0-25)
    h2 = len([l for l in lines if l.startswith('## ')])
    h3 = len([l for l in lines if l.startswith('### ')])
    bullets = len([l for l in lines if l.strip().startswith('- ')])
    if h2 >= 3: s += 10
    elif h2 >= 2: s += 7
    elif h2 >= 1: s += 4
    if h3 >= 2: s += 5
    elif h3 >= 1: s += 3
    if bullets >= 5: s += 5
    elif bullets >= 3: s += 3
    code_blocks = content.count('```')
    if code_blocks >= 2: s += 5
    elif code_blocks >= 1: s += 3
    
    # Depth (0-25)
    has_math = bool(re.search(r'\$.*?\$', content))
    has_citation = bool(re.search(r'\(.*?\d{4}.*?\)', content))
    has_example = bool(re.search(r'(例|example|e\.g\.|案例|比如)', content, re.I))
    has_compare = bool(re.search(r'(vs|对比|比较|区别|不同)', content, re.I))
    if has_math: s += 8
    if has_citation: s += 7
    if has_example: s += 5
    if has_compare: s += 5
    
    # Quality (0-25)
    para_lengths = [len(p) for p in re.split(r'\n\n', content) if len(p.strip()) > 0]
    if para_lengths:
        avg_para = sum(para_lengths) / len(para_lengths)
        if avg_para >= 200: s += 10
        elif avg_para >= 100: s += 7
        elif avg_para >= 50: s += 4
    
    unique_words = len(set(re.findall(r'[a-zA-Z\u4e00-\u9fff]+', content)))
    if unique_words >= 300: s += 8
    elif unique_words >= 200: s += 6
    elif unique_words >= 100: s += 4
    
    filler = len(re.findall(r'(basically|simply|just|很简单|其实就是)', content, re.I))
    if filler == 0: s += 7
    elif filler <= 2: s += 4
    
    return min(100, s)

def main():
    scores = []
    for domain in sorted(os.listdir(RAG_ROOT)):
        domain_path = os.path.join(RAG_ROOT, domain)
        if not os.path.isdir(domain_path):
            continue
        for root, dirs, files in os.walk(domain_path):
            for f in files:
                if f.endswith('.md'):
                    fp = os.path.join(root, f)
                    try:
                        sc = score_file(fp)
                        rel = os.path.relpath(fp, RAG_ROOT).replace('\\', '/')
                        scores.append((sc, rel))
                    except:
                        pass
    
    scores.sort()
    total = len(scores)
    avg = sum(s for s, _ in scores) / total
    
    print(f"Total docs: {total}")
    print(f"Average: {avg:.2f}")
    print(f"S (>=80): {sum(1 for s,_ in scores if s >= 80)}")
    print(f"A (60-79): {sum(1 for s,_ in scores if 60 <= s < 80)}")
    print(f"B (40-59): {sum(1 for s,_ in scores if 40 <= s < 60)}")
    print(f"C (<40): {sum(1 for s,_ in scores if s < 40)}")
    
    # Calculate gap to 80.0
    current_total = sum(s for s, _ in scores)
    target_total = total * 80.0
    gap = target_total - current_total
    print(f"\nCurrent total score: {current_total:.0f}")
    print(f"Target total (avg 80): {target_total:.0f}")
    print(f"Gap: {gap:.0f} points")
    
    # Bottom 80
    print(f"\nBottom 80 docs:")
    bottom = scores[:80]
    for sc, path in bottom:
        print(f"  {sc:5.1f}  {path}")
    
    # Save bottom list for rewrite script
    bottom_list = [{"score": sc, "path": path} for sc, path in bottom]
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bottom_80_for_rewrite.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(bottom_list, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {out_path}")

if __name__ == '__main__':
    main()
