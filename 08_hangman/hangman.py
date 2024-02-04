def read_words(): 
    with open('08_hangman/words.txt') as f:
        text = f.read().split(',')

    return text

def select_random_word():
    import random
    return random.choice(read_words())

letters = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'])
chosen_char = set()

word = select_random_word().strip()
guess = ['-' for _ in range(len(word))]

num_turns = 7
num_letters_guessed = 0

while num_turns > 0:
    print(f'You have {num_turns} more turns left.')    
    print('\nGuess: ',''.join(guess))
    print('Letters used:', list(chosen_char))
    
    char = input("Type a character: ")
    if char in chosen_char or char not in letters: 
        print('Wrong letter')
        continue
    
    if char not in word: 
        print('Character is not in the word.')
        chosen_char.add(char)
        num_turns -= 1
        continue
    
    index = []
    for i, v in enumerate(word):
        if v == char:
            guess[i] = char
            num_letters_guessed += 1
            
    print('The letter is present in the word')

    if len(word) == num_letters_guessed:
        print('Congrats. You correctly guessed the word:', word)
        quit(0)
    
print('You lost. The word was', word)