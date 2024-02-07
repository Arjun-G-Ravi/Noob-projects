# Tic-tac-toe using minimax

state = [['' for _ in range(3)] for _ in range(3)]

def action(state): return 'states'

def transition(state,action): return 'new state'

def terminal_state(state): return True

def utility(state): return 1

def is_valid(action): return True


def minimax_max(state):
    if terminal_state(state):
        return utility(state)
    
    actions = action(state)
    max_utility = [(),-10]
    
    for a in actions:
        new_state = transition(state, a)
        
        minimax(state)
        
 
def minimax_min(state):
    if terminal_state(state):
        return utility(state)
    
    actions = action(state)
    max_utility = [(),-10]
    
    for a in actions:
        new_state = transition(state, a)
        
        minimax(state)
        

    
    
    
    
for i in range(5):
    print(state)
    
    move = tuple(input('Enter a move'))
    print(move)

    if not is_valid(move):
        continue # bug here
    
    state = transition(state, move)
    
    # Mini-max
    
    moves = action(state)
    
    
    
    