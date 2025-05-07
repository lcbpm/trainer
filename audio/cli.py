import torch
import torchaudio
import argparse
import os
from einops import rearrange
from stable_audio_tools import get_pretrained_model
from stable_audio_tools.inference.generation import generate_diffusion_cond

# 设置命令行参数
parser = argparse.ArgumentParser(description='生成音频')
parser.add_argument('--local_model_path', type=str, help='本地模型路径，包含model.safetensors和model_config.json文件')
parser.add_argument('--prompt', type=str, default='128 BPM tech house drum loop', help='音频生成提示词')
parser.add_argument('--duration', type=float, default=30, help='音频时长（秒）')
parser.add_argument('--output_file', type=str, default='output.wav', help='输出文件路径')
parser.add_argument('--token', type=str, help='Hugging Face API令牌')
parser.add_argument('--proxy', type=str, help='HTTP/HTTPS代理，例如：http://localhost:7890')
args = parser.parse_args()

# 设置代理（如果提供）
if args.proxy:
    os.environ['HTTP_PROXY'] = args.proxy
    os.environ['HTTPS_PROXY'] = args.proxy
    print(f"已设置代理: {args.proxy}")

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")

# 加载模型
print(f"正在加载模型...")
try:
    if args.local_model_path:
        # 检查本地模型文件是否存在
        model_path = os.path.join(args.local_model_path, "model.safetensors")
        config_path = os.path.join(args.local_model_path, "model_config.json")
        print(f"本地模型文件路径: {model_path}")
        print(f"本地模型配置文件路径: {config_path}")
        print(f"os.path:{os.path.abspath}")
        if not os.path.exists(model_path) or not os.path.exists(config_path):
            raise FileNotFoundError(f"本地模型文件不完整，请确保{model_path}和{config_path}都存在")
            
        print(f"从本地路径加载模型: {args.local_model_path}")
        # 直接使用本地路径加载模型
        model, model_config = get_pretrained_model(args.local_model_path)
    else:
        # 从Hugging Face下载模型
        print("从Hugging Face下载模型: stabilityai/stable-audio-open-1.0")
        token = args.token if args.token else None
        model, model_config = get_pretrained_model("stabilityai/stable-audio-open-1.0", token=token)
        
    print(f"时长: {args.duration}秒")
    print(f"输出文件: {args.output_file}")
    
    conditioning = [{
        "prompt": args.prompt,
        "seconds_start": 0,
        "seconds_total": args.duration
    }]
    
    # 生成立体声音频
    print("开始生成音频...")
    output = generate_diffusion_cond(
        model,
        steps=100,
        cfg_scale=7,
        conditioning=conditioning,
        sample_size=sample_size,
        sigma_min=0.3,
        sigma_max=500,
        sampler_type="dpmpp-3m-sde",
        device=device
    )
    print("音频生成完成！")
    
    # Rearrange audio batch to a single sequence
    output = rearrange(output, "b d n -> d (b n)")
    
    # 峰值归一化，裁剪，转换为int16，并保存到文件
    print("正在处理音频...")
    output = output.to(torch.float32).div(torch.max(torch.abs(output))).clamp(-1, 1).mul(32767).to(torch.int16).cpu()
    
    print(f"正在保存音频到 {args.output_file}...")
    torchaudio.save(args.output_file, output, sample_rate)
    print(f"音频已成功保存到: {args.output_file}")
    print("处理完成！")
    
except Exception as e:
    print(f"模型加载失败: {str(e)}")
    print("\n可能的解决方案:")
    print("1. 确保您已登录Hugging Face并接受模型使用条款: https://huggingface.co/stabilityai/stable-audio-open-1.0")
    print("2. 使用--token参数提供Hugging Face API令牌")
    print("3. 下载模型文件并使用--local_model_path参数指定本地路径")
    print("4. 如果网络连接有问题，请使用--proxy参数设置代理")
    exit(1)