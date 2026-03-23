@echo off
cd /d D:\EchoAgent\projects\ai-knowledge-graph
python scripts/_batch_tier_b_upgrade.py --max 200 --resume > data\tier_b_stdout.log 2>&1
