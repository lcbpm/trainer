# 大语言模型指南

> 更新时间：2025-04-29

本文整理了目前主流的语言模型（LLM）按"家族"（Family）划分的分类方式，以及大模型的应用模式。

## 📋 目录

### 第一部分：模型家族分类整理
- [🧬 1. OpenAI 家族](#-1-openai-家族)
- [🦙 2. LLaMA 家族（Meta）](#-2-llama-家族meta)
- [🐲 3. ChatGLM 家族（清华 & 智谱）](#-3-chatglm-家族清华--智谱)
- [🐼 4. Qwen 家族（阿里）](#-4-qwen-家族阿里)
- [🦅 5. Mistral 家族（法国）](#-5-mistral-家族法国)
- [🔓 6. BLOOM 家族（BigScience）](#-6-bloom-家族bigscience)
- [💡 7. T5 / UL2 家族（Google）](#-7-t5--ul2-家族google)
- [📊 8. BERT 家族（Google）](#-8-bert-家族google)
- [📘 9. Claude 家族（Anthropic）](#-9-claude-家族anthropic)
- [📚 10. 其他代表性家族](#-10-其他代表性家族)
- [🧩 11. 衍生 & 混血类模型](#-11-衍生--混血类模型)

### 第二部分：大模型应用模式
- [🚀 12. 直接调用现有大模型（不开箱即用）](#-12-直接调用现有大模型不开箱即用)
- [⚙️ 13. 微调（Fine-tuning）现有大模型](#️-13-微调fine-tuning现有大模型)
  - [13.1 微调框架对比](#131-微调框架对比)
  - [13.2 各框架详细介绍](#132-各框架详细介绍)
  - [13.3 选择指南](#133-选择指南)
  - [13.4 实际经验建议](#134-实际经验建议)
- [💡 14. 提示工程（Prompt Engineering + 外挂知识库/参数化控制）](#-14-提示工程prompt-engineering--外挂知识库参数化控制)
  - [14.1 提示词优化技术分类](#141-提示词优化技术分类)
  - [14.2 具体优化方法详解](#142-具体优化方法详解)
  - [14.3 提示词结构优化](#143-提示词结构优化)
  - [14.4 动态提示词优化](#144-动态提示词优化)
  - [14.5 提示词测试与迭代](#145-提示词测试与迭代)
  - [14.6 常见问题与解决方案](#146-常见问题与解决方案)
  - [14.7 实际应用场景](#147-实际应用场景)
  - [14.8 提示词优化工具](#148-提示词优化工具)
- [🤖 15. Agent（智能代理）vs 大模型（LLM）的区别](#-15-agent智能代理vs-大模型llm的区别)
- [🎯 16. 综合应用](#-16-综合应用)

### 第三部分：HuggingFace 工具总结
- [🛠️ 17. HuggingFace 常用工具类与 Pipeline 总结](#️-17-huggingface-常用工具类与-pipeline-总结)
  - [17.1 transformers 里的 Auto/专用类](#171-transformers-里的-auto专用类)
  - [17.2 diffusers 里的 Pipeline/Auto类](#172-diffusers-里的-pipelineauto类)
  - [17.3 常见用法举例](#173-常见用法举例)
  - [17.4 选择建议](#174-选择建议)

### 第四部分：Torch、HuggingFace、UV 区别与 ASGI 介绍
- [⚙️ 18. Torch、HuggingFace、UV 区别](#️-18-torchhuggingfaceuv-区别)
  - [18.1 核心框架对比](#181-核心框架对比)
  - [18.2 ASGI 简介](#182-asgi-简介)
  - [18.3 总结对比](#183-总结对比)

### 第五部分：PEFT 参数高效微调详解
- [🌀 19. PEFT 参数高效微调详解](#-19-peft-参数高效微调详解)
  - [19.1 PEFT 核心概念](#191-peft-核心概念)
  - [19.2 使用方法与代码示例](#192-使用方法与代码示例)
  - [19.3 PEFT 与 QLoRA 的关系](#193-peft-与-qlora-的关系)
  - [19.4 BitsAndBytes 与 Mac 兼容性](#194-bitsandbytes-与-mac-兼容性)

---

# 第一部分：模型家族分类整理

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

## 🧩 11. 衍生 & 混血类模型

| 模型 | 来源 | 基础 |
|------|------|------|
| Alpaca | Stanford | LLaMA 微调 |
| Vicuna | LMSYS | LLaMA + ShareGPT |
| Phoenix | Tsinghua | InternLM 中文强化 |
| OpenChat | 社区 | Mistral 微调 |

---

# 第二部分：大模型应用模式

在 ToB 多模态 AI 项目中，大模型通常有三种使用方式：

## 🚀 12. 直接调用现有大模型（不开箱即用）
- **适用场景**：通用对话、基础文生文、文生图、文生视频。
- **优点**：成本低，上线快。
- **实现方式**：直接调用现成 API 或开源模型（如 Stable Diffusion、Veo2、Minimax）。
- **缺点**：对垂直领域/企业定制化需求适配度有限。

## ⚙️ 13. 微调（Fine-tuning）现有大模型
- **适用场景**：需要角色人设、品牌风格或垂直领域知识。
- **实现方式**：在企业数据上做轻量参数微调（LoRA、PEFT）或全量微调。
- **优点**：效果定制化强，可提升一致性与专业度。
- **缺点**：需要算力与标注数据，维护成本高。

### 13.1 微调框架对比

**参数高效微调（PEFT）框架总览**：

| 框架 | 类型 | 可训练参数 | 内存使用 | 适用场景 | 技术特点 |
|------|------|------------|----------|----------|----------|
| **LoRA** | 低秩分解 | 0.1-1% | 低 | 通用任务 | 最流行，效果好 |
| **AdaLoRA** | 自适应低秩 | 0.1-1% | 低 | 复杂任务 | 动态调整参数 |
| **QLoRA** | 量化+LoRA | 0.1-1% | 极低 | 大模型微调 | 4bit量化节省内存 |
| **Prefix Tuning** | 前缀微调 | <0.1% | 极低 | 生成任务 | 只训练前缀 |
| **P-Tuning v2** | 提示微调 | <0.1% | 极低 | NLU任务 | 改进版提示学习 |
| **AdapterFusion** | 适配器融合 | 2-4% | 中等 | 多任务学习 | 组合多个适配器 |
| **BitFit** | 偏置微调 | <0.1% | 极低 | 简单任务 | 只训练bias参数 |
| **Full Fine-tuning** | 全量微调 | 100% | 高 | 高要求任务 | 传统方法 |

### 13.2 各框架详细介绍

#### **LoRA (Low-Rank Adaptation)**
- **原理**：将权重更新分解为两个低秩矩阵
- **优势**：效果接近全量微调，资源消耗少
- **适用**：最通用的选择，适合大多数任务
- **参数**：r=4-16, alpha=16-32

#### **QLoRA (Quantized LoRA)**
- **原理**：4bit量化基础模型 + LoRA微调
- **优势**：内存使用最少，可在消费级GPU微调大模型
- **适用**：资源极度受限，微调70B+模型
- **特点**：65B模型只需48GB显存

### 13.3 选择指南

**根据资源选择**：
- **GPU内存充足**：Full Fine-tuning > LoRA > AdaLoRA
- **GPU内存有限**：QLoRA > Prefix Tuning > P-Tuning v2
- **极度受限**：BitFit > Prefix Tuning

**根据任务选择**：
- **文本生成**：LoRA > Prefix Tuning > AdaLoRA
- **文本分类**：LoRA > P-Tuning v2 > BitFit

### 13.4 实际经验建议

**新手推荐**：
1. **首选LoRA**：成熟稳定，效果好，资料多
2. **GPU不够用QLoRA**：可以微调更大的模型

## 💡 14. 提示工程（Prompt Engineering + 外挂知识库/参数化控制）
- **适用场景**：无需改动模型本身，快速实现定制化。
- **实现方式**：通过精心设计 Prompt、外挂知识库（RAG）、规则控制生成结果。
- **优点**：灵活，成本低，迭代快。
- **缺点**：依赖 Prompt 设计，定制化能力有限。

### 14.1 提示词优化技术分类

#### **基础优化技术**

| 技术 | 原理 | 适用场景 | 效果 |
|------|------|----------|------|
| **角色扮演** | 给模型设定身份 | 专业咨询、创作 | 提高专业性 |
| **少样本学习(Few-shot)** | 提供示例 | 格式控制、风格模仿 | 提高一致性 |
| **思维链(CoT)** | 展示推理过程 | 复杂推理、数学题 | 提高准确性 |

#### **高级优化技术**

| 技术 | 原理 | 适用场景 | 效果 |
|------|------|----------|------|
| **检索增强(RAG)** | 外挂知识库 | 实时信息、专业知识 | 提高准确性 |
| **工具调用** | 集成外部API | 计算、查询、执行 | 扩展能力 |

### 14.2 具体优化方法详解

#### **1. 角色扮演（Role Playing）**

**简单理解**：让AI扮演特定角色，像请专家帮忙

**基础版本**：
```
你是一名资深财务分析师，请分析这份财报。
```

**优化版本**：
```
你是一名拥有15年经验的注册会计师和财务分析师。你擅长：
- 识别财务风险和机会
- 用通俗语言解释复杂财务概念
- 提供具体可行的建议

请分析以下财报，重点关注盈利能力和现金流状况。
```

#### **2. 少样本学习（Few-shot Learning）**

**简单理解**：给AI看几个例子，它就能模仿格式

**示例**：
```
请将以下内容转换为结构化格式：

例子1：
输入：小明今年25岁，是程序员
输出：{"姓名":"小明", "年龄":25, "职业":"程序员"}

例子2：
输入：李华32岁，从事设计工作
输出：{"姓名":"李华", "年龄":32, "职业":"设计师"}

现在请处理：张三28岁，是老师
```

#### **3. 检索增强生成（RAG）**

**简单理解**：AI先查资料，再回答问题

**工作流程**：
```
用户问题 → 检索相关文档 → 将文档作为上下文 → AI基于文档回答
```

## 🤖 15. Agent（智能代理）vs 大模型（LLM）的区别

### 核心区别概述

| 特征 | 大模型（LLM） | Agent（智能代理） |
|------|---------------|------------------|
| **定义** | 被动的语言理解和生成系统 | 主动的、目标导向的智能系统 |
| **交互方式** | 单轮对话，一问一答 | 多轮对话，持续交互 |
| **行动能力** | 只能生成文本回复 | 可以执行具体行动和任务 |
| **决策能力** | 根据输入生成输出 | 自主规划和决策执行路径 |
| **状态保持** | 无状态（除非外部记录） | 维护内部状态和记忆 |

### 详细对比分析

#### 1. **功能范围**

**大模型（LLM）：**
- 专注于语言理解和生成
- 回答问题、写作、翻译、总结等文本任务
- 被动响应用户输入

**Agent（智能代理）：**
- 具备完整的问题解决能力
- 可以分解复杂任务并逐步执行
- 主动采取行动达成目标
- 可以与外部系统交互

#### 2. **架构设计**

**大模型架构：**
```
输入文本 → 编码器 → 注意力机制 → 解码器 → 输出文本
```

**Agent架构：**
```
感知环境 → 规划决策 → 工具调用 → 执行行动 → 反馈评估 → 更新状态
```

#### Agent规划决策能力详解

**Agent的规划决策能力来源于几个核心组件的协同工作：**

**目标分解器**：把复杂任务拆分成简单步骤
**动作选择器**：在每个步骤中选择最佳行动
**依赖分析器**：理解哪些任务必须先完成
**资源管理器**：合理安排可用的工具和时间
**执行监控器**：实时监督进展并调整计划

**持续学习能力详解**

Agent会在每次对话中变得更聪明：

1. **记录反馈**：
   - 您说"这个分析太详细了" → Agent记住：下次简化
   - 您说"需要更多数据" → Agent记住：下次补充

2. **调整策略**：
   - 第1次：发送10页报告 → 您嫌太长
   - 第2次：发送5页报告 → 您说刚好
   - 第3次：自动生成5页报告

**持续学习 vs 微调的区别**

| 对比维度 | 微调 | 持续学习 |
|---------|------|----------|
| **学习内容** | 专业知识和技能 | 用户个人习惯 |
| **学习范围** | 整个行业/领域 | 单个用户 |
| **计算成本** | 高（需GPU训练） | 低（只需存储） |
| **更新频率** | 偶尔更新 | 实时更新 |

#### 3. **典型应用场景**

**大模型适用场景：**
- 内容创作和编辑
- 代码生成和解释
- 语言翻译
- 知识问答

**Agent适用场景：**
- 自动化工作流程
- 智能客服和助手
- 数据分析和报告生成
- 复杂业务流程处理

## 🎯 16. 综合应用
- **聊天（文生文）**：以现成 LLM 调用 + Prompt 优化为主，部分角色使用 LoRA 微调。
- **图片/视频（文生图/文生视频）**：主要调用现成模型（Stable Diffusion/ControlNet、Veo2/Veo3），结合 Prompt 规则控制；如需行业专属效果，可做定制化微调。

---

# 第三部分：HuggingFace 工具总结

## 🛠️ 17. HuggingFace 常用工具类与 Pipeline 总结

### 17.1 transformers 里的 Auto/专用类

#### **1. 通用自动加载类（AutoClass）**

- **AutoModel**  
  自动加载任意任务的基础模型（不带头部）。
- **AutoModelForSequenceClassification**  
  自动加载用于文本分类的模型。
- **AutoModelForTokenClassification**  
  自动加载用于序列标注（如NER）的模型。
- **AutoModelForQuestionAnswering**  
  自动加载用于问答的模型。
- **AutoModelForSeq2SeqLM**  
  自动加载用于序列到序列（如翻译、摘要）的模型。
- **AutoModelForMaskedLM**  
  自动加载用于掩码语言建模（如BERT）的模型。
- **AutoModelForImageClassification**  
  自动加载用于图像分类的模型。
- **AutoModelForVision2Seq**  
  图像到文本（如图像描述）模型。
- **AutoModelForSpeechSeq2Seq**  
  语音到文本（如ASR）模型。
- **AutoModelForAudioClassification**  
  音频分类模型。
- **AutoProcessor**  
  自动加载多模态处理器（如 CLIP、Whisper 等）。

#### **2. Tokenizer/Processor/FeatureExtractor**

- **AutoTokenizer**  
  自动加载分词器（文本任务）。
- **AutoFeatureExtractor**  
  自动加载特征提取器（图像、音频等）。
- **AutoProcessor**  
  自动加载多模态处理器（如 Whisper、CLIP）。

#### **3. 专用Pipeline**

- `pipeline("text-classification")`  文本分类
- `pipeline("question-answering")`  问答
- `pipeline("translation")`  翻译
- `pipeline("summarization")`  摘要
- `pipeline("image-classification")`  图像分类
- `pipeline("automatic-speech-recognition")`  语音识别
- `pipeline("image-to-text")`  图像描述
- `pipeline("zero-shot-classification")`  零样本分类
- `pipeline("text-to-speech")`  文本转语音
- `pipeline("document-question-answering")`  文档问答

### 17.2 diffusers 里的 Pipeline/Auto类

#### **1. 通用/专用Pipeline**

- **DiffusionPipeline**  
  通用扩散模型基类。
- **StableDiffusionPipeline**  
  文本生成图像。
- **StableDiffusionImg2ImgPipeline**  
  图像到图像生成。
- **StableDiffusionInpaintPipeline**  
  图像修复/补全。
- **StableDiffusionXLImg2ImgPipeline**  
  SDXL 图像到图像。
- **StableDiffusionXLInpaintPipeline**  
  SDXL 图像修复。
- **StableVideoDiffusionPipeline**  
  文本/图像生成视频。
- **StableAudioPipeline**  
  文本生成音频。
- **AudioLDMPipeline**  
  另一种音频扩散模型。
- **VersatileDiffusionPipeline**  
  多模态扩散模型。
- **ControlNetPipeline**  
  带控制条件的扩散模型。
- **PaintByExamplePipeline**  
  以例子图像为条件的生成。

#### **2. 其他专用类**

- **AutoencoderKL**  
  自动编码器（常用于扩散模型的VAE部分）。
- **UNet2DConditionModel**  
  条件UNet（扩散模型核心）。
- **DDIMScheduler/DPMSolverMultistepScheduler**  
  各类采样调度器。

### 17.3 常见用法举例

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
```

```python
from diffusers import StableDiffusionImg2ImgPipeline

pipe = StableDiffusionImg2ImgPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
```

### 17.4 选择建议

- **NLP任务**：优先用 transformers 的 AutoModelForXXX、AutoTokenizer、pipeline。
- **CV/音频/多模态**：transformers 也有 AutoModelForImageClassification、AutoModelForAudioClassification、AutoProcessor 等。
- **扩散模型**：用 diffusers 的 StableDiffusionPipeline、StableAudioPipeline、DiffusionPipeline 等。
- **多模态/自定义**：用 AutoProcessor、AutoFeatureExtractor、VersatileDiffusionPipeline 等。

---

# 第四部分：Torch、HuggingFace、UV 区别与 ASGI 介绍

## ⚙️ 18. Torch、HuggingFace、UV 区别

### 18.1 核心框架对比

#### **1. torch（PyTorch）**
- **类型**：深度学习框架
- **用途**：用于构建和训练神经网络，支持自动微分、GPU加速等。
- **典型场景**：图像识别、自然语言处理、强化学习等AI任务的底层实现。
- **代表功能**：张量运算、模型定义、训练循环、优化器等。

#### **2. huggingface（Hugging Face Transformers）**
- **类型**：NLP（自然语言处理）工具包/平台
- **用途**：提供大量预训练的NLP模型（如BERT、GPT、T5等），方便快速应用和微调。
- **典型场景**：文本分类、问答、翻译、文本生成等。
- **代表功能**：模型下载、推理、微调、数据集管理等。
- **依赖**：底层通常用PyTorch或TensorFlow作为后端。

#### **3. uv（uvicorn）**
- **类型**：ASGI服务器
- **用途**：用于运行基于ASGI协议的Python Web应用（如FastAPI、Starlette等）。
- **典型场景**：部署API服务，尤其是高性能异步Web服务。
- **代表功能**：高并发、异步支持、WebSocket支持等。

### 18.2 ASGI 简介

#### **什么是 ASGI？**

**ASGI**（Asynchronous Server Gateway Interface，异步服务器网关接口）是 Python Web 服务器与 Web 应用之间的通信协议标准。

#### **1. 背景**

- 早期 Python Web 应用主要采用 WSGI（Web Server Gateway Interface），但 WSGI 只支持同步（阻塞）请求。
- 随着异步编程（async/await）和 WebSocket 等实时通信需求的兴起，WSGI 已无法满足高并发和异步场景。

#### **2. ASGI 的作用**

- 允许 Web 应用支持**异步**和**同步**两种编程方式。
- 支持 HTTP、WebSocket 等多种协议。
- 使 Python Web 应用可以高效处理高并发、长连接、实时推送等现代 Web 需求。

#### **3. 应用场景**

- FastAPI、Starlette、Django 3.0+ 等现代 Web 框架都支持 ASGI。
- 适合需要高并发、实时通信（如聊天、推送、直播）的 Web 服务。

#### **4. 与 WSGI 的区别**

| 特性 | WSGI | ASGI |
|------|------|------|
| 支持异步 | 否 | 是 |
| 支持 WebSocket | 否 | 是 |
| 主要用途 | 传统 Web 应用 | 现代 Web 应用 |

#### **5. 常见 ASGI 服务器**

- **uvicorn**：轻量级高性能 ASGI 服务器
- **daphne**：Django 官方推荐 ASGI 服务器

#### **总结**

ASGI 是为了解决 Python Web 应用异步和高并发需求而设计的新一代接口标准，是现代 Python Web 开发的基础设施之一。

### 18.3 总结对比

| 名称 | 领域 | 主要用途 | 典型依赖/关系 |
|------|------|----------|----------|
| torch | 深度学习 | 神经网络底层实现 | 被huggingface等调用 |
| huggingface | NLP工具包 | 预训练模型与NLP任务 | 底层用torch或tensorflow |
| uv (uvicorn) | Web服务器 | 部署Python异步Web应用 | 与torch无直接关系 |

---

# 第五部分：PEFT 参数高效微调详解

## 🌀 19. PEFT 参数高效微调详解

### 19.1 PEFT 核心概念

`peft` 是 Hugging Face 推出的一个轻量化微调库，全称是 **Parameter-Efficient Fine-Tuning**。

#### **🧠 简单来说，PEFT 是什么？**

> **PEFT 是一套工具和方法，专门用于对大语言模型（LLM）做"只微调一小部分参数"的训练方式，既省资源又有效。**

它让你能轻松使用如：
- **LoRA**
- **Prefix Tuning**
- **Prompt Tuning**
- **IA3**
- **AdaLoRA**
等高效微调技术。

#### **✅ 为什么用 PEFT？**

传统的微调（full fine-tune）：
- 要修改上百亿参数
- 占内存、训练慢、显存爆炸

而 PEFT 方法只训练少量"额外注入的参数"，比如 LoRA 方式只训练几百万个参数。

> 所以 **你只需加一点小模块，就能训练原模型的新能力，还能保持推理快、成本低。**

### 19.2 使用方法与代码示例

#### **🔧 示例：用 LoRA 微调一个模型（常用于 QLoRA）**

```python
from peft import get_peft_model, LoraConfig, TaskType

peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,  # 用于语言建模
    inference_mode=False,
    r=8, lora_alpha=16, lora_dropout=0.1
)

model = get_peft_model(base_model, peft_config)
```

> 你就给 `base_model` 注入了可训练的 LoRA 层，**其他原始参数都被冻结**，只训练 LoRA。

#### **📚 安装方式：**

```bash
pip install peft
```

或

```bash
pip install git+https://github.com/huggingface/peft
```

#### **📘 文档/资料：**

- 官方文档： https://huggingface.co/docs/peft
- GitHub 仓库： https://github.com/huggingface/peft
- 中文讲解推荐：[知乎 PEFT 关键词搜](https://www.zhihu.com/search?q=PEFT)

### 19.3 PEFT 与 QLoRA 的关系

- `QLoRA = 4bit 量化 + LoRA 微调`
- PEFT 提供了其中的 **LoRA 注入逻辑**
- QLoRA 训练中通常会先加载量化模型，再用 PEFT 添加 LoRA

### 19.4 BitsAndBytes 与 Mac 兼容性

#### **❗关于 4-bit 量化和 CUDA 的现状**

**✅ BitsAndBytes (bnb) 支持平台：**
- BitsAndBytes 是一个专为 **NVIDIA GPU（CUDA）** 设计的低比特量化库。
- 它的高效 4-bit 和 8-bit 算法依赖于：
  - **CUDA 内核**
  - **NVIDIA GPU**
  - **Linux/Windows（x86_64 架构）**

**❌ 不支持的平台：**
- **Mac（尤其是 Apple Silicon M1/M2/M3）**
- 原因是：
  - Apple M 系列芯片使用 **Metal Performance Shaders (MPS)**，而不是 CUDA。
  - `bitsandbytes` 库内部调用大量 `.cu` 文件和 CUDA C/C++ 核心，无法兼容 Metal。

#### **🔄 替代方案（适用于 Mac）**

| 方案 | 是否支持 MPS | 说明 |
|------|--------------|------|
| 🔁 **使用 FP16 模型 + MPS 后端** | ✅ 支持 | 用 `transformers` + `torch.device("mps")` 加载模型 |
| ⚠️ **使用量化模型（已量化好）+ Ollama 或 GGUF** | ✅ 支持 | 靠 CPU/Apple GPU 推理，无需 bitsandbytes |
| ❌ **自己用 bitsandbytes 量化微调** | ❌ 不支持 | 只能在支持 CUDA 的 Linux/NVIDIA 机器上做 |

#### **🧩 推荐方式（在 Mac 上）**

**1. 加载已量化模型（例如 GGUF）**
使用 [Ollama](https://ollama.com) 或 llama.cpp，可以本地推理 LLaMA、Mistral 等模型：

```bash
ollama run llama3
```

或用 `transformers` + GGUF/ggml 格式推理（需要 CPU/GPU 后端支持）。

**2. 微调方案（Mac 上建议这样做）：**
- 云服务器（NVIDIA GPU）上训练（例如 QLoRA + bitsandbytes）
- 保存 adapter 或 delta 参数
- 下载到 Mac 上只做 **推理/加载**

> 若需要 QLoRA 微调脚本或在 Mac 上推理微调模型的完整代码，可以参考第二部分的微调框架对比章节。
