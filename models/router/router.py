import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import PeftModel

class SequenceClassificationRouter:
    def __init__(self, model_path, classes, device_map="auto", peft_path=None, use_bits_and_bytes=False, use_peft=False):
        if use_bits_and_bytes:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=False,
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_path,
                device_map=device_map,
                num_labels=len(classes),
                quantization_config=bnb_config,
                torch_dtype=torch.bfloat16,
            )
        else:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_path,
                device_map=device_map,
                num_labels=len(classes),
                torch_dtype=torch.bfloat16,
            )
        if use_peft:
            assert peft_path is not None, "PEFT path is required."
            self.model = PeftModel.from_pretrained(
                self.model,
                peft_path
            )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.classes = classes
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def __call__(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        outputs = self.model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax().item()
        predicted_class = self.classes[predicted_class_idx]
        return predicted_class