import pygame
import random
import sys
import numpy as np
import pickle
import os
from datetime import datetime

# Initialize pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (0, 0, 0)  # Black
WHITE = (255, 255, 255)
PADDLE_COLOR = (200, 200, 200)
BALL_COLOR = (255, 255, 255)
FONT_COLOR = (255, 255, 255)
RL_LEARNING_COLOR = (0, 255, 0)  # Green for when RL is learning

# Game objects dimensions
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15
PADDLE_SPEED = 7
AI_PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# RL Agent Parameters
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95
EXPLORATION_RATE = 0.3
EXPLORATION_DECAY = 0.9999
MIN_EXPLORATION_RATE = 0.01

# State discretization
GRID_SIZE_X = 8
GRID_SIZE_Y = 6
VELOCITY_STATES = 4  # -fast, -slow, +slow, +fast

class Ball:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])
        self.rect = pygame.Rect(x, y, size, size)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Collision with top and bottom walls
        if self.y <= 0 or self.y + self.size >= SCREEN_HEIGHT:
            self.speed_y *= -1
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2 - self.size // 2
        self.y = SCREEN_HEIGHT // 2 - self.size // 2
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        pygame.draw.rect(screen, BALL_COLOR, self.rect)

class Paddle:
    def __init__(self, x, y, width, height, is_ai=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_ai = is_ai
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = AI_PADDLE_SPEED if is_ai else PADDLE_SPEED
    
    def update(self, direction=0):
        if direction == 1 and self.y > 0:
            self.y -= self.speed
        elif direction == -1 and self.y + self.height < SCREEN_HEIGHT:
            self.y += self.speed
        
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect)

class RLAgent:
    def __init__(self, paddle):
        self.paddle = paddle
        
        # Initialize Q-table with state-action pairs
        # State: (ball_x, ball_y, ball_direction_x, ball_direction_y, paddle_y)
        # Actions: 0 (stay), 1 (up), 2 (down)
        self.q_table = {}
        
        self.learning_rate = LEARNING_RATE
        self.discount_factor = DISCOUNT_FACTOR
        self.exploration_rate = EXPLORATION_RATE
        self.exploration_decay = EXPLORATION_DECAY
        self.min_exploration_rate = MIN_EXPLORATION_RATE
        
        self.last_state = None
        self.last_action = None
        self.episode_rewards = 0
        self.total_rewards = []
        self.hit_count = 0
        self.miss_count = 0
        
    def get_state(self, ball, player1_paddle, player2_paddle):
        # Discretize ball position
        ball_x = int(ball.x / (SCREEN_WIDTH / GRID_SIZE_X))
        ball_y = int(ball.y / (SCREEN_HEIGHT / GRID_SIZE_Y))
        
        # Discretize ball direction
        ball_dir_x = 1 if ball.speed_x > 0 else 0
        if abs(ball.speed_y) < BALL_SPEED_Y:
            ball_dir_y = 1 if ball.speed_y > 0 else 0
        else:
            ball_dir_y = 3 if ball.speed_y > 0 else 2
            
        # Discretize paddle position
        paddle_y = int(self.paddle.y / (SCREEN_HEIGHT / GRID_SIZE_Y))
        
        return (ball_x, ball_y, ball_dir_x, ball_dir_y, paddle_y)
    
    def choose_action(self, state):
        # Exploration vs. exploitation
        if random.random() < self.exploration_rate:
            return random.randint(0, 2)  # Randomly choose (stay, up, down)
        
        # Exploitation: choose the best action from Q-table
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]  # Initialize Q-values for new state
        
        return np.argmax(self.q_table[state])
    
    def learn(self, state, action, reward, next_state, done):
        # Initialize Q-values if states not in Q-table
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]
        
        if next_state not in self.q_table and not done:
            self.q_table[next_state] = [0, 0, 0]
        
        # Q-learning update
        if not done:
            max_next_q = np.max(self.q_table[next_state])
            self.q_table[state][action] = (1 - self.learning_rate) * self.q_table[state][action] + \
                                         self.learning_rate * (reward + self.discount_factor * max_next_q)
        else:
            self.q_table[state][action] = (1 - self.learning_rate) * self.q_table[state][action] + \
                                         self.learning_rate * reward
        
        # Decay exploration rate
        self.exploration_rate = max(self.min_exploration_rate, 
                                   self.exploration_rate * self.exploration_decay)
        
        self.episode_rewards += reward
    
    def update(self, ball, player1_paddle, player2_paddle):
        current_state = self.get_state(ball, player1_paddle, player2_paddle)
        action = self.choose_action(current_state)
        
        # Map action (0, 1, 2) to paddle direction (0, 1, -1)
        direction = 0
        if action == 1:
            direction = 1  # Up
        elif action == 2:
            direction = -1  # Down
            
        # Update paddle position
        self.paddle.update(direction)
        
        return current_state, action
    
    def reward(self, ball, hit=False, miss=False, closer=False):
        reward = 0
        
        if hit:
            reward = 10  # Reward for hitting the ball
            self.hit_count += 1
        elif miss:
            reward = -15  # Penalty for missing the ball
            self.miss_count += 1
        elif closer and ball.speed_x < 0:  # Ball is moving towards the AI
            # Small reward for moving towards the ball
            vertical_distance = abs((self.paddle.y + self.paddle.height/2) - (ball.y + ball.size/2))
            reward = max(0, 0.1 * (1 - vertical_distance/SCREEN_HEIGHT))
        
        return reward
    
    def save_model(self, filename="27_Double_pong/rl_pong_model.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'exploration_rate': self.exploration_rate,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'total_rewards': self.total_rewards
            }, f)
        print(f"Model saved to {filename}")
    
    def load_model(self, filename="27_Double_pong/rl_pong_model.pkl"):
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.q_table = data['q_table']
                self.exploration_rate = data['exploration_rate']
                self.hit_count = data.get('hit_count', 0)
                self.miss_count = data.get('miss_count', 0)
                self.total_rewards = data.get('total_rewards', [])
            print(f"Model loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"Model file {filename} not found. Starting with a new model.")
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

def main():
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RL Pong Game - RL Agent vs Two Players")
    
    # Create game clock
    clock = pygame.time.Clock()
    
    # Create font for display
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Create game objects
    ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE)
    
    # Left paddle (RL Agent)
    ai_paddle = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, 
                        PADDLE_WIDTH, PADDLE_HEIGHT, is_ai=True)
    
    # Right paddles (Human players)
    # Upper paddle - controlled by UP/DOWN
    player1_paddle = Paddle(SCREEN_WIDTH - 20 - PADDLE_WIDTH, 
                           SCREEN_HEIGHT // 4 - PADDLE_HEIGHT // 2,
                           PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # Lower paddle - controlled by W/S
    player2_paddle = Paddle(SCREEN_WIDTH - 20 - PADDLE_WIDTH, 
                           3 * SCREEN_HEIGHT // 4 - PADDLE_HEIGHT // 2,
                           PADDLE_WIDTH, PADDLE_HEIGHT)
    
    # Create RL agent
    rl_agent = RLAgent(ai_paddle)
    
    # Try to load existing model
    model_loaded = rl_agent.load_model()
    
    # Scores
    ai_score = 0
    players_score = 0
    
    # Game state tracking
    last_hit_time = 0
    training_mode = True
    ball_last_x = ball.x
    
    # Game loop
    running = True
    game_start_time = pygame.time.get_ticks()
    auto_save_interval = 60000  # Save every minute
    last_save_time = game_start_time
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    # Toggle training mode
                    training_mode = not training_mode
                    print(f"Training mode: {'ON' if training_mode else 'OFF'}")
                elif event.key == pygame.K_s:
                    # Save model
                    rl_agent.save_model()
                elif event.key == pygame.K_r:
                    # Reset scores
                    ai_score = 0
                    players_score = 0
        
        # Get keys pressed
        keys = pygame.key.get_pressed()
        
        # Player 1 controls (arrow keys)
        player1_direction = 0
        if keys[pygame.K_UP]:
            player1_direction = 1
        elif keys[pygame.K_DOWN]:
            player1_direction = -1
        
        # Player 2 controls (W/S keys)
        player2_direction = 0
        if keys[pygame.K_w]:
            player2_direction = 1
        elif keys[pygame.K_s]:
            player2_direction = -1
        
        # Save ball's previous x position to determine direction
        ball_last_x = ball.x
        
        # Update game objects
        ball.update()
        player1_paddle.update(player1_direction)
        player2_paddle.update(player2_direction)
        
        # Get current state and action for RL agent
        current_state, action = rl_agent.update(ball, player1_paddle, player2_paddle)
        
        # Check for ball collision with AI paddle
        hit_occurred = False
        if ball.rect.colliderect(ai_paddle.rect):
            ball.speed_x *= -1
            ball.x = ai_paddle.x + ai_paddle.width  # Prevent getting stuck
            hit_occurred = True
            last_hit_time = current_time
        
        # Check for ball collision with player paddles
        if ball.rect.colliderect(player1_paddle.rect) or ball.rect.colliderect(player2_paddle.rect):
            ball.speed_x *= -1
            ball.x = player1_paddle.x - ball.size  # Prevent getting stuck
        
        # RL rewards and learning
        reward = 0
        game_over = False
        
        if hit_occurred:
            reward = rl_agent.reward(ball, hit=True)
        elif ball.x <= 0:  # AI missed the ball
            reward = rl_agent.reward(ball, miss=True)
            players_score += 1
            game_over = True
            ball.reset()
        elif ball.x + ball.size >= SCREEN_WIDTH:  # Players missed the ball
            reward = rl_agent.reward(ball, closer=True)
            ai_score += 1
            game_over = True
            ball.reset()
        elif ball_last_x > ball.x and ball.speed_x < 0:  # Ball moving toward AI
            reward = rl_agent.reward(ball, closer=True)
        
        # Determine next state
        next_state = rl_agent.get_state(ball, player1_paddle, player2_paddle)
        
        # RL agent learning (if in training mode)
        if training_mode and rl_agent.last_state is not None:
            rl_agent.learn(rl_agent.last_state, rl_agent.last_action, reward, next_state, game_over)
        
        # Update last state and action
        rl_agent.last_state = current_state
        rl_agent.last_action = action
        
        # Auto-save model periodically
        if current_time - last_save_time > auto_save_interval:
            rl_agent.save_model()
            last_save_time = current_time
            
            # Also record the episode rewards
            if rl_agent.episode_rewards != 0:
                rl_agent.total_rewards.append(rl_agent.episode_rewards)
                rl_agent.episode_rewards = 0
        
        # Draw everything
        screen.fill(BG_COLOR)
        
        # Draw center line
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        
        # Draw paddles and ball
        ai_paddle.draw(screen)
        player1_paddle.draw(screen)
        player2_paddle.draw(screen)
        ball.draw(screen)
        
        # Draw scores
        ai_score_text = font.render(str(ai_score), True, FONT_COLOR)
        players_score_text = font.render(str(players_score), True, FONT_COLOR)
        screen.blit(ai_score_text, (SCREEN_WIDTH // 4, 20))
        screen.blit(players_score_text, (3 * SCREEN_WIDTH // 4, 20))
        
        # Draw RL agent status
        status_color = RL_LEARNING_COLOR if training_mode else WHITE
        status_text = small_font.render(f"RL Agent: {'Learning' if training_mode else 'Playing'}", True, status_color)
        explore_text = small_font.render(f"Exploration: {rl_agent.exploration_rate:.4f}", True, status_color)
        hit_miss_text = small_font.render(f"Hits: {rl_agent.hit_count} Misses: {rl_agent.miss_count}", True, status_color)
        controls_text = small_font.render("T: Toggle Training | S: Save Model | R: Reset Score", True, WHITE)
        
        screen.blit(status_text, (10, SCREEN_HEIGHT - 80))
        screen.blit(explore_text, (10, SCREEN_HEIGHT - 60))
        screen.blit(hit_miss_text, (10, SCREEN_HEIGHT - 40))
        screen.blit(controls_text, (10, SCREEN_HEIGHT - 20))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Save model before exiting
    rl_agent.save_model()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()