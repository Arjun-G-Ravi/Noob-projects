import pygame
import random
import sys

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

# Game objects dimensions
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15
PADDLE_SPEED = 5
AI_PADDLE_SPEED = 5
BALL_SPEED_X = 8
BALL_SPEED_Y = 7

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
        self.speed = PADDLE_SPEED if not is_ai else AI_PADDLE_SPEED
    
    def update(self, direction=0, ball=None):
        if self.is_ai and ball:
            # Simple AI: follow the ball
            if self.y + self.height/2 < ball.y and self.y + self.height < SCREEN_HEIGHT:
                self.y += self.speed
            elif self.y + self.height/2 > ball.y and self.y > 0:
                self.y -= self.speed
        else:
            # Human control
            if direction == 1 and self.y > 0:
                self.y -= self.speed
            elif direction == -1 and self.y + self.height < SCREEN_HEIGHT:
                self.y += self.speed
        
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, PADDLE_COLOR, self.rect)

def main():
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong Game - One AI vs Two Players")
    
    # Create game clock
    clock = pygame.time.Clock()
    
    # Create font for score display
    font = pygame.font.Font(None, 36)
    
    # Create game objects
    ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE)
    
    # Left paddle (AI)
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
    
    # Scores
    ai_score = 0
    players_score = 0
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
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
        
        # Update game objects
        ball.update()
        ai_paddle.update(ball=ball)  # AI follows the ball
        player1_paddle.update(player1_direction)
        player2_paddle.update(player2_direction)
        
        # Check for ball collision with paddles
        if ball.rect.colliderect(ai_paddle.rect):
            ball.speed_x *= -1
            ball.x = ai_paddle.x + ai_paddle.width  # Prevent getting stuck
        
        if ball.rect.colliderect(player1_paddle.rect) or ball.rect.colliderect(player2_paddle.rect):
            ball.speed_x *= -1
            ball.x = player1_paddle.x - ball.size  # Prevent getting stuck
        
        # Check for scoring
        if ball.x <= 0:
            players_score += 1
            ball.reset()
        elif ball.x + ball.size >= SCREEN_WIDTH:
            ai_score += 1
            ball.reset()
        
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
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()