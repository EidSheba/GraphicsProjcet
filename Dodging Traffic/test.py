import pygame
import sys
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Frame rate
FPS = 60
clock = pygame.time.Clock()

# Set up the OpenGL display
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
glClearColor(1.0, 1.0, 1.0, 1.0)  # White background
glEnable(GL_TEXTURE_2D)  # Enable texture mapping
glEnable(GL_BLEND)  # Enable alpha blending
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Set up orthographic projection (0,0 at bottom-left)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)  # Bottom-left origin
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()

# Load images and convert to OpenGL textures
def load_image(path, width=None, height=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if width and height:
            image = pygame.transform.scale(image, (width, height))
        # Convert to texture
        data = pygame.image.tostring(image, "RGBA", 1)
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        return tex_id, image.get_width(), image.get_height()
    except Exception as e:
        print(f"Error loading image: {path}. {e}")
        return None, 50, 50

# Load sounds
def load_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except Exception as e:
        print(f"Error loading sound: {path}. {e}")
        return None

click_sound = load_sound("click.wav")
background_music = load_sound("background.wav")
victory_sound = load_sound("victory.wav")
collision_sound = load_sound("crash.wav")
coin_sound = load_sound("coin_collect.wav")

# Load game assets
background_tex, _, _ = load_image("background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
cloud1_tex, cloud1_w, cloud1_h = load_image("cloud.png", 200, 75)
cloud2_tex, cloud2_w, cloud2_h = load_image("cloud2.png", 175, 65)
level1_btn_tex, btn_w, btn_h = load_image("level1.png", 200, 50)
level2_btn_tex, _, _ = load_image("level2.png", 200, 50)
level3_btn_tex, _, _ = load_image("level3.png", 200, 50)
play_btn_tex, _, _ = load_image("play.png", 200, 50)
player_tex, player_w, player_h = load_image("player2.png", 100, 120)
enemy_tex, enemy_w, enemy_h = load_image("enemy4.png", 110, 125)
same_dir_enemy_tex, same_dir_w, same_dir_h = load_image("Enemy8.png", 110, 125)
rock_tex, rock_w, rock_h = load_image("Rock.png", 60, 70)
street_tex, _, _ = load_image("AnimatedStreet.png", SCREEN_WIDTH, SCREEN_HEIGHT)
finishing_line_tex, _, _ = load_image("FinishingLine.png", SCREEN_WIDTH, 30)
lose_tex, _, _ = load_image("game_over_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
win_tex, _, _ = load_image("you_win_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
coin_tex, coin_w, coin_h = load_image("coin.png", 70, 70)

# Fonts
font = pygame.font.SysFont("Arial", 30)
large_font = pygame.font.SysFont("Arial", 40)

# Render text to texture
def text_to_texture(text, font, color):
    text_surface = font.render(text, True, color)
    data = pygame.image.tostring(text_surface, "RGBA", 1)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(),
                 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    return tex_id, text_surface.get_width(), text_surface.get_height()

# Draw textured quad
def draw_quad(tex_id, x, y, w, h):
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()

# Game states
selected_level = None
message = ""

# Start screen
def start_screen():
    global selected_level, message
    cloud1_x = SCREEN_WIDTH
    cloud2_x = -cloud2_w
    cloud1_y = int(SCREEN_HEIGHT * 0.1)
    cloud2_y = int(SCREEN_HEIGHT * 0.2)

    button_surfaces = [level1_btn_tex, level2_btn_tex, level3_btn_tex, play_btn_tex]
    btn_width = 200
    btn_height = 50
    x_pos = (SCREEN_WIDTH - btn_width) // 2
    gap = 20
    start_y = SCREEN_HEIGHT - 200
    y_positions = [start_y - i * (btn_height + gap) for i in range(4)]

    running = True
    while running:
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw background
        draw_quad(background_tex, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Move and draw clouds
        cloud1_x -= 1
        if cloud1_x < -cloud1_w:
            cloud1_x = SCREEN_WIDTH
        cloud2_x += 1
        if cloud2_x > SCREEN_WIDTH:
            cloud2_x = -cloud2_w
        draw_quad(cloud1_tex, cloud1_x, cloud1_y, cloud1_w, cloud1_h)
        draw_quad(cloud2_tex, cloud2_x, cloud2_y, cloud2_w, cloud2_h)

        # Draw buttons
        button_rects = []
        for i, y in enumerate(y_positions):
            rect = pygame.Rect(x_pos, SCREEN_HEIGHT - y - btn_height, btn_width, btn_height)  # Flip y for OpenGL
            draw_quad(button_surfaces[i], x_pos, y, btn_width, btn_height)
            button_rects.append(rect)

        # Draw message
        if message:
            msg_tex, msg_w, msg_h = text_to_texture(message, font, BLACK)
            draw_quad(msg_tex, 20, SCREEN_HEIGHT - 500 - msg_h, msg_w, msg_h)
            glDeleteTextures([msg_tex])

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mx, my):
                        if i < 3:
                            selected_level = i + 1
                            message = f"Level {selected_level} selected"
                            if click_sound:
                                click_sound.play()
                        else:
                            if selected_level is None:
                                message = "Choose level first"
                            else:
                                return "game"
                        break

        clock.tick(FPS)
    return "start"

def pause_screen():
    pygame.mixer.music.pause()
    paused = True
    while paused:
        glClear(GL_COLOR_BUFFER_BIT)
        pause_tex, pause_w, pause_h = text_to_texture("Paused", large_font, WHITE)
        resume_tex, resume_w, resume_h = text_to_texture("Press ESC to Resume", font, WHITE)
        draw_quad(pause_tex, SCREEN_WIDTH // 2 - pause_w // 2, SCREEN_HEIGHT // 3, pause_w, pause_h)
        draw_quad(resume_tex, SCREEN_WIDTH // 2 - resume_w // 2, SCREEN_HEIGHT // 2, resume_w, resume_h)
        glDeleteTextures([pause_tex, resume_tex])
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
                pygame.mixer.music.unpause()

        clock.tick(FPS)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_tex  # Store texture ID
        self.width, self.height = player_w, player_h
        self.rect = pygame.Rect(0, 0, player_w, player_h)
        self.rect.inflate_ip(-player_w // 2, -player_h // 4)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 85)

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)

    def draw(self):
        draw_quad(self.image, self.rect.left, SCREEN_HEIGHT - self.rect.bottom, self.width, self.height)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, tex_id, width, height, speed):
        super().__init__()
        self.image = tex_id
        self.width, self.height = width, height
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.inflate_ip(-width // 2, -height // 4)
        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -50)
        self.base_speed = speed
        self.speed = speed

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw(self):
        draw_quad(self.image, self.rect.left, SCREEN_HEIGHT - self.rect.bottom, self.width, self.height)

class SameDirectionEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = same_dir_enemy_tex
        self.width, self.height = same_dir_w, same_dir_h
        self.rect = pygame.Rect(0, 0, same_dir_w, same_dir_h)
        self.rect.inflate_ip(-same_dir_w // 2, -same_dir_h // 4)
        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -100)

    def update(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw(self):
        draw_quad(self.image, self.rect.left, SCREEN_HEIGHT - self.rect.bottom, self.width, self.height)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_tex
        self.width, self.height = coin_w, coin_h
        self.rect = pygame.Rect(0, 0, coin_w, coin_h)
        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -40)

    def update(self):
        self.rect.move_ip(0, 5)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def draw(self):
        draw_quad(self.image, self.rect.left, SCREEN_HEIGHT - self.rect.bottom, self.width, self.height)

def check_collision(player, enemies):
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            return True
    return False

def game_loop(level):
    global selected_level
    player = Player()
    player_group = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    same_direction_enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    street_y = 0
    base_speed = 5 + (level - 1) * 2
    score = 0
    start_time = None
    enemy_timer = time.time()
    same_dir_timer = time.time()
    coin_timer = time.time()
    finishing_line_y = -30
    finishing_line_reached = False

    running = True
    while running:
        glClear(GL_COLOR_BUFFER_BIT)

        keys = pygame.key.get_pressed()
        street_speed = base_speed + (4 if keys[pygame.K_UP] else 0)

        street_y += street_speed
        if street_y >= SCREEN_HEIGHT:
            street_y = 0

        draw_quad(street_tex, 0, SCREEN_HEIGHT - street_y, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_quad(street_tex, 0, SCREEN_HEIGHT - street_y - SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

        now = time.time()
        if now - coin_timer >= 2:
            coins.add(Coin())
            coin_timer = now

        enemy_spawn_interval = 3 - (level * 0.5)
        if now - enemy_timer >= enemy_spawn_interval:
            if level == 1:
                pass
            elif level == 2:
                img = random.choice([(same_dir_enemy_tex, same_dir_w, same_dir_h), (rock_tex, rock_w, rock_h)])
                enemies.add(Enemy(img[0], img[1], img[2], base_speed))
            elif level == 3:
                img = random.choice([(enemy_tex, enemy_w, enemy_h), (rock_tex, rock_w, rock_h)])
                enemies.add(Enemy(img[0], img[1], img[2], street_speed))
            enemy_timer = now

        if level >= 1 and now - same_dir_timer >= 5:
            same_direction_enemies.add(SameDirectionEnemy())
            same_dir_timer = now

        coins.update()
        enemies.update()
        for e in same_direction_enemies:
            e.update(base_speed)

        for coin in coins:
            coin.draw()
        for enemy in enemies:
            enemy.draw()
        for e in same_direction_enemies:
            e.draw()

        player.update(keys)
        player.draw()

        for coin in pygame.sprite.spritecollide(player, coins, True):
            score += 1
            if coin_sound:
                coin_sound.play()

        score_tex, score_w, score_h = text_to_texture(f"Score: {score}", font, BLACK)
        draw_quad(score_tex, 10, SCREEN_HEIGHT - 17 - score_h, score_w, score_h)
        glDeleteTextures([score_tex])

        if check_collision(player, enemies) or check_collision(player, same_direction_enemies):
            if collision_sound:
                collision_sound.play()
            pygame.mixer.music.stop()
            return "game_over"

        if start_time is None and keys[pygame.K_UP]:
            start_time = time.time()

        if start_time and now - start_time >= 60:
            if finishing_line_y < SCREEN_HEIGHT - 30:
                finishing_line_y += 2
            else:
                finishing_line_reached = True
            draw_quad(finishing_line_tex, 0, SCREEN_HEIGHT - finishing_line_y - 30, SCREEN_WIDTH, 30)
            if finishing_line_reached and player.rect.top < finishing_line_y + 30:
                if victory_sound:
                    victory_sound.play()
                pygame.mixer.music.stop()
                selected_level = None
                return "level_complete"

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_screen()

        clock.tick(FPS)
    return "game"

def game_over_screen():
    while True:
        glClear(GL_COLOR_BUFFER_BIT)
        draw_quad(lose_tex, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        text2_tex, text2_w, text2_h = text_to_texture("Press SPACE to return to Start", large_font, WHITE)
        draw_quad(text2_tex, SCREEN_WIDTH // 2 - text2_w // 2, SCREEN_HEIGHT // 2 + 100, text2_w, text2_h)
        glDeleteTextures([text2_tex])
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return "start"

        clock.tick(FPS)

def level_complete_screen(level):
    while True:
        glClear(GL_COLOR_BUFFER_BIT)
        draw_quad(win_tex, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        text2_tex, text2_w, text2_h = text_to_texture("Press SPACE to return to Start", large_font, WHITE)
        draw_quad(text2_tex, SCREEN_WIDTH // 2 - text2_w // 2, SCREEN_HEIGHT // 2 + 120, text2_w, text2_h)
        glDeleteTextures([text2_tex])
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return "start"

        clock.tick(FPS)

# Main loop
def main():
    global selected_level
    if background_music:
        pygame.mixer.music.load("background.wav")
        pygame.mixer.music.play(-1, 0.0)
    state = "start"
    while True:
        if state == "start":
            state = start_screen()
        elif state == "game":
            state = game_loop(selected_level)
        elif state == "game_over":
            state = game_over_screen()
        elif state == "level_complete":
            state = level_complete_screen(selected_level)

if __name__ == "__main__":
    main()