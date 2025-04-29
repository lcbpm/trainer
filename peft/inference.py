from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

class ModelInference:
    def __init__(self, model_name="uer/gpt2-chinese-cluecorpussmall"):
        self.model_name = model_name
        self.device = self._setup_device()
        self.model_kwargs = self._get_model_kwargs()
        self.tokenizer = None
        self.model = None
        
    def _setup_device(self):
        """Setup computing device"""
        return torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    
    def _get_model_kwargs(self):
        """Get model loading configuration"""
        return {
            "torch_dtype": torch.float32,
            "low_cpu_mem_usage": True,
        }
    
    def setup_tokenizer(self):
        """Initialize and setup tokenizer"""
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
    def load_base_model(self):
        """Load and setup base model"""
        print("Loading base model...")
        base_model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **self.model_kwargs
        )
        return base_model.to(self.device)
    
    def load_fine_tuned_model(self, base_model, model_path):
        """Load fine-tuned model"""
        print("Loading fine-tuned model...")
        self.model = PeftModel.from_pretrained(base_model, model_path)
        self.model = self.model.to(self.device)
        self.model.eval()
        
    def generate_text(self, prompt, max_length=50):
        """Generate text based on input prompt"""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.6,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                top_p=0.95,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                early_stopping=True,
                length_penalty=1.0
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return ''.join(generated_text.split())
    
    def run_test_prompts(self, prompts):
        """Run test prompts and print results"""
        print("\nStarting test dialogue:")
        for prompt in prompts:
            try:
                generated_text = self.generate_text(prompt)
                print(f"Input: {prompt}")
                print(f"Output: {generated_text}")
            except Exception as e:
                print(f"Error generating response: {str(e)}")
                continue

# Initialize and run
if __name__ == "__main__":
    model_inference = ModelInference()
    model_inference.setup_tokenizer()
    base_model = model_inference.load_base_model()
    model_inference.load_fine_tuned_model(base_model, "./results/final-model")
    
    test_prompts = [
        "你是谁",
        "你能做什么",
        "介绍一下你自己"
    ]
    
    model_inference.run_test_prompts(test_prompts)
