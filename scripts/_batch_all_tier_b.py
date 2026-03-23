#!/usr/bin/env python3
"""
Serial batch rewrite for all Tier-B documents across all domains.
Processes domains one at a time to avoid API rate limiting.
"""
import subprocess, sys, time
from pathlib import Path

SCRIPT = str(Path(__file__).parent / "_batch_intranet_rewrite.py")

# Domains ordered by average score (worst first)
DOMAINS = [
    "game-design", "mathematics", "level-design", "biology", "english",
    "writing", "finance", "physics", "concept-design", "philosophy",
    "game-engine", "psychology", "animation", "economics", "product-design",
    "3d-art", "computer-graphics", "technical-art", "vfx", "ai-engineering",
    "multiplayer-network", "software-engineering", "game-audio-sfx", "game-qa",
    "narrative-design", "game-publishing", "game-production", "game-live-ops",
    "game-ui-ux", "game-audio-music",
]

for domain in DOMAINS:
    print(f"\n{'='*60}")
    print(f"Processing domain: {domain}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, SCRIPT, "--domain", domain, "--tier", "B", "--max", "300"],
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"WARNING: {domain} exited with code {result.returncode}")
    time.sleep(2)

print("\n\nALL DOMAINS COMPLETE!")
