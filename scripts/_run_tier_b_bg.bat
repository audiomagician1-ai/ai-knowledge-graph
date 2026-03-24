@echo off
chcp 65001 >nul 2>&1
cd /d D:\EchoAgent\projects\ai-knowledge-graph
echo Starting Tier-B batch upgrade at %date% %time%
python scripts/_batch_tier_b_upgrade.py --resume --max 500 > data\tier_b_upgrade_stdout.log 2>&1
echo Finished at %date% %time%
