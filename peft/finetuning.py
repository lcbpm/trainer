from transformers import (
    AutoModelForCausalLM, 
    Trainer, 
    AutoTokenizer, 
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset
import torch

class ModelTrainer:
    def __init__(self, model_name="uer/gpt2-chinese-cluecorpussmall"):
        self.model_name = model_name
        self.device = self._setup_device()
        self.model_kwargs = {
            "torch_dtype": torch.float32,
            "low_cpu_mem_usage": True,
        }
        
    def _setup_device(self):
        device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
        print(f"使用设备: {device}")
        return device
        
    def setup_tokenizer(self):
        print(f"正在加载模型: {self.model_name}")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        return tokenizer
        
    def load_base_model(self):
        print("正在加载基础模型...")
        base_model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **self.model_kwargs
        ).to(self.device)
        return base_model
        
    def setup_peft_model(self, base_model):
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=4,
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["c_proj", "c_attn"]
        )
        print("正在应用LoRA配置...")
        model = get_peft_model(base_model, peft_config)
        model.print_trainable_parameters()
        return model
        
    def prepare_dataset(self, tokenizer):
        print("正在准备训练数据...")
        dataset = load_dataset("BelleGroup/train_0.5M_CN")
        train_dataset = dataset['train'].select(range(1000))
        return self._process_dataset(train_dataset, tokenizer)
        
    def _format_conversation(self, example, tokenizer):
        text = f"用户: {example['instruction']}\n助手: {example['output']}"
        encoded = tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=512,
            return_tensors=None
        )
        return encoded
        
    def _process_dataset(self, train_dataset, tokenizer):
        def process_function(x):
            formatted = self._format_conversation(x, tokenizer)
            return {
                "input_ids": formatted["input_ids"],
                "attention_mask": formatted["attention_mask"],
                "labels": formatted["input_ids"]
            }
            
        return train_dataset.map(
            process_function,
            remove_columns=train_dataset.column_names
        )
        
    def setup_training(self, model, processed_dataset, tokenizer):
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
            pad_to_multiple_of=8
        )
        
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=3,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=50,
            learning_rate=1e-4,
            logging_steps=10,
            save_steps=50,
            save_total_limit=2,
            dataloader_pin_memory=False,
            optim="adamw_torch",
            weight_decay=0.01,
            remove_unused_columns=False,
            gradient_checkpointing=False,
            max_grad_norm=0.5
        )
        
        return Trainer(
            model=model,
            train_dataset=processed_dataset,
            data_collator=data_collator,
            args=training_args,
        )
        
    def train_and_save(self, model, trainer):
        model.config.use_cache = False
        model.train()
        
        print("开始训练...")
        trainer.train()
        print("训练完成！")
        
        print("正在保存模型...")
        model.save_pretrained("./results/final-model")
        print("模型已保存到 ./results/final-model")

def main():
    trainer = ModelTrainer()
    tokenizer = trainer.setup_tokenizer()
    base_model = trainer.load_base_model()
    model = trainer.setup_peft_model(base_model)
    processed_dataset = trainer.prepare_dataset(tokenizer)
    trainer_instance = trainer.setup_training(model, processed_dataset, tokenizer)
    trainer.train_and_save(model, trainer_instance)

if __name__ == "__main__":
    main()
