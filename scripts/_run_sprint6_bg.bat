@echo off
chcp 65001 >nul 2>&1
cd /d D:\EchoAgent\projects\ai-knowledge-graph
python -u scripts/_batch_sprint6.py --max 3400 > data\tier_b_s6_stdout.log 2>&1
