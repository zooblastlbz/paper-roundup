#!/usr/bin/env python3
"""
Daily Paper Roundup - 定时任务主脚本
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/node/.openclaw/workspace/paper-roundup")
DAILY_DIR = BASE_DIR / "daily"

def run_quark_search(query, days=1, max_results=10):
    """使用夸克搜索获取论文信息"""
    try:
        skill_path = Path("/home/node/.openclaw/workspace/skills/quark-search")
        result = subprocess.run(
            ["python", "scripts/agent.py", "news", query, "--days", str(days), "--max-results", str(max_results)],
            cwd=skill_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Search error: {e}")
        return {"results": []}

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 确保目录存在
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    
    # 搜索各领域的最新论文
    search_queries = [
        ("multimodal large language model arxiv", "Multimodal LLM"),
        ("agentic AI LLM agent arxiv", "Agentic AI"),
        ("DPO direct preference optimization RL arxiv", "Post-Training"),
        ("world model arxiv", "World Model"),
        ("visual generation diffusion model arxiv", "Visual Generation"),
    ]
    
    all_results = []
    for query, category in search_queries:
        print(f"Searching: {query}")
        results = run_quark_search(query, days=1, max_results=5)
        for r in results.get("results", []):
            r["category"] = category
        all_results.extend(results.get("results", []))
    
    # 简化的数据结构（实际应由agent整理）
    papers_data = {
        "date": today,
        "hot_papers": [],
        "interesting_papers": []
    }
    
    # 保存原始搜索结果
    json_path = DAILY_DIR / f"{today}_raw.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Raw data saved: {json_path}")
    print(f"📊 Found {len(all_results)} papers")

def auto_push():
    """自动推送更改到 GitHub"""
    try:
        os.chdir(BASE_DIR)
        
        # 检查是否有更改
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("📦 没有需要推送的更改")
            return
        
        # 添加所有更改
        subprocess.run(["git", "add", "-A"], check=True)
        
        # 提交
        today = datetime.now().strftime("%Y-%m-%d")
        subprocess.run(
            ["git", "commit", "-m", f"Daily update: {today}"],
            check=True
        )
        
        # 推送
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"🚀 已自动推送到 GitHub: {today}")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git push 失败: {e}")
    except Exception as e:
        print(f"⚠️ Auto push error: {e}")

if __name__ == "__main__":
    main()
    auto_push()
