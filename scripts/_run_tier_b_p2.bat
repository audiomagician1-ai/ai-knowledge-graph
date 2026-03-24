@echo off
cd /d D:\EchoAgent\projects\ai-knowledge-graph
echo Starting Parallel Batch (P2) - Large domains...
python -u scripts/_batch_tier_b_parallel.py --max 1000 --domains ai-engineering,software-engineering,computer-graphics,game-engine,game-ui-ux,multiplayer-network,game-live-ops,game-audio-music,game-audio-sfx,game-publishing,concept-design,technical-art,narrative-design,3d-art,vfx,animation,game-production,game-qa
echo Done.
pause
