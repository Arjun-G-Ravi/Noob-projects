from datasets import load_dataset

dataset = load_dataset("carblacac/twitter-sentiment-analysis",)
X = dataset['train']['text'][:1000]
y = dataset['train']['feeling'][:1000]
print(len(X), len(y))

print(X[10], y[10])