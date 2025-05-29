 # HuggingFace 常用工具类与 Pipeline 总结

## 一、transformers 里的 Auto/专用类

### 1. 通用自动加载类（AutoClass）

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

### 2. Tokenizer/Processor/FeatureExtractor

- **AutoTokenizer**  
  自动加载分词器（文本任务）。
- **AutoFeatureExtractor**  
  自动加载特征提取器（图像、音频等）。
- **AutoProcessor**  
  自动加载多模态处理器（如 Whisper、CLIP）。

### 3. 专用Pipeline

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

---

## 二、diffusers 里的 Pipeline/Auto类

### 1. 通用/专用Pipeline

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

### 2. 其他专用类

- **AutoencoderKL**  
  自动编码器（常用于扩散模型的VAE部分）。
- **UNet2DConditionModel**  
  条件UNet（扩散模型核心）。
- **DDIMScheduler/DPMSolverMultistepScheduler**  
  各类采样调度器。

---

## 三、常见用法举例

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

---

## 四、选择建议

- **NLP任务**：优先用 transformers 的 AutoModelForXXX、AutoTokenizer、pipeline。
- **CV/音频/多模态**：transformers 也有 AutoModelForImageClassification、AutoModelForAudioClassification、AutoProcessor 等。
- **扩散模型**：用 diffusers 的 StableDiffusionPipeline、StableAudioPipeline、DiffusionPipeline 等。
- **多模态/自定义**：用 AutoProcessor、AutoFeatureExtractor、VersatileDiffusionPipeline 等。

---
