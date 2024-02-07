# Tic-tac-toe using minimax
from copy import deepcopy
state = [['' for _ in range(3)] for _ in range(3)]
# state = [[1,2,3], [5, 4,5], [1,2,'x']]



def action(state):
    empty = []
    
    for ind1, block in enumerate(state):
        for ind2, i in enumerate(block):
            if i == '':
                empty.append([ind1, ind2])
    return empty

def transition(state,action,player):
    new_state = deepcopy(state)
    new_state[action[0]][action[1]] = player
    return new_state
    
    

def terminal_state(state): 
    
    wins = [[[0,0], [0,1], [0,2]],
            [[1,0], [1,1], [1,2]],
            [[2,0], [2,1], [2,2]],
            [[0,0], [1,0], [2,0]],
            [[0,1], [1,1], [2,1]],
            [[0,2], [1,2], [2,2]],
            [[0,0], [1,1], [2,2]],
            [[0,2], [1,1], [2,0]],
    ]
    for win in wins:
        x,o = 0, 0
        for w in win:
            if state[w[0]][w[1]] == 'X': x += 1
            if state[w[0]][w[1]] == 'O': o += 1
        if x == 3: return True, -1
        if o == 3: return True, 1
        
    if action(state) == []: return True, 0
    return False, None
            

def is_valid(state, act):
    if act in action(state):
        return True
    return False


def minimax_max(state):
    print(state)
    if terminal_state(state)[0]:
        print('Terminal')
        return terminal_state(state)[1], state
    
    actions = action(state)
    v = 10
    for a in actions:
        new_state = transition(state, a, "O").copy()
        v_, s = minimax_min(new_state)
        if v_ < v:
            v = v_
            return_action= a
    return v,return_action 
 
def minimax_min(state):
    print(state)
    if terminal_state(state)[0]:
        return terminal_state(state)[1], state
    
    actions = action(state)
    
    v = -10
    for a in actions:
        new_state = transition(state, a, 'X').copy()
        
        v_, s = minimax_max(new_state)
        
        if v_ > v:
            v = v_
            return_action = a
    return v,return_action
            
        

    
    
    
    
for i in range(5):
    # print(state)
    
    move = input('Enter a move: ')
    move = [int(move[0]), int(move[-1])]
    print(move)
    if not is_valid(state, move):
        print("Move is Invalid")
        continue # bug here
    
    state = transition(state, move, 'X')
    
    if terminal_state(state)[0]: 
        print(terminal_state(state)[1])
        print('Player Won')     
        break
    # print(state)
    
    # Mini-max
    
    _, act = minimax_max(state)
    state = transition(state, act, 'O')
    
    print('-'*20)
    print(state)
    
    if terminal_state(state)[0]: 
        print(terminal_state(state)[1])
        print('Computer Won')     
        break   
    