def read_words(): 
    with open('08_hangman/words.txt') as f:
        text = f.read().split(',')
    return text

def select_random_word():
    import random
    return random.choice(read_words())

letters = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'])
chosen_char = set()

word = select_random_word()
guess = ['-' for _ in range(len(word)-1)]

num_turns = 5

print(word)

while num_turns > 0:
    print('\nGuess: ',''.join(guess))
    
    char = input("Type a character: ")
    if char in chosen_char or char not in letters: 
        print('Wrong letter')
        continue
    
    if char not in word: 
        print('Character is not in the word.')
        chosen_char.add(char)
        num_turns -= 1
    
    else:
        index = []
        for i, v in enumerate(word):
            if v == char:
                guess[i-1] = char
                
        print('The letter is present in the word')


    print(f'You have {num_turns} more turns left.')    
        
    


