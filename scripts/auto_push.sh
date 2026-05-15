#!/bin/bash
# 每日论文搜集与自动推送任务

cd /home/node/.openclaw/workspace/paper-roundup

# 1. 运行每日任务（搜集论文并推送）
python scripts/daily_task.py

# 2. 生成报告
python scripts/generate_report.py

# 3. 确保所有更改都被提交并推送
git add -A
git commit -m "Daily update: $(date +%Y-%m-%d)" || true
git push origin main

echo "✅ Daily paper roundup completed and pushed at $(date)"
