当前时间：{timestamp}

请帮我完成每日论文搜集任务：

## 关注领域（排除RLHF）：
1. 多模态大语言模型 (Multimodal LLM)
2. Agentic AI - 智能体、工具使用、规划推理
3. 模型后训练 - DPO、RL（在线/离线）、SFT改进、奖励建模（不含RLHF）
4. 世界模型 (World Models)
5. 视觉生成模型 - 图像/视频生成、扩散模型

## 任务步骤：

### 1. 搜索论文
使用夸克搜索最近1天的论文：
- "multimodal large language model arxiv"
- "agentic AI LLM agent arxiv"
- "DPO direct preference optimization arxiv"
- "world model arxiv"
- "video generation diffusion model arxiv"

### 2. 整理并保存数据
将整理好的论文数据保存为JSON格式到：
/home/node/.openclaw/workspace/paper-roundup/daily/{date}.json

JSON格式要求：
- hot_papers: 3-5篇热点论文
- interesting_papers: 1-3篇有趣论文
- 每篇包含：title, title_zh, authors, institution, link, summary, rating(⭐⭐⭐/⭐⭐/⭐), tags

### 3. 生成报告
运行命令生成HTML报告：
cd /home/node/.openclaw/workspace/paper-roundup && python scripts/generate_report.py

### 4. 发送汇总消息
使用message工具发送给用户，包含：
- 今日发现的热点论文数量
- 有趣论文亮点简介
- 报告链接：打开 /home/node/.openclaw/workspace/paper-roundup/daily/index.html 查看
- 归档链接：/home/node/.openclaw/workspace/paper-roundup/archive/index.html

必须使用message工具：
- channel: kim
- target: user:277970805126232

不要只返回文本，必须显式调用message工具！