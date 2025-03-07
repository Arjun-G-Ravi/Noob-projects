import pygame
import random
import math
from pygame.math import Vector2
from upgrades import upgrade_gun, upgrade_blob, upgrade_heavy

# Initialize Pygame
pygame.init()

# Screen setup
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Vampire Survivors Clone")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Font setup
font = pygame.font.SysFont(None, 22)
large_font = pygame.font.SysFont(None, 48)
kill_font = pygame.font.SysFont(None, 36)  # Larger font for kill count

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
items = pygame.sprite.Group()

# Screen rectangle for boundary checking
screen_rect = screen.get_rect()

# Drop probabilities
DROP_PROBABILITIES = {
    "experience": 0.6,  # 70% chance
    "health": 0.03      # 3% chance
}

### Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(screen_width / 2, screen_height / 2))
        self.pos = Vector2(self.rect.center)
        self.speed = 300
        self.health = 100
        self.experience = 0
        self.level = 1
        self.exp_to_next_level = self.level
        self.weapons = [Gun(self), BlobWeapon(self), HeavyAttack(self)]
        self.kill_count = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        velocity = Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: velocity.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: velocity.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: velocity.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: velocity.x += 1
        if velocity.length() > 0:
            velocity = velocity.normalize() * self.speed
        self.pos += velocity * dt
        self.rect.center = self.pos
        self.rect.clamp_ip(screen_rect)
        self.pos = Vector2(self.rect.center)  # Update pos to clamped position
        for weapon in self.weapons:
            weapon.update(dt)

### Enemy Classes
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_type="normal", player_level=1):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((20, 20))
        if enemy_type == "normal":
            self.image.fill(GREEN)
            self.speed = 50
            self.health = 20
            self.damage_rate = 20  # 1 damage per second
        elif enemy_type == "fast":
            self.image.fill(RED)
            self.speed = 200
            self.health = 10 + player_level
            self.damage_rate = 10  # 0.5 damage per second
        elif enemy_type == "strong":
            self.image.fill(BLUE)
            self.speed = 100
            self.health = 100 + 3 * player_level
            self.damage_rate = 30  # 2 damage per second
        elif enemy_type == "boss":
            self.image = pygame.Surface((70, 70))
            self.image.fill(YELLOW)
            self.speed = 200
            self.health = 500 + 10 * player_level
            self.damage_rate = 50  # 5 damage per second
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)

    def update(self, dt):
        diff = player.pos - self.pos
        if diff.length_squared() == 0:  # Check if positions are identical
            direction = Vector2(0, 0)
        else:
            direction = diff.normalize()
        self.pos += direction * self.speed * dt
        self.rect.center = self.pos

### Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, damage, color=RED, piercing=False):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.velocity = direction * 500
        self.damage = damage
        self.lifetime = 2.0
        self.piercing = piercing
        self.hit_enemies = set()

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        self.lifetime -= dt
        if self.lifetime <= 0 or not screen_rect.contains(self.rect):
            self.kill()

### Blob Class (Rotating Projectile)
class Blob(pygame.sprite.Sprite):
    def __init__(self, pos, damage, speed):
        super().__init__()
        self.size = 20
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.damage = damage
        self.rotation_speed = speed
        self.angle = 0
        self.distance = 100
        self.hit_enemies = set()

    def update(self, dt):
        self.angle += self.rotation_speed * dt
        self.pos = Vector2(
            player.pos.x + math.cos(self.angle) * self.distance,
            player.pos.y + math.sin(self.angle) * self.distance
        )
        self.rect.center = self.pos

### Item Classes
class ExpItem(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=pos)
        self.value = 1

class HealthItem(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=pos)
        self.value = random.randint(1,10)

### Weapon Classes
class Gun:
    def __init__(self, player):
        self.name = 'Gun'
        self.player = player
        self.level = 1
        self.damage = upgrade_gun[self.level]["damage"]
        self.cooldown = upgrade_gun[self.level]["cooldown"]
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.fire()
            self.timer = 0

    def fire(self):
        nearest_enemy = find_nearest_enemy(self.player.pos)
        if nearest_enemy:
            direction = (nearest_enemy.pos - self.player.pos).normalize()
            projectile = Projectile(self.player.pos, direction, self.damage, RED, piercing=False)
            all_sprites.add(projectile)
            projectiles.add(projectile)

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.damage = upgrade_gun[self.level]["damage"]
            self.cooldown = upgrade_gun[self.level]["cooldown"]

    def stats(self):
        return f"Gun (Lvl {self.level}/10): Dmg {self.damage}, CD {self.cooldown:.2f}s"

    def stats_next_level(self):
        if self.level < 10:
            next_level = self.level + 1
            dmg_diff = upgrade_gun[next_level]["damage"] - self.damage
            return f"Gun (Lvl {next_level}/10): Dmg {upgrade_gun[next_level]['damage']} (+{dmg_diff}), CD {upgrade_gun[next_level]['cooldown']:.2f}s"
        return f"Gun (Maxed): Dmg {self.damage}, CD {self.cooldown:.2f}s"

class BlobWeapon:
    def __init__(self, player):
        self.name = "Blob"
        self.player = player
        self.level = 1
        self.damage = upgrade_blob[self.level]["damage"]
        self.speed = upgrade_blob[self.level]["speed"]
        self.cooldown = 0.5
        self.timer = 0
        self.blob = None

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.fire()
            self.timer = 0
        if self.blob:
            self.blob.update(dt)

    def fire(self):
        if self.blob and self.blob.alive():
            self.blob.damage = self.damage
            self.blob.rotation_speed = self.speed
        else:
            self.blob = Blob(self.player.pos, self.damage, self.speed)
            all_sprites.add(self.blob)
            projectiles.add(self.blob)

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.damage = upgrade_blob[self.level]["damage"]
            self.speed = upgrade_blob[self.level]["speed"]
            self.size = upgrade_blob[self.level]["size"]
            if self.blob and self.blob.alive():
                self.blob.damage = self.damage
                self.blob.rotation_speed = self.speed
                self.blob.size = self.size
                self.blob.image = pygame.Surface((self.size, self.size))
                self.blob.image.fill(YELLOW)

    def stats(self):
        return f"Blob (Lvl {self.level}/10): Dmg {self.damage}, Spd {self.speed:.1f}"

    def stats_next_level(self):
        if self.level < 10:
            next_level = self.level + 1
            dmg_diff = upgrade_blob[next_level]["damage"] - self.damage
            spd_diff = upgrade_blob[next_level]["speed"] - self.speed
            return f"Blob (Lvl {next_level}/10): Dmg {upgrade_blob[next_level]['damage']} (+{dmg_diff}), Spd {upgrade_blob[next_level]['speed']:.1f} (+{spd_diff:.1f})"
        return f"Blob (Maxed): Dmg {self.damage}, Spd {self.speed:.1f}"

class HeavyAttack:
    def __init__(self, player):
        self.name = 'Heavy'
        self.player = player
        self.level = 1
        self.damage = upgrade_heavy[self.level]["damage"]
        self.cooldown = upgrade_heavy[self.level]["cooldown"]
        self.timer = self.cooldown
        self.num_shots = 4
        self.ready = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if not self.ready:
            self.timer += dt
            if self.timer >= self.cooldown:
                self.ready = True
                self.timer = self.cooldown
        if keys[pygame.K_SPACE] and self.ready:
            self.fire()
            self.ready = False
            self.timer = 0

    def fire(self):
        angle_step = 360 / self.num_shots
        for i in range(self.num_shots):
            angle = math.radians(i * angle_step)
            direction = Vector2(math.cos(angle), math.sin(angle)).normalize()
            projectile = Projectile(self.player.pos, direction, self.damage, BLUE, piercing=True)
            all_sprites.add(projectile)
            projectiles.add(projectile)

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.damage = upgrade_heavy[self.level]["damage"]
            self.cooldown = upgrade_heavy[self.level]["cooldown"]
            self.ready = False
            self.timer = self.cooldown
            self.num_shots = upgrade_heavy[self.level]["num_shots"]

    def stats(self):
        reload = self.cooldown - self.timer if not self.ready else 0
        return f"Heavy (Lvl {self.level}/10): Dmg {self.damage}, Rld {reload:.1f}s"

    def stats_next_level(self):
        if self.level < 10:
            next_level = self.level + 1
            dmg_diff = upgrade_heavy[next_level]["damage"] - self.damage
            reload = upgrade_heavy[next_level]["cooldown"] - self.timer if not self.ready else 0
            return f"Heavy (Lvl {next_level}/10): Dmg {upgrade_heavy[next_level]['damage']} (+{dmg_diff}), Rld {reload:.1f}s"
        reload = self.cooldown - self.timer if not self.ready else 0
        return f"Heavy (Maxed): Dmg {self.damage}, Rld {reload:.1f}s"

def find_nearest_enemy(position):
    nearest = None
    min_dist = float('inf')
    for enemy in enemies:
        dist = (enemy.pos - position).length()
        if dist < min_dist:
            min_dist = dist
            nearest = enemy
    return nearest

# Instantiate player
player = Player()
all_sprites.add(player)

# Enemy spawning setup
spawn_timer = 0
base_spawn_interval = 3

# Game state
game_state = "playing"
game_result = None

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
            if game_state == "upgrading":
                if event.key == pygame.K_1 and player.weapons[0].level < 10:
                    player.weapons[0].upgrade()
                    game_state = "playing"
                elif event.key == pygame.K_2 and player.weapons[1].level < 10:
                    player.weapons[1].upgrade()
                    game_state = "playing"
                elif event.key == pygame.K_3 and player.weapons[2].level < 10:
                    player.weapons[2].upgrade()
                    game_state = "playing"
                elif event.key == pygame.K_4 or event.key == pygame.K_SPACE:
                    player.health = min(100, player.health + 25)  # Add 25 health, cap at 100
                    game_state = "playing"
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "upgrading":
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(upgrade_rects):
                if rect.collidepoint(mouse_pos):
                    if i < 3 and player.weapons[i].level < 10:
                        player.weapons[i].upgrade()
                        game_state = "playing"
                    elif i == 3:  # Health upgrade option
                        player.health = min(100, player.health + 25)  # Add 25 health, cap at 100
                        game_state = "playing"
                    break

    # Update game logic only when playing
    if game_state == "playing":
        all_sprites.update(dt)

        # Dynamic spawn interval based on player level
        spawn_interval = max(0.5, base_spawn_interval - 0.5 * (player.level - 1))
        spawn_timer += dt
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                pos = (random.randint(0, screen_width), -20)
            elif side == 'bottom':
                pos = (random.randint(0, screen_width), screen_height + 20)
            elif side == 'left':
                pos = (-20, random.randint(0, screen_height))
            else:
                pos = (screen_width + 20, random.randint(0, screen_height))
            if player.level < 5: enemy_type = random.choices(["normal", "fast", "strong"], weights=[95, 5, 0], k=1)[0] # 0 - 5
            elif player.level < 10: enemy_type = random.choices(["normal", "fast", "strong"], weights=[60, 20, 20], k=1)[0] # 5 - 10
            elif player.level < 15: enemy_type = random.choices(["normal", "fast", "strong"], weights=[40, 20, 40], k=1)[0] # 10 - 15
            elif player.level < 20: enemy_type = random.choices(["normal", "fast", "strong"], weights=[0, 80, 20], k=1)[0] # 15 - 20
            elif player.level < 25: enemy_type = random.choices(["normal", "fast", "strong"], weights=[0, 50, 50], k=1)[0] # 25 - 30
            elif player.level < 30: enemy_type = random.choices(["normal", "fast", "strong"], weights=[0, 90, 10], k=1)[0] # 35- 40
            else: enemy_type = random.choices(["normal", "fast", "strong"], weights=[0, 50, 50], k=1)[0]
            enemy = Enemy(pos, enemy_type, player.level)
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Collision detection
        for projectile in projectiles:
            if isinstance(projectile, Blob):
                hits = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in hits:
                    if enemy not in projectile.hit_enemies:
                        enemy.health -= projectile.damage
                        projectile.hit_enemies.add(enemy)
                        if enemy.health <= 0:
                            enemy.kill()
                            drop = random.choices(["experience", "health"], 
                                                  weights=[DROP_PROBABILITIES["experience"], 
                                                           DROP_PROBABILITIES["health"]], 
                                                  k=1)[0]
                            if drop == "experience":
                                item = ExpItem(enemy.rect.center)
                            else:
                                item = HealthItem(enemy.rect.center)
                            all_sprites.add(item)
                            items.add(item)
                            player.kill_count += 1
                            if player.kill_count in [100, 200, 300, 400, 401]:
                                side = random.choice(['top', 'bottom', 'left', 'right'])
                                if side == 'top':
                                    pos = (random.randint(0, screen_width), -50)
                                elif side == 'bottom':
                                    pos = (random.randint(0, screen_width), screen_height + 50)
                                elif side == 'left':
                                    pos = (-50, random.randint(0, screen_height))
                                else:
                                    pos = (screen_width + 50, random.randint(0, screen_height))
                                boss = Enemy(pos, "boss", player.level)
                                all_sprites.add(boss)
                                enemies.add(boss)
                if projectile.angle >= 2 * math.pi:
                    projectile.hit_enemies.clear()
                    projectile.angle -= 2 * math.pi
            else:
                hits = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in hits:
                    if enemy not in projectile.hit_enemies:
                        enemy.health -= projectile.damage
                        projectile.hit_enemies.add(enemy)
                        if not projectile.piercing:
                            projectile.kill()
                        if enemy.health <= 0:
                            enemy.kill()
                            drop = random.choices(["experience", "health"], 
                                                  weights=[DROP_PROBABILITIES["experience"], 
                                                           DROP_PROBABILITIES["health"]], 
                                                  k=1)[0]
                            if drop == "experience":
                                item = ExpItem(enemy.rect.center)
                            else:
                                item = HealthItem(enemy.rect.center)
                            all_sprites.add(item)
                            items.add(item)
                            player.kill_count += 1
                            if player.kill_count in [100, 200, 300, 401]:
                                side = random.choice(['top', 'bottom', 'left', 'right'])
                                if side == 'top':
                                    pos = (random.randint(0, screen_width), -50)
                                elif side == 'bottom':
                                    pos = (random.randint(0, screen_width), screen_height + 50)
                                elif side == 'left':
                                    pos = (-50, random.randint(0, screen_height))
                                else:
                                    pos = (screen_width + 50, random.randint(0, screen_height))
                                boss = Enemy(pos, "boss", player.level)
                                all_sprites.add(boss)
                                enemies.add(boss)
                        break

        # Player vs Items
        for item in items:
            if (player.pos - Vector2(item.rect.center)).length() < 50:
                if isinstance(item, ExpItem):
                    player.experience += item.value
                    if player.experience >= player.exp_to_next_level:
                        player.level += 1
                        player.experience -= player.exp_to_next_level
                        player.exp_to_next_level = player.level
                        game_state = "upgrading"
                elif isinstance(item, HealthItem):
                    player.health = min(100, player.health + item.value)
                item.kill()

        # Player vs Enemies
        colliding_enemies = pygame.sprite.spritecollide(player, enemies, False)
        if colliding_enemies:
            total_damage_rate = sum(enemy.damage_rate for enemy in colliding_enemies)
            damage = total_damage_rate * dt
            player.health -= damage

        # Check game over conditions
        if player.kill_count >= 500:
            game_state = "end"
            game_result = "win"
        elif player.health <= 0:
            game_state = "end"
            game_result = "loss"

    # Drawing
    if game_state in ["playing", "upgrading"]:
        screen.fill(BLACK)
        all_sprites.draw(screen)

    if game_state == "upgrading":
        upgrade_rects = []
        # pygame.draw.rect(screen, GRAY, (100, 200, 600, 200))
        pygame.draw.rect(screen, GRAY, (50, 150, 700, 300))  # Larger box
        title_text = font.render("Level Up! Choose an upgrade:", True, WHITE)
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 220))

        # Calculate layout for 4 options (3 weapons + health)
        button_width = 140  # Reduced width to fit 4 options
        total_width = button_width * 4 + 20 * 3  # 4 buttons, 3 gaps
        start_x = (screen_width - total_width) // 2
        
        # Weapon upgrades
        for i, weapon in enumerate(player.weapons):
            x = start_x + i * (button_width + 20)
            if weapon.level >= 10:
                upgrade_text = font.render(f"{weapon.stats()} - MAXED OUT", True, WHITE)
                text_rect = upgrade_text.get_rect(center=(x + button_width//2, 320))
                button_rect = pygame.Rect(x, 280, button_width, 80)
                pygame.draw.rect(screen, GRAY, button_rect)
                screen.blit(upgrade_text, text_rect)
            else:
                upgrade_text1 = font.render(f"{weapon.name}: Lv {weapon.level}", True, WHITE)
                upgrade_text2 = font.render(f"Damage: {weapon.damage}", True, WHITE)
                upgrade_text3 = font.render(f"Cooldown: {weapon.cooldown}", True, WHITE)
                text_rect1 = upgrade_text1.get_rect(center=(x + button_width//2, 300-5))
                text_rect2 = upgrade_text2.get_rect(center=(x + button_width//2, 325-5))
                text_rect3 = upgrade_text3.get_rect(center=(x + button_width//2, 350-5))
                button_rect = pygame.Rect(x, 280, button_width, 80)
                upgrade_rects.append(button_rect)
                pygame.draw.rect(screen, LIGHT_GRAY, button_rect)
                screen.blit(upgrade_text1, text_rect1)
                screen.blit(upgrade_text2, text_rect2)
                screen.blit(upgrade_text3, text_rect3)

        # Health upgrade option (always available)
        x = start_x + 3 * (button_width + 20)
        health_text1 = font.render("Health", True, WHITE)
        health_text2 = font.render("+25", True, WHITE)
        text_rect1 = health_text1.get_rect(center=(x + button_width//2, 310))
        text_rect2 = health_text2.get_rect(center=(x + button_width//2, 340))
        button_rect = pygame.Rect(x, 280, button_width, 80)
        upgrade_rects.append(button_rect)
        pygame.draw.rect(screen, LIGHT_GRAY, button_rect)
        screen.blit(health_text1, text_rect1)
        screen.blit(health_text2, text_rect2)

    elif game_state == "end":
        screen.fill(GRAY)
        if game_result == "win":
            end_text = large_font.render("You Won!", True, WHITE)
        else:
            end_text = large_font.render("You Lost!", True, WHITE)
        screen.blit(end_text, (screen_width // 2 - end_text.get_width() // 2, screen_height // 2 - 100))
        stats_text = font.render(f"Level: {player.level}  Kills: {player.kill_count}", True, WHITE)
        screen.blit(stats_text, (screen_width // 2 - stats_text.get_width() // 2, screen_height // 2))
        quit_text = font.render("Press Q to quit", True, WHITE)
        screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, screen_height // 2 + 50))

    if game_state in ["playing", "upgrading"]:
        # UI: Top-left - Health bar and text
        health_bar_width = 150
        health_bar_height = 10
        health_ratio = max(0, player.health / 100)  # Health is 0 to 100, ratio 0 to 1
        pygame.draw.rect(screen, RED, (5, 5, health_bar_width, health_bar_height))  # Background
        pygame.draw.rect(screen, GREEN, (5, 5, health_bar_width * health_ratio, health_bar_height))  # Foreground
        health_text = font.render(f"Health: {int(max(0, player.health))}", True, WHITE)
        screen.blit(health_text, (160, 5))  # Next to the bar
        
        # Level text
        level_text = font.render(f"Level: {player.level}", True, WHITE)
        screen.blit(level_text, (5, 25))  # Below health bar
        
        # Experience bar
        exp_ratio = player.experience / player.exp_to_next_level if player.exp_to_next_level > 0 else 0
        pygame.draw.rect(screen, BLUE, (5, 40, 150 * exp_ratio, 10))  # Adjusted position

        # UI: Top-center - Kill Count with larger font
        kill_text = kill_font.render(f"Kills: {player.kill_count}", True, WHITE)
        screen.blit(kill_text, (screen_width // 2 - kill_text.get_width() // 2, 5))

        # UI: Top-right - Weapon Stats
        for i, weapon in enumerate(player.weapons):
            if weapon.name == 'Heavy':
                color = WHITE if weapon.ready else RED
            else:
                color = WHITE
            stat_text = font.render(weapon.stats(), True, color)
            screen.blit(stat_text, (screen_width - 250, 10 + i * 30))

    pygame.display.flip()

pygame.quit()