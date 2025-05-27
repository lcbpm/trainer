from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained("/Users/test/traeproject/trainer/image/models/stable-video-diffusion-img2vid-xt")

prompt = "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"
image = pipe(prompt).images[0]