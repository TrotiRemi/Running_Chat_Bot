from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
input_text = "Je suis un coureur"
inputs = tokenizer(input_text, return_tensors='pt')
outputs = model.generate(**inputs, max_length=50)
print(tokenizer.decode(outputs[0]))