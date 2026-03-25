"""Fix the 2 timeout errors from Batch P2."""
import sys, re, os
sys.path.insert(0, os.path.dirname(__file__))
import _batch_tier_b_upgrade as mod

concept_map = mod.load_seed_data()
targets = ['mn-lb-ready-check', 'anim-force-motion']

for slug in targets:
    if slug not in concept_map:
        print(f'{slug}: NOT FOUND in concept map, skipping')
        continue
    concept = concept_map[slug]
    rag_file = mod.find_rag_file(slug, concept['domain'])
    if not rag_file:
        print(f'{slug}: RAG file not found')
        continue

    print(f'Rewriting {slug} ({concept["name"]})...', end='', flush=True)
    user_prompt = mod.build_user_prompt(concept)
    new_content = mod.call_llm(mod.SYSTEM_PROMPT, user_prompt)

    old = open(rag_file, 'r', encoding='utf-8').read()
    fm_match = re.match(r'^(---\s*\n.*?\n---\s*\n)', old, re.DOTALL)
    if fm_match:
        combined = fm_match.group(1) + '\n' + new_content
        combined = mod.update_frontmatter(combined)
    else:
        combined = new_content

    with open(rag_file, 'w', encoding='utf-8') as f:
        f.write(combined)
    print(f' OK ({len(new_content)} chars)')

print('Done fixing 2 errors.')
