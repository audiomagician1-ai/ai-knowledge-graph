"""Phase 6 A-1: Expand LLM Core + Agent Systems + RAG Knowledge subdomains."""
import json, sys, os

SEED = os.path.join(os.path.dirname(__file__), '..', 'data', 'seed', 'programming', 'seed_graph.json')

d = json.load(open(SEED, encoding='utf-8'))
existing_ids = set(c['id'] for c in d['concepts'])
print(f"Before: {len(d['concepts'])} concepts, {len(d['edges'])} edges")

ts = '2026-03-19T00:00:00.000000+00:00'
DE = 'ai-engineering'

new_concepts = []

# LLM Core +10
for item in [
    ('speculative-decoding', 'Speculative Decoding', 'llm-core', 8, 35, 'theory', ['LLM'], False),
    ('kv-cache', 'KV Cache', 'llm-core', 7, 30, 'theory', ['LLM'], False),
    ('rope-embedding', 'RoPE', 'llm-core', 8, 35, 'theory', ['LLM','Transformer'], False),
    ('flash-attention', 'FlashAttention', 'llm-core', 8, 40, 'theory', ['LLM'], False),
    ('llm-distillation', 'LLM Distillation', 'llm-core', 7, 30, 'theory', ['LLM'], False),
    ('llm-safety-alignment', 'LLM Safety', 'llm-core', 7, 35, 'theory', ['LLM'], False),
    ('embedding-models', 'Embedding Models', 'llm-core', 6, 30, 'theory', ['LLM','NLP'], False),
    ('function-calling', 'Function Calling', 'llm-core', 6, 30, 'practice', ['LLM'], False),
    ('llm-benchmarks', 'LLM Benchmarks', 'llm-core', 6, 25, 'theory', ['LLM'], False),
    ('llm-serving', 'LLM Serving', 'llm-core', 7, 35, 'practice', ['LLM'], False),
]:
    new_concepts.append({
        'id': item[0], 'name': item[1],
        'description': f'Master {item[1]}',
        'domain_id': DE, 'subdomain_id': item[2],
        'difficulty': item[3], 'estimated_minutes': item[4],
        'content_type': item[5], 'tags': item[6],
        'is_milestone': item[7], 'created_at': ts,
    })

# Agent Systems +2
for item in [
    ('agent-frameworks-comparison', 'Agent Frameworks Comparison', 'agent-systems', 6, 30, 'theory', ['Agent'], False),
    ('agent-debugging', 'Agent Debugging', 'agent-systems', 6, 25, 'practice', ['Agent'], False),
]:
    new_concepts.append({
        'id': item[0], 'name': item[1],
        'description': f'Master {item[1]}',
        'domain_id': DE, 'subdomain_id': item[2],
        'difficulty': item[3], 'estimated_minutes': item[4],
        'content_type': item[5], 'tags': item[6],
        'is_milestone': item[7], 'created_at': ts,
    })

# RAG Knowledge +3
for item in [
    ('graph-rag', 'Graph RAG', 'rag-knowledge', 7, 35, 'theory', ['RAG'], False),
    ('hyde-retrieval', 'HyDE Retrieval', 'rag-knowledge', 6, 25, 'theory', ['RAG'], False),
    ('reranking', 'Reranking', 'rag-knowledge', 6, 25, 'theory', ['RAG'], False),
]:
    new_concepts.append({
        'id': item[0], 'name': item[1],
        'description': f'Master {item[1]}',
        'domain_id': DE, 'subdomain_id': item[2],
        'difficulty': item[3], 'estimated_minutes': item[4],
        'content_type': item[5], 'tags': item[6],
        'is_milestone': item[7], 'created_at': ts,
    })

# Check duplicates
for c in new_concepts:
    if c['id'] in existing_ids:
        print(f"DUPLICATE: {c['id']}")
        sys.exit(1)

d['concepts'].extend(new_concepts)

# New edges
def E(src, tgt, rel='prerequisite', s=0.7):
    return {'source_id': src, 'target_id': tgt, 'relation_type': rel, 'strength': s}

new_edges = [
    # LLM Core
    E('llm-inference','speculative-decoding'),
    E('transformer-architecture','speculative-decoding'),
    E('self-attention','kv-cache'),
    E('llm-inference','kv-cache'),
    E('positional-encoding','rope-embedding'),
    E('self-attention','flash-attention'),
    E('llm-pretraining','llm-distillation'),
    E('fine-tuning-overview','llm-distillation'),
    E('rlhf','llm-safety-alignment'),
    E('dpo','llm-safety-alignment'),
    E('tokenization','embedding-models'),
    E('text-embedding','embedding-models','related',0.6),
    E('gpt-model','function-calling'),
    E('structured-output','function-calling'),
    E('tool-use','function-calling','related',0.8),
    E('llm-evaluation','llm-benchmarks'),
    E('llm-inference','llm-serving'),
    E('quantization','llm-serving'),
    E('kv-cache','llm-serving','related',0.6),
    E('flash-attention','llm-serving','related',0.6),
    E('speculative-decoding','llm-serving','related',0.6),
    # Agent Systems
    E('autogen-framework','agent-frameworks-comparison'),
    E('crewai-framework','agent-frameworks-comparison'),
    E('agent-loop','agent-debugging'),
    E('agent-evaluation','agent-debugging','related',0.6),
    # RAG Knowledge
    E('knowledge-graph-rag','graph-rag'),
    E('rag-pipeline','graph-rag'),
    E('text-embedding','hyde-retrieval'),
    E('similarity-search','hyde-retrieval'),
    E('similarity-search','reranking'),
    E('rag-pipeline','reranking'),
    E('hyde-retrieval','rag-evaluation','related',0.6),
    E('reranking','rag-evaluation','related',0.6),
]

d['edges'].extend(new_edges)

# Verify all edge references exist
all_ids = set(c['id'] for c in d['concepts'])
for e in d['edges']:
    src = e.get('source_id') or e.get('source')
    tgt = e.get('target_id') or e.get('target')
    if src not in all_ids:
        print(f"ERROR: edge source '{src}' not found")
        sys.exit(1)
    if tgt not in all_ids:
        print(f"ERROR: edge target '{tgt}' not found")
        sys.exit(1)

# Update meta
from collections import Counter
sub_counts = Counter(c['subdomain_id'] for c in d['concepts'])
diff_counts = Counter(str(c['difficulty']) for c in d['concepts'])
d['meta'] = {
    'generated_at': ts,
    'total_concepts': len(d['concepts']),
    'total_edges': len(d['edges']),
    'subdomain_counts': dict(sub_counts),
    'difficulty_distribution': dict(diff_counts),
}

# Save
with open(SEED, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f"After: {len(d['concepts'])} concepts, {len(d['edges'])} edges")
print(f"Added: {len(new_concepts)} concepts, {len(new_edges)} edges")
print("OK")