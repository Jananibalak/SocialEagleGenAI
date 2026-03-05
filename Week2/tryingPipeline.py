from transformers import pipeline
generator = pipeline("text-generation",model="gpt2")

result = generator ("The silent people conquers",max_new_tokens=50)

print(result)

# Example: Sentiment analysis
classifier = pipeline("sentiment-analysis")
result = classifier("We spent our holidays in my hometown")
print(result)