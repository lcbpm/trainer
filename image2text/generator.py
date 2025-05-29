from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image

processor = Blip2Processor.from_pretrained("/Users/test/traeproject/trainer/image2text/models/blip2-flan-t5-xl")
model = Blip2ForConditionalGeneration.from_pretrained("/Users/test/traeproject/trainer/image2text/models/blip2-flan-t5-xl")

image = Image.open("/Users/test/traeproject/trainer/image2text/models/blip2-flan-t5-xl/222.png").convert("RGB")
question = "图片里有几只猫？"
inputs = processor(images=image, text=question, return_tensors="pt")
out = model.generate(**inputs)
answer = processor.tokenizer.decode(out[0], skip_special_tokens=True)
print("模型回答：", answer)