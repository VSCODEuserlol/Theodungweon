import pygame
import math
import random
import json

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors (Devil theme)
BLACK = (10, 10, 10)
DARK_RED = (40, 0, 0)
RED = (200, 50, 50)
BRIGHT_RED = (255, 100, 100)
WHITE = (255, 255, 255)
PURPLE = (100, 50, 150)
ORANGE = (255, 150, 50)
DARK_PURPLE = (50, 25, 75)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vel = 5
        self.health = 100
        self.max_health = 100
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        
        # Weapons
        self.weapon = "pistol"
        self.damage = 25
        self.fire_rate = 300  # milliseconds
        self.last_shot = 0
        self.ammo = float('inf')
        
        # Abilities
        self.abilities = {
            "double_shot": False,
            "rapid_fire": False,
            "health_regen": False,
            "damage_boost": False,
            "shield": False
        }
        
        self.shield_active = False
        self.shield_time = 0
        
    def move(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.vel
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.vel
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.vel
            
        # Keep player on screen
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
    
    def shoot(self, mouse_pos, bullets):
        current_time = pygame.time.get_ticks()
        fire_delay = self.fire_rate
        
        if self.abilities["rapid_fire"]:
            fire_delay //= 2
            
        if current_time - self.last_shot > fire_delay:
            # Calculate direction to mouse
            dx = mouse_pos[0] - (self.x + self.width//2)
            dy = mouse_pos[1] - (self.y + self.height//2)
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Normalize direction
                dx /= distance
                dy /= distance
                
                # Create bullet(s)
                damage = self.damage
                if self.abilities["damage_boost"]:
                    damage = int(damage * 1.5)
                
                bullet = Bullet(self.x + self.width//2, self.y + self.height//2, dx, dy, damage)
                bullets.append(bullet)
                
                # Double shot ability
                if self.abilities["double_shot"]:
                    # Add slight angle offset for second bullet
                    angle_offset = 0.3
                    dx2 = dx * math.cos(angle_offset) - dy * math.sin(angle_offset)
                    dy2 = dx * math.sin(angle_offset) + dy * math.cos(angle_offset)
                    bullet2 = Bullet(self.x + self.width//2, self.y + self.height//2, dx2, dy2, damage)
                    bullets.append(bullet2)
                
                self.last_shot = current_time
    
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp = 0
        self.xp_to_next = int(self.xp_to_next * 1.2)
        
        # Increase stats
        self.max_health += 20
        self.health = self.max_health
        self.damage += 5
        
        # Unlock abilities at certain levels
        if self.level == 2:
            self.abilities["double_shot"] = True
            return "Double Shot Unlocked!"
        elif self.level == 3:
            self.abilities["rapid_fire"] = True
            return "Rapid Fire Unlocked!"
        elif self.level == 4:
            self.abilities["health_regen"] = True
            return "Health Regeneration Unlocked!"
        elif self.level == 5:
            self.abilities["damage_boost"] = True
            return "Damage Boost Unlocked!"
        elif self.level == 6:
            self.abilities["shield"] = True
            return "Shield Ability Unlocked! (Press SPACE)"
        
        return f"Level {self.level} Reached!"
    
    def activate_shield(self):
        if self.abilities["shield"] and not self.shield_active:
            self.shield_active = True
            self.shield_time = pygame.time.get_ticks()
    
    def update(self):
        # Health regeneration
        if self.abilities["health_regen"] and self.health < self.max_health:
            if pygame.time.get_ticks() % 1000 < 17:  # Roughly every second
                self.health = min(self.max_health, self.health + 1)
        
        # Shield duration
        if self.shield_active:
            if pygame.time.get_ticks() - self.shield_time > 3000:  # 3 seconds
                self.shield_active = False
    
    def draw(self, screen):
        # Player body (devil-like)
        color = BRIGHT_RED if self.shield_active else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Devil horns
        horn_size = 8
        pygame.draw.polygon(screen, DARK_RED, [
            (self.x + 5, self.y),
            (self.x + 5, self.y - horn_size),
            (self.x + 10, self.y)
        ])
        pygame.draw.polygon(screen, DARK_RED, [
            (self.x + self.width - 10, self.y),
            (self.x + self.width - 5, self.y - horn_size),
            (self.x + self.width - 5, self.y)
        ])
        
        # Eyes
        pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 10), 3)
        pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 10), 3)
        pygame.draw.circle(screen, RED, (self.x + 8, self.y + 10), 1)
        pygame.draw.circle(screen, RED, (self.x + 22, self.y + 10), 1)
        
        # Shield effect
        if self.shield_active:
            pygame.draw.circle(screen, PURPLE, 
                             (self.x + self.width//2, self.y + self.height//2), 
                             self.width, 3)

class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.type = enemy_type
        
        if enemy_type == "basic":
            self.width = 25
            self.height = 25
            self.health = 50
            self.damage = 10
            self.vel = 1.5
            self.xp_value = 15
            self.color = ORANGE
        elif enemy_type == "fast":
            self.width = 20
            self.height = 20
            self.health = 30
            self.damage = 15
            self.vel = 3
            self.xp_value = 25
            self.color = BRIGHT_RED
        elif enemy_type == "tank":
            self.width = 35
            self.height = 35
            self.health = 150
            self.damage = 25
            self.vel = 0.8
            self.xp_value = 50
            self.color = DARK_RED
        
        self.max_health = self.health
    
    def move_toward_player(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.x += (dx / distance) * self.vel
            self.y += (dy / distance) * self.vel
    
    def draw(self, screen):
        # Enemy body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Health bar
        bar_width = self.width
        bar_height = 4
        health_percentage = self.health / self.max_health
        
        pygame.draw.rect(screen, RED, 
                        (self.x, self.y - 8, bar_width, bar_height))
        pygame.draw.rect(screen, WHITE, 
                        (self.x, self.y - 8, bar_width * health_percentage, bar_height))
        
        # Enemy details based on type
        if self.type == "fast":
            # Draw spikes
            pygame.draw.polygon(screen, WHITE, [
                (self.x + self.width//2, self.y - 5),
                (self.x + self.width//2 - 3, self.y),
                (self.x + self.width//2 + 3, self.y)
            ])
        elif self.type == "tank":
            # Draw armor plates
            pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, 10, 10))
            pygame.draw.rect(screen, BLACK, (self.x + 20, self.y + 5, 10, 10))
            pygame.draw.rect(screen, BLACK, (self.x + 12, self.y + 20, 10, 10))

class Bullet:
    def __init__(self, x, y, dx, dy, damage):
        self.x = x
        self.y = y
        self.dx = dx * 8  # Bullet speed
        self.dy = dy * 8
        self.damage = damage
        self.size = 4
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
    
    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def draw(self, screen):
        pygame.draw.circle(screen, BRIGHT_RED, (int(self.x), int(self.y)), self.size)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Devil's Arsenal")
        self.clock = pygame.time.Clock()
        
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.enemies = []
        self.bullets = []
        
        self.wave = 1
        self.enemies_killed = 0
        self.score = 0
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.level_up_message = ""
        self.level_up_time = 0
        
        # Spawn first wave
        self.spawn_wave()
    
    def spawn_wave(self):
        enemies_to_spawn = 3 + self.wave * 2
        
        for _ in range(enemies_to_spawn):
            # Random spawn from edges
            side = random.randint(0, 3)
            if side == 0:  # Top
                x, y = random.randint(0, SCREEN_WIDTH), -30
            elif side == 1:  # Right
                x, y = SCREEN_WIDTH + 30, random.randint(0, SCREEN_HEIGHT)
            elif side == 2:  # Bottom
                x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
            else:  # Left
                x, y = -30, random.randint(0, SCREEN_HEIGHT)
            
            # Choose enemy type based on wave
            if self.wave >= 5 and random.random() < 0.2:
                enemy_type = "tank"
            elif self.wave >= 3 and random.random() < 0.3:
                enemy_type = "fast"
            else:
                enemy_type = "basic"
            
            self.enemies.append(Enemy(x, y, enemy_type))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.activate_shield()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    self.player.shoot(mouse_pos, self.bullets)
        
        # Continuous shooting while holding mouse button
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            self.player.shoot(mouse_pos, self.bullets)
        
        return True
    
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.update()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.move_toward_player(self.player)
        
        # Check bullet-enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (abs(bullet.x - (enemy.x + enemy.width//2)) < enemy.width//2 and
                    abs(bullet.y - (enemy.y + enemy.height//2)) < enemy.height//2):
                    
                    enemy.health -= bullet.damage
                    self.bullets.remove(bullet)
                    
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.enemies_killed += 1
                        self.score += enemy.xp_value
                        
                        # Gain XP and check for level up
                        level_up_msg = self.player.gain_xp(enemy.xp_value)
                        if level_up_msg:
                            self.level_up_message = level_up_msg
                            self.level_up_time = pygame.time.get_ticks()
                    break
        
        # Check enemy-player collisions
        for enemy in self.enemies[:]:
            if (abs((enemy.x + enemy.width//2) - (self.player.x + self.player.width//2)) < 
                (enemy.width + self.player.width)//2 and
                abs((enemy.y + enemy.height//2) - (self.player.y + self.player.height//2)) < 
                (enemy.height + self.player.height)//2):
                
                if not self.player.shield_active:
                    self.player.health -= enemy.damage
                    # Push enemy away slightly
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance > 0:
                        enemy.x += (dx / distance) * 20
                        enemy.y += (dy / distance) * 20
        
        # Check for next wave
        if not self.enemies:
            self.wave += 1
            self.spawn_wave()
    
    def draw(self):
        # Background
        self.screen.fill(BLACK)
        
        # Draw grid pattern for atmosphere
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))
        
        # Draw game objects
        self.player.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        # Level up notification
        if self.level_up_message and pygame.time.get_ticks() - self.level_up_time < 3000:
            text = self.font.render(self.level_up_message, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            pygame.draw.rect(self.screen, (100, 0, 0), rect.inflate(20, 10))
            pygame.draw.rect(self.screen, WHITE, rect.inflate(20, 10), 2)
            self.screen.blit(text, rect)
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Health bar
        bar_width = 200
        bar_height = 20
        health_percentage = self.player.health / self.player.max_health
        
        pygame.draw.rect(self.screen, DARK_RED, (10, 10, bar_width, bar_height))
        pygame.draw.rect(self.screen, RED, (10, 10, bar_width * health_percentage, bar_height))
        pygame.draw.rect(self.screen, WHITE, (10, 10, bar_width, bar_height), 2)
        
        # Health text
        health_text = self.small_font.render(f"HP: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (15, 13))
        
        # XP bar
        xp_percentage = self.player.xp / self.player.xp_to_next
        pygame.draw.rect(self.screen, DARK_PURPLE, (10, 35, bar_width, 15))
        pygame.draw.rect(self.screen, PURPLE, (10, 35, bar_width * xp_percentage, 15))
        pygame.draw.rect(self.screen, WHITE, (10, 35, bar_width, 15), 2)
        
        # Level and stats
        level_text = self.font.render(f"Level {self.player.level}", True, WHITE)
        self.screen.blit(level_text, (10, 55))
        
        wave_text = self.small_font.render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (10, 85))
        
        kills_text = self.small_font.render(f"Kills: {self.enemies_killed}", True, WHITE)
        self.screen.blit(kills_text, (10, 105))
        
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 125))
        
        # Abilities
        y_offset = 10
        abilities_text = self.small_font.render("Abilities:", True, WHITE)
        self.screen.blit(abilities_text, (SCREEN_WIDTH - 150, y_offset))
        y_offset += 25
        
        for ability, unlocked in self.player.abilities.items():
            if unlocked:
                color = BRIGHT_RED if ability == "shield" and self.player.shield_active else WHITE
                text = self.small_font.render(f"✓ {ability.replace('_', ' ').title()}", True, color)
                self.screen.blit(text, (SCREEN_WIDTH - 150, y_offset))
                y_offset += 20
        
        # Controls
        controls = [
            "WASD/Arrows: Move",
            "Mouse: Aim & Shoot",
            "Space: Shield (if unlocked)"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, (150, 150, 150))
            self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 20))
    
    def run(self):
        running = True
        while running and self.player.health > 0:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Game over screen
        if self.player.health <= 0:
            game_over_text = self.font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            final_level_text = self.font.render(f"Reached Level: {self.player.level}", True, WHITE)
            
            self.screen.fill(BLACK)
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(final_level_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 20))
            
            pygame.display.flip()
            pygame.time.wait(3000)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
