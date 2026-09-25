import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset

# 1. VERIFY GPU AVAILABILITY
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device} ({torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'})")

# 2. DOWNLOAD MODEL & TOKENIZER
# Using a tiny, lightweight model (Qwen2.5-0.5B) for a fast test
model_name = "Qwen/Qwen2.5-0.5B"
print(f"Downloading {model_name}...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set padding token if it doesn't exist
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id

# 3. LOAD TO GPU
model = model.to(device)
print("Model successfully loaded onto GPU!")

# --- TASK 1: RUN INFERENCE TEST ---
print("\n--- Running Inference ---")
prompt = "The future of Artificial Intelligence is"
inputs = tokenizer(prompt, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=20)

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"Prompt: {prompt}")
print(f"Generated Output: {response}")

# --- TASK 2: PREPARE FOR FINE-TUNING ---
print("\n--- Preparing Fine-Tuning Pipeline ---")
# Create a tiny dummy dataset
dummy_data = {"text": ["AI is changing the world.", "Machine learning is a subset of AI."]}
dataset = Dataset.from_dict(dummy_data)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=32)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Set up basic training configurations
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=1,
    num_train_epochs=1,
    logging_steps=1,
    fp16=True, # Uses your GPU's tensor cores for faster training
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)
print("Fine-tuning pipeline initialized successfully! Ready for your data.")
