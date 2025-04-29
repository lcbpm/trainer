# 模型家族分类整理

> 更新时间：2025-04-29

本文整理了目前主流的语言模型（LLM）按“家族”（Family）划分的分类方式。

---

## 🧬 1. OpenAI 家族

| 模型 | 类型 | 说明 |
|------|------|------|
| GPT-1 / 2 / 3 | Decoder-only | 预训练语言模型的开山鼻祖 |
| GPT-3.5 / 4 / 4 Turbo | Instruct, Chat | ChatGPT 使用的核心模型，闭源 |
| Codex | 代码生成 | GPT-3 微调版，用于编程任务（如 Copilot） |

---

## 🦙 2. LLaMA 家族（Meta）

| 模型 | 类型 | 说明 |
|------|------|------|
| LLaMA 1 | 基础预训练 | 2023 年初推出，引发开源浪潮 |
| LLaMA 2 | Chat 模型 | 适用于对话和微调，广泛被使用 |
| LLaMA 3 | 更大、更强 | 2024年发布，基础和 instruct 模型都有 |

**衍生模型**：Vicuna、Alpaca、WizardLM、Baize、OpenChat 等

---

## 🐲 3. ChatGLM 家族（清华 & 智谱）

| 模型 | 类型 | 说明 |
|------|------|------|
| ChatGLM-6B / 2 / 3 | 中英双语 | 中文能力强，推理效率高 |
| GLM-4 | 多模态大模型 | 支持图文输入，多任务能力 |

---

## 🐼 4. Qwen 家族（阿里）

| 模型 | 类型 | 说明 |
|------|------|------|
| Qwen-7B / 14B | 通用模型 | 中文能力优异 |
| Qwen-1.5 系列 | 新一代优化 | 更强的多任务表现 |
| Qwen-Audio / VL | 多模态扩展 | 图文音处理能力 |

---

## 🦅 5. Mistral 家族（法国）

| 模型 | 类型 | 说明 |
|------|------|------|
| Mistral-7B | Decoder-only | 小而强的 Transformer |
| Mixtral | MoE（多专家） | 推理速度快，效果好 |
| OpenChat-Mistral | 社区优化 | 更强的对话能力 |

---

## 🔓 6. BLOOM 家族（BigScience）

| 模型 | 类型 | 说明 |
|------|------|------|
| BLOOM | 多语言 | 支持 46+ 语言，完全开源 |
| BLOOMZ | 微调版本 | 针对多语言任务优化 |

---

## 💡 7. T5 / UL2 家族（Google）

| 模型 | 类型 | 说明 |
|------|------|------|
| T5 | 编码-解码 | Text-to-Text 框架 |
| mT5 | 多语言 | 支持百种语言 |
| UL2 | 统一训练 | 多任务、多目标混合训练策略 |

---

## 📊 8. BERT 家族（Google）

| 模型 | 类型 | 说明 |
|------|------|------|
| BERT | Encoder-only | 自监督语言理解 |
| RoBERTa | 改进版 BERT | 更强的表现 |
| DistilBERT | 蒸馏版 | 更小更快 |
| ALBERT | 参数共享 | 更高效的训练结构 |

---

## 📘 9. Claude 家族（Anthropic）

| 模型 | 类型 | 说明 |
|------|------|------|
| Claude 1 / 2 / 3 | 对话模型 | 长上下文能力、注重安全，闭源 |

---

## 📚 10. 其他代表性家族

| 家族 | 代表模型 | 说明 |
|------|----------|------|
| DeepSeek | DeepSeek-Coder / Chat | 面向中文、代码任务 |
| InternLM | InternLM2 / InternVL | 商汤出品，多模态能力 |
| Yi 系列 | Yi-6B / 34B | 01.AI 开源模型 |
| Baichuan | Baichuan 7B / 13B | 强调商用和部署能力 |
| Xverse / MiniCPM / Skywork | 小参数国产模型 | 部署灵活，适合轻量应用 |

---

## 🧩 衍生 & 混血类模型

| 模型 | 来源 | 基础 |
|------|------|------|
| Alpaca | Stanford | LLaMA 微调 |
| Vicuna | LMSYS | LLaMA + ShareGPT |
| Phoenix | Tsinghua | InternLM 中文强化 |
| OpenChat | 社区 | Mistral 微调 |

---
