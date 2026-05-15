#!/usr/bin/env python3
"""
Generate daily paper roundup report from JSON data.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def generate_report(date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    data_file = Path(f"/home/node/.openclaw/workspace/paper-roundup/daily/{date_str}.json")
    
    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        return None
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    report_lines = []
    report_lines.append(f"# 📚 每日论文汇总 ({date_str})")
    report_lines.append("")
    report_lines.append("## 📊 数据来源统计")
    report_lines.append("")
    report_lines.append(f"- **arXiv**: {data['sources']['arxiv']['status']} - {data['sources']['arxiv'].get('note', '')}")
    report_lines.append(f"- **Hugging Face Papers**: {data['sources']['huggingface']['status']} - {data['sources']['huggingface'].get('note', '')}")
    report_lines.append(f"- **Papers With Code**: {data['sources']['paperswithcode']['status']} - {data['sources']['paperswithcode'].get('note', '')}")
    report_lines.append("")
    report_lines.append(f"**搜索方式**: {data['stats'].get('search_method', 'N/A')}")
    report_lines.append("")
    
    # Categories
    report_lines.append("### 领域分布")
    report_lines.append("")
    for cat, count in data['stats'].get('categories', {}).items():
        report_lines.append(f"- {cat}: {count}篇")
    report_lines.append("")
    
    # Hot Papers
    report_lines.append("---")
    report_lines.append("")
    report_lines.append(f"## 🔥 Hot Papers ({len(data['hot_papers'])}篇)")
    report_lines.append("")
    
    for i, paper in enumerate(data['hot_papers'], 1):
        heat_marker = "🔥" if paper.get('heat') == 'trending' else ""
        report_lines.append(f"### {i}. {paper['title']} {heat_marker}")
        report_lines.append("")
        report_lines.append(f"**arXiv ID**: {paper.get('arxiv_id', 'N/A')}")
        report_lines.append(f"**作者**: {paper.get('authors', 'N/A')}")
        report_lines.append(f"**发表**: {paper.get('venue', 'N/A')}")
        report_lines.append(f"**分类**: {paper.get('category', 'N/A')}")
        if paper.get('url'):
            report_lines.append(f"**链接**: {paper['url']}")
        report_lines.append("")
        report_lines.append(f"**摘要**: {paper.get('summary', 'N/A')}")
        report_lines.append("")
        if paper.get('keywords'):
            report_lines.append(f"**关键词**: {', '.join(paper['keywords'])}")
        report_lines.append("")
    
    # Interesting Papers
    report_lines.append("---")
    report_lines.append("")
    report_lines.append(f"## 💡 Interesting Papers ({len(data['interesting_papers'])}篇)")
    report_lines.append("")
    
    for i, paper in enumerate(data['interesting_papers'], 1):
        report_lines.append(f"### {i}. {paper['title']}")
        report_lines.append("")
        report_lines.append(f"**arXiv ID**: {paper.get('arxiv_id', 'N/A')}")
        report_lines.append(f"**作者**: {paper.get('authors', 'N/A')}")
        report_lines.append(f"**发表**: {paper.get('venue', 'N/A')}")
        report_lines.append(f"**分类**: {paper.get('category', 'N/A')}")
        if paper.get('url'):
            report_lines.append(f"**链接**: {paper['url']}")
        report_lines.append("")
        report_lines.append(f"**摘要**: {paper.get('summary', 'N/A')}")
        report_lines.append("")
    
    report_text = '\n'.join(report_lines)
    
    # Save report
    report_file = Path(f"/home/node/.openclaw/workspace/paper-roundup/daily/{date_str}_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"Report saved to: {report_file}")
    return report_text

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    report = generate_report(date_arg)
    if report:
        print("\n" + "="*60)
        print(report)
