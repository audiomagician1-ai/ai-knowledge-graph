import sqlite3, os, glob
candidates = glob.glob("**/knowledge_base.db", recursive=True) + glob.glob("**/*.db", recursive=True)
print("DB files found:", candidates[:5])
for db in candidates[:3]:
    try:
        conn = sqlite3.connect(db)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if "knowledge_entries" in tables:
            total = conn.execute("SELECT COUNT(*) FROM knowledge_entries").fetchone()[0]
            tier_s = conn.execute("SELECT COUNT(*) FROM knowledge_entries WHERE quality_tier='S'").fetchone()[0]
            tier_a = conn.execute("SELECT COUNT(*) FROM knowledge_entries WHERE quality_tier='A'").fetchone()[0]
            tier_b = conn.execute("SELECT COUNT(*) FROM knowledge_entries WHERE quality_tier='B'").fetchone()[0]
            tier_c = conn.execute("SELECT COUNT(*) FROM knowledge_entries WHERE quality_tier='C'").fetchone()[0]
            print(f"{db}: Total={total} S={tier_s} A={tier_a} B={tier_b} C={tier_c} B+above={(tier_s+tier_a+tier_b)*100//max(total,1)}%")
        conn.close()
    except Exception as e:
        print(f"{db}: Error {e}")