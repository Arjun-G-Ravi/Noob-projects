import pickle

s = 'hi'

f = open('/home/arjun/Desktop/GitHub/Noob-projects/cow.txt', 'r')
s = f.read()
f.seek(10)
print(f.tell())
f.close()
# print(s)

