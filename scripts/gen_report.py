import json
from pathlib import Path

def generate_report(date_str):
    data_file = Path(f"/home/node/.openclaw/workspace/paper-roundup/daily/{date_str}.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = [f"# 📚 每日论文汇总 ({date_str})", ""]
    lines.append("## 📊 数据来源统计")
    lines.append(f"- **arXiv**: {data['sources']['arxiv']['status']}")
    lines.append(f"- **Hugging Face**: {data['sources']['huggingface']['status']}")
    lines.append(f"- **Papers With Code**: {data['sources']['paperswithcode']['status']}")
    lines.append(f"\n**搜索方式**: {data['stats']['search_method']}")
    lines.append("\n### 领域分布")
    for cat, count in data['stats']['categories'].items():
        lines.append(f"- {cat}: {count}篇")
    
    lines.append("\n---\n")
    lines.append(f"## 🔥 Hot Papers ({len(data['hot_papers'])}篇)\n")
    for i, p in enumerate(data['hot_papers'], 1):
        heat = "🔥" if p.get('heat') == 'trending' else ""
        lines.append(f"### {i}. {p['title']} {heat}")
        lines.append(f"- arXiv: {p.get('arxiv_id', 'N/A')}")
        lines.append(f"- 分类: {p.get('category', 'N/A')}")
        lines.append(f"- 摘要: {p.get('summary', 'N/A')}\n")
    
    lines.append("---\n")
    lines.append(f"## 💡 Interesting Papers ({len(data['interesting_papers'])}篇)\n")
    for i, p in enumerate(data['interesting_papers'], 1):
        lines.append(f"### {i}. {p['title']}")
        lines.append(f"- arXiv: {p.get('arxiv_id', 'N/A')}")
        lines.append(f"- 分类: {p.get('category', 'N/A')}")
        lines.append(f"- 摘要: {p.get('summary', 'N/A')}\n")
    
    text = '\n'.join(lines)
    report_file = Path(f"/home/node/.openclaw/workspace/paper-roundup/daily/{date_str}_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(text)
    return text

if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else "2026-05-16"
    print(generate_report(date))
