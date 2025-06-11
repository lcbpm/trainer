# 文本生成音频（Text-to-Audio）主流模型整理

## 1. 扩散模型（Diffusion Models）

- **Stable Audio**
  - 你当前代码用的就是 Stable Audio（StableAudioPipeline，diffusers库）。
  - 基于扩散模型，支持高质量音乐、音效等生成。

- **AudioLDM**
  - 基于扩散模型，支持文本到音频、音乐、环境音等多种音频生成任务。
  - diffusers库有支持。

- **AudioGen**
  - Meta（Facebook）提出，擅长环境音效的文本到音频生成。
  - 已开源。

---

## 2. 语言-音频对齐大模型

- **MusicLM**
  - Google提出，专注于文本到音乐的生成，能生成复杂、长时长的音乐片段。
  - 暂未完全开源，但有论文和部分demo。

- **MusicGen**
  - Meta提出，专注于音乐生成，支持多种风格和乐器。
  - 已开源。

---

## 3. 其他代表性模型

- **Tango**
  - 结合扩散和对抗生成网络（GAN），用于高质量音频生成。

- **Jukebox**
  - OpenAI提出，专注于歌曲生成（包括歌词和旋律）。

---

## 4. 你当前代码用的是

- **Stable Audio**（StableAudioPipeline，diffusers库）

---

## 5. 其他常见开源模型

- **AudioLDM**（diffusers库支持）
- **AudioGen**（Meta开源）
- **MusicGen**（Meta开源）
- **MusicLM**（Google，部分开放）

---