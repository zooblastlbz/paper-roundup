#!/usr/bin/env python3
"""
Daily Paper Roundup - 完整定时任务主脚本
功能：搜索论文 -> 数据处理 -> 生成JSON+HTML -> 推送到GitHub
"""

import json
import subprocess
import os
import re
from datetime import datetime
from pathlib import Path
from html import escape

BASE_DIR = Path("/home/node/.openclaw/workspace/paper-roundup")
DAILY_DIR = BASE_DIR / "daily"
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"

# 搜索查询配置
SEARCH_QUERIES = [
    ("multimodal large language model MLLM arxiv 2025", "Multimodal LLM"),
    ("AI agent tool use reasoning planning arxiv", "Agentic AI"),
    ("DPO RL reward model SFT training arxiv", "Post-Training"),
    ("world model AI arxiv", "World Model"),
    ("diffusion model video generation arxiv", "Visual Generation"),
]


def run_quark_search(query, days=3, max_results=8):
    """使用夸克搜索获取论文信息"""
    try:
        skill_path = Path("/home/node/.openclaw/workspace/skills/quark-search")
        result = subprocess.run(
            ["python", "scripts/agent.py", "news", query, "--days", str(days), "--max-results", str(max_results)],
            cwd=skill_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Search error for '{query}': {e}")
        return {"results": []}


def extract_arxiv_info(text):
    """从搜索结果中提取 arXiv ID 和其他信息"""
    arxiv_pattern = r'arXiv[:\s]*(\d{4}\.\d{4,5})'
    match = re.search(arxiv_pattern, text, re.IGNORECASE)
    arxiv_id = match.group(1) if match else None
    
    # 提取链接
    url_pattern = r'https?://arxiv\.org/abs/(\d{4}\.\d{4,5})'
    url_match = re.search(url_pattern, text)
    if url_match and not arxiv_id:
        arxiv_id = url_match.group(1)
    
    url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
    return arxiv_id, url


def process_paper_item(item, category):
    """处理单个搜索结果，转换为标准论文格式"""
    title = item.get("title", "").strip()
    snippet = item.get("snippet", "")
    main_text = item.get("main_text", "")
    link = item.get("link", "")
    published = item.get("published_time", "")
    
    # 提取 arXiv ID
    combined_text = f"{title} {snippet} {link}"
    arxiv_id, arxiv_url = extract_arxiv_info(combined_text)
    
    if not arxiv_id and "arxiv" in link.lower():
        # 尝试从链接提取
        arxiv_match = re.search(r'(\d{4}\.\d{4,5})', link)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
    
    # 生成摘要
    summary = snippet if snippet else main_text[:300] if main_text else "暂无摘要"
    if len(summary) > 500:
        summary = summary[:497] + "..."
    
    # 生成关键词（从标题和摘要提取）
    keywords = []
    keyword_map = {
        "Multimodal LLM": ["多模态", "视觉语言模型", "MLLM", "Vision Language"],
        "Agentic AI": ["智能体", "Agent", "工具使用", "Tool Use", "规划"],
        "Post-Training": ["DPO", "RLHF", "对齐", "偏好优化", "奖励模型"],
        "World Model": ["世界模型", "World Model", "动态模型", "想象"],
        "Visual Generation": ["扩散模型", "Diffusion", "图像生成", "视频生成"]
    }
    
    for kw in keyword_map.get(category, []):
        if kw.lower() in (title + summary).lower():
            keywords.append(kw)
    keywords = list(set(keywords))[:4]  # 最多4个，去重
    
    return {
        "title": title,
        "arxiv_id": arxiv_id,
        "url": arxiv_url or link,
        "summary": summary,
        "category": category,
        "published_time": published,
        "keywords": keywords,
        "source": "quark_search"
    }


def search_all_papers():
    """搜索所有领域的论文"""
    all_papers = []
    category_stats = {}
    
    for query, category in SEARCH_QUERIES:
        print(f"🔍 Searching: {category} ...")
        try:
            results = run_quark_search(query, days=3, max_results=8)
            papers = results.get("results", [])
            category_stats[category] = 0
            
            for item in papers:
                paper = process_paper_item(item, category)
                if paper["title"] and len(paper["title"]) > 20:  # 过滤无效结果
                    all_papers.append(paper)
                    category_stats[category] += 1
            
            print(f"   ✅ {category}: {category_stats[category]} papers")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return all_papers, category_stats


def deduplicate_papers(papers):
    """去重论文，基于 arXiv ID 或标题相似度"""
    seen_ids = set()
    seen_titles = set()
    unique_papers = []
    
    for paper in papers:
        # 用 arXiv ID 去重
        if paper.get("arxiv_id") and paper["arxiv_id"] in seen_ids:
            continue
        
        # 用标题去重（简化后比较）
        title_key = paper["title"].lower().replace(" ", "").replace("-", "")[:30]
        if title_key in seen_titles:
            continue
        
        if paper.get("arxiv_id"):
            seen_ids.add(paper["arxiv_id"])
        seen_titles.add(title_key)
        unique_papers.append(paper)
    
    return unique_papers


def categorize_papers(papers):
    """将论文分为 Hot Papers 和 Interesting Papers"""
    # 简单规则：包含 2025 或最新日期的作为 Hot
    hot_keywords = ["2025", "novel", "state", "sota", "new", "breakthrough"]
    hot_papers = []
    interesting_papers = []
    
    for paper in papers:
        title_lower = paper["title"].lower()
        is_hot = any(kw in title_lower for kw in hot_keywords) or "2025" in paper.get("published_time", "")
        
        if is_hot and len(hot_papers) < 6:
            paper["heat"] = "trending"
            hot_papers.append(paper)
        elif len(interesting_papers) < 6:
            interesting_papers.append(paper)
    
    # 如果 hot 不够，从前面补充
    while len(hot_papers) < min(4, len(papers)):
        remaining = [p for p in papers if p not in hot_papers and p not in interesting_papers]
        if not remaining:
            break
        p = remaining[0]
        p["heat"] = "trending"
        hot_papers.append(p)
    
    return hot_papers, interesting_papers


def save_data_json(today, hot_papers, interesting_papers, category_stats):
    """保存数据到 JSON 文件"""
    # 确保目录存在
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    data = {
        "date": today,
        "sources": {
            "arxiv": {"status": "using_quark_search", "note": "通过夸克搜索获取，绕过代理限制"},
            "huggingface": {"status": "using_quark_search", "note": "通过夸克搜索获取"},
            "paperswithcode": {"status": "using_quark_search", "note": "通过夸克搜索获取"}
        },
        "stats": {
            "search_method": "夸克搜索 (阿里云 IQS)",
            "categories": category_stats,
            "total_papers": len(hot_papers) + len(interesting_papers),
            "hot_count": len(hot_papers),
            "interesting_count": len(interesting_papers)
        },
        "hot_papers": hot_papers,
        "interesting_papers": interesting_papers
    }
    
    # 保存到 daily/ (原始数据)
    daily_path = DAILY_DIR / f"{today}.json"
    with open(daily_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved to daily/: {daily_path}")
    
    # 复制到 data/ (网站读取)
    data_path = DATA_DIR / f"{today}.json"
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved to data/: {data_path}")
    
    return data


def generate_html_report(today, data):
    """生成静态 HTML 报告"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    hot_papers = data.get("hot_papers", [])
    interesting_papers = data.get("interesting_papers", [])
    stats = data.get("stats", {})
    
    def render_paper_card(paper, is_hot=False):
        heat_badge = '<span class="badge hot">🔥 Hot</span>' if is_hot else ''
        category_badge = f'<span class="badge category">{escape(paper.get("category", "Other"))}</span>' if paper.get("category") else ''
        url = paper.get("url") or (f"https://arxiv.org/abs/{paper['arxiv_id']}" if paper.get("arxiv_id") else "#")
        keywords = ''.join(f'<span class="keyword">{escape(k)}</span>' for k in paper.get("keywords", []))
        
        return f'''
        <div class="paper-card {'hot' if is_hot else ''}">
            <div class="paper-header">
                <a href="{escape(url)}" target="_blank" class="paper-title">{escape(paper.get("title", "Untitled"))}</a>
                <div class="paper-badges">{heat_badge}{category_badge}</div>
            </div>
            <div class="paper-meta">{escape(paper.get("arxiv_id", "") or "")}</div>
            <div class="paper-summary">{escape(paper.get("summary", "暂无摘要"))}</div>
            {f'<div class="paper-keywords">{keywords}</div>' if keywords else ''}
        </div>
        '''
    
    hot_html = ''.join(render_paper_card(p, True) for p in hot_papers) if hot_papers else '<p class="loading">暂无论文</p>'
    interesting_html = ''.join(render_paper_card(p, False) for p in interesting_papers) if interesting_papers else '<p class="loading">暂无论文</p>'
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paper Roundup - {today}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>📚 Paper Roundup</h1>
        <p>每日 AI/ML 论文精选 - {today}</p>
    </header>

    <main>
        <section class="stats">
            <h2>📊 统计</h2>
            <div class="stat-cards">
                <div class="stat-card">
                    <span class="stat-number">{stats.get("total_papers", 0)}</span>
                    <span class="stat-label">总论文数</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{stats.get("hot_count", 0)}</span>
                    <span class="stat-label">热榜论文</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{stats.get("interesting_count", 0)}</span>
                    <span class="stat-label">精选论文</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len(stats.get("categories", {}))}</span>
                    <span class="stat-label">覆盖领域</span>
                </div>
            </div>
        </section>

        <section class="latest">
            <h2>🔥 热榜论文 ({len(hot_papers)}篇)</h2>
            <div>{hot_html}</div>
        </section>

        <section class="latest">
            <h2>💡 精选论文 ({len(interesting_papers)}篇)</h2>
            <div>{interesting_html}</div>
        </section>
    </main>

    <footer>
        <p>生成于 {today} | 数据来源: 夸克搜索 | <a href="https://github.com/zooblastlbz/paper-roundup">GitHub</a></p>
    </footer>
</body>
</html>'''
    
    # 保存每日报告
    report_path = DOCS_DIR / f"{today}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"🌐 HTML report saved: {report_path}")
    
    # 更新首页为最新报告
    index_path = DOCS_DIR / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"🏠 Homepage updated: {index_path}")


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
            return True
        
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
        print(f"🚀 已推送到 GitHub: {today}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git push 失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Auto push error: {e}")
        return False


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"📚 Paper Roundup - Daily Task ({today})")
    print(f"{'='*60}\n")
    
    # 1. 搜索论文
    print("Step 1/4: 搜索论文...")
    all_papers, category_stats = search_all_papers()
    
    if not all_papers:
        print("⚠️ 没有找到论文，任务终止")
        return False
    
    print(f"\n📊 Total papers found: {len(all_papers)}")
    
    # 2. 去重和分类
    print("\nStep 2/4: 处理数据...")
    unique_papers = deduplicate_papers(all_papers)
    hot_papers, interesting_papers = categorize_papers(unique_papers)
    print(f"   - Hot papers: {len(hot_papers)}")
    print(f"   - Interesting papers: {len(interesting_papers)}")
    
    # 3. 保存数据
    print("\nStep 3/4: 保存数据...")
    data = save_data_json(today, hot_papers, interesting_papers, category_stats)
    
    # 4. 生成 HTML
    print("\nStep 4/4: 生成 HTML 报告...")
    generate_html_report(today, data)
    
    # 5. 推送
    print("\n" + "="*60)
    print("📤 推送到 GitHub...")
    success = auto_push()
    
    print("\n" + "="*60)
    if success:
        print(f"✅ 任务完成！网站将在 1-2 分钟后更新:")
        print(f"   🌐 https://zooblastlbz.github.io/paper-roundup/")
    else:
        print("⚠️ 任务部分完成，请手动检查 Git 状态")
    print("="*60 + "\n")
    
    return success


if __name__ == "__main__":
    main()
