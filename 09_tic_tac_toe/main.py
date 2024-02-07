# Tic-tac-toe using minimax

state = [['' for _ in range(3)] for _ in range(3)]
# state = [[1,2,3], ['', 4,''], [1,2,'']]


def action(state):
    empty = []
    
    for ind1, block in enumerate(state):
        for ind2, i in enumerate(block):
            if i == '':
                empty.append([ind1, ind2])
    return empty

def transition(state,action): return 'new state'

def terminal_state(state): return True

def utility(state): return 1

def is_valid(action): return True


if __name__ == '__main__':
    print(action(state))



def minimax_max(state):
    if terminal_state(state):
        return utility(state), state
    
    actions = action(state)
    v = 10
    for a in actions:
        new_state = transition(state, a)
        v_, s = minimax_min(state)
        if v_ < v:
            v = v_
            return_state = s
            
 
def minimax_min(state):
    if terminal_state(state):
        return utility(state), state
    
    actions = action(state)
    
    v = -10
    for a in actions:
        new_state = transition(state, a)
        
        v_, s = minimax_max(state)
        
        if v_ > v:
            v = v_
            return_state = s
            
        

    
    
    
    
# for i in range(5):
#     print(state)
    
#     move = tuple(input('Enter a move'))
#     print(move)

#     if not is_valid(move):
#         continue # bug here
    
#     state = transition(state, move)
    
#     # Mini-max
    
#     minimax_max(state)
    
    
    
    