# s = 'Hey there! What is your your your name'
# import nltk

# words = ['run', 'running', 'runned']

# stemmer = nltk.stem.PorterStemmer()

# print(stemmer.stem(i for i in words))

from nltk.stem import PorterStemmer, SnowballStemmer

porter = PorterStemmer()
snowball = SnowballStemmer(language="english")

words = ['run', 'running', 'ran', 'runned','run']
porter_results = [porter.stem(word) for word in words]
snowball_results = [snowball.stem(word) for word in words]

print("Porter Stemmer Results:", porter_results)
print("Snowball Stemmer Results:", snowball_results)