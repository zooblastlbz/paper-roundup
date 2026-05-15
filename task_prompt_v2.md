当前时间：{timestamp}

请帮我完成每日论文搜集任务（arXiv官方源 + 热点追踪）：

## 关注领域（排除RLHF）：
1. 多模态大语言模型 (Multimodal LLM) - arXiv cs.CL, cs.CV, cs.MM
2. Agentic AI - 智能体、工具使用、规划推理 - arXiv cs.AI, cs.CL
3. 模型后训练 - DPO、RL（在线/离线）、SFT改进、奖励建模 - arXiv cs.LG, cs.CL
4. 世界模型 (World Models) - arXiv cs.LG, cs.AI
5. 视觉生成模型 - 图像/视频生成、扩散模型 - arXiv cs.CV, cs.GR

## 任务步骤：

### 1. arXiv API 搜索昨日新论文
使用 arXiv API 查询最近24小时提交的论文：

**API端点：** `http://export.arxiv.org/api/query?`

**搜索分类（cat:）：**
- cs.CL (Computation and Language)
- cs.CV (Computer Vision)
- cs.LG (Machine Learning)
- cs.AI (Artificial Intelligence)
- cs.MM (Multimedia)
- cs.GR (Graphics)

**查询参数示例：**
```
search_query=cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.LG+OR+cat:cs.AI
&sortBy=submittedDate&sortOrder=descending
&max_results=50
```

**筛选条件（注意排除RLHF相关）：**
- 标题/摘要不包含：RLHF, RL-HF, Human Feedback, Preference Learning（除非是DPO相关）
- 关注关键词：multimodal, agent, tool use, reasoning, DPO, SFT, world model, diffusion, video generation

### 2. Hugging Face Papers 热点追踪
访问 https://huggingface.co/papers 获取今日热门论文（基于社区讨论热度）：
- 使用 browser 工具访问页面
- 提取热榜上的论文标题和arXiv链接
- 筛选符合关注领域的论文

### 3. 数据整理与去重
合并两个来源的论文，去重后整理为：

**hot_papers** (3-5篇): 
- 来自Hugging Face热榜 + 高相关性arXiv论文
- 优先选择：有代码、高引用潜力、知名机构

**interesting_papers** (1-3篇):
- 独特视角、跨领域、或方法新颖

### 4. 保存数据
保存为JSON格式到：
`/home/node/.openclaw/workspace/paper-roundup/daily/{date}.json`

JSON格式：
```json
{
  "date": "2026-05-14",
  "sources": ["arxiv-api", "huggingface-papers"],
  "hot_papers": [...],
  "interesting_papers": [...],
  "stats": {
    "arxiv_total": 50,
    "huggingface_hot": 10,
    "filtered": 15
  }
}
```

每篇论文包含：
- title, title_zh（中文标题）
- authors, institution（第一作者机构）
- arxiv_id, link
- summary, summary_zh（中文摘要）
- rating: ⭐⭐⭐/⭐⭐/⭐
- tags: [领域标签]
- source: "arxiv" | "huggingface" | "both"
- heat?: "trending"（如果是热榜论文）

### 5. 生成报告
运行命令生成HTML报告：
```bash
cd /home/node/.openclaw/workspace/paper-roundup && python scripts/generate_report.py
```

### 6. 发送汇总消息
使用message工具发送给用户：
- 今日arXiv新论文总数（筛选后的相关数）
- Hugging Face热榜命中数
- hot_papers亮点（2-3句话/篇）
- 特别标注热榜论文 🔥
- 报告链接

必须使用message工具：
- channel: kim
- target: user:277970805126232

不要只返回文本，必须显式调用message工具！
