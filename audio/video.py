import torch
from diffusers import StableAudioPipeline, DPMSolverMultistepScheduler
from scipy.io.wavfile import write as write_wav
import numpy as np

# 使用本地路径加载模型
pipe = StableAudioPipeline.from_pretrained(
       "/Users/test/traeproject/trainer/audio/models/stable-audio-open-1.0",
       torch_dtype=torch.float32,
       config="/Users/test/traeproject/trainer/audio/models/stable-audio-open-1.0/model_config.json"
   ).to("cuda" if torch.cuda.is_available() else "cpu")

# 切换调度器
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# 生成音频
prompt = "An emotional piano melody with strings in the background"
output = pipe(prompt=prompt, num_inference_steps=20)
audio = output.audios[0]
sample_rate = 44100

audio_np = audio.cpu().numpy()

# 如果是 [channels, samples]，转为 [samples, channels]
if audio_np.ndim == 2 and audio_np.shape[0] < audio_np.shape[1]:
    audio_np = audio_np.T

# 归一化并转换为 int16
audio_int16 = (audio_np * 32767).clip(-32768, 32767).astype(np.int16)

write_wav("generated_audio.wav", sample_rate, audio_int16)
print("音频已保存为 generated_audio.wav")
