import pygame
import sys
import random
import time

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


def load_image(path, width=None, height=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if width and height:
            image = pygame.transform.scale(image, (width, height))
        return image
    except Exception as e:
        print(f"Error loading image: {path}. {e}")
        return pygame.Surface((width or 50, height or 50))


def load_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except Exception as e:
        print(f"Error loading sound: {path}. {e}")
        return None


class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-55, -20)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 85)
        self.boosting = False

    def update(self, keys):
        speed = 5
        if keys[pygame.K_UP]:
            speed = 9
            self.boosting = True
        else:
            self.boosting = False
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-speed, 0)
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(speed, 0)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-55, -20)
        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -50)
        self.speed = speed

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class SameDirectionEnemy(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-55, -20)
        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -100)

    def update(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -40)

    def update(self):
        self.rect.move_ip(0, 5)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Button:
    def __init__(self, image, x, y, width=200, height=50):
        self.image = image
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self):
        # Set up display and clock
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Car Game")

        self.clock = pygame.time.Clock()

        # Load assets
        self.load_assets()

        # Initialize game state variables
        self.selected_level = None
        self.message = ""

    def load_assets(self):
        # Images
        self.background_img = load_image("background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.cloud1_img = load_image("cloud.png", 200, 75)
        self.cloud2_img = load_image("cloud2.png", 175, 65)
        self.level_btn_images = [
            load_image("level1.png", 200, 50),
            load_image("level2.png", 200, 50),
            load_image("level3.png", 200, 50)
        ]
        self.play_btn_img = load_image("play.png", 200, 50)
        self.player_img = load_image("player2.png", 100, 120)
        self.enemy_img = load_image("enemy4.png", 110, 125)
        self.same_dir_enemy_img = load_image("Enemy8.png", 110, 125)
        self.rock_img = load_image("Rock.png", 60, 70)
        self.street_img = load_image("AnimatedStreet.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.finishing_line_img = load_image("FinishingLine.png", SCREEN_WIDTH, 30)
        self.lose_img = load_image("game_over_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.win_img = load_image("you_win_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.coin_img = load_image("coin.png", 70, 70)

        # Sounds
        self.click_sound = load_sound("click.wav")
        self.background_music_path = "background.wav"
        self.victory_sound = load_sound("victory.wav")
        self.collision_sound = load_sound("crash.wav")
        self.coin_sound = load_sound("coin_collect.wav")

        # Fonts
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 40)

    def start_screen(self):
        cloud1_x = SCREEN_WIDTH
        cloud2_x = -self.cloud2_img.get_width()
        cloud1_y = int(SCREEN_HEIGHT * 0.1)
        cloud2_y = int(SCREEN_HEIGHT * 0.2)

        btn_width = 200
        btn_height = 50
        x_pos = (SCREEN_WIDTH - btn_width) // 2
        gap = 20
        start_y = SCREEN_HEIGHT - 200
        y_positions = [start_y - i * (btn_height + gap) for i in range(4)]

        buttons = [
            Button(self.level_btn_images[0], x_pos, y_positions[0]),
            Button(self.level_btn_images[1], x_pos, y_positions[1]),
            Button(self.level_btn_images[2], x_pos, y_positions[2]),
            Button(self.play_btn_img, x_pos, y_positions[3]),
        ]

        running = True
        while running:
            self.screen.blit(self.background_img, (0, 0))

            cloud1_x -= 1
            if cloud1_x < -self.cloud1_img.get_width():
                cloud1_x = SCREEN_WIDTH
            cloud2_x += 1
            if cloud2_x > SCREEN_WIDTH:
                cloud2_x = -self.cloud2_img.get_width()

            self.screen.blit(self.cloud1_img, (cloud1_x, cloud1_y))
            self.screen.blit(self.cloud2_img, (cloud2_x, cloud2_y))

            for btn in buttons:
                btn.draw(self.screen)

            if self.message:
                text_surface = self.font.render(self.message, True, BLACK)
                self.screen.blit(text_surface, (20, 500))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for i, btn in enumerate(buttons):
                        if btn.is_clicked((mx, my)):
                            if i < 3:
                                self.selected_level = i + 1
                                self.message = f"Level {self.selected_level} selected"
                                if self.click_sound:
                                    self.click_sound.play()
                            else:
                                if self.selected_level is None:
                                    self.message = "Choose level first"
                                else:
                                    self.game_loop(self.selected_level)
                                    self.selected_level = None
                                    self.message = ""
                            break

            self.clock.tick(FPS)

    def pause_screen(self):
        pygame.mixer.music.pause()
        paused = True
        while paused:
            self.screen.fill(BLACK)
            pause_text = self.large_font.render("Paused", True, WHITE)
            resume_text = self.font.render("Press ESC to Resume", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    paused = False
                    pygame.mixer.music.unpause()

            self.clock.tick(FPS)

    def check_collision(self, player, enemies):
        return pygame.sprite.spritecollideany(player, enemies) is not None

    def game_loop(self, level):
        player = Player(self.player_img)
        player_group = pygame.sprite.Group(player)
        enemies = pygame.sprite.Group()
        same_direction_enemies = pygame.sprite.Group()
        coins = pygame.sprite.Group()

        street_y = 0
        base_speed = 5
        score = 0
        start_time = None
        enemy_timer = time.time()
        same_dir_timer = time.time()
        coin_timer = time.time()
        finishing_line_y = -30
        finishing_line_reached = False

        if self.background_music_path:
            pygame.mixer.music.load(self.background_music_path)
            pygame.mixer.music.play(-1, 0.0)

        running = True
        while running:
            self.screen.fill(WHITE)
            keys = pygame.key.get_pressed()

            street_speed = base_speed + (4 if keys[pygame.K_UP] else 0)

            street_y += street_speed
            if street_y >= SCREEN_HEIGHT:
                street_y = 0

            self.screen.blit(self.street_img, (0, street_y))
            self.screen.blit(self.street_img, (0, street_y - SCREEN_HEIGHT))

            now = time.time()

            if now - coin_timer >= 2:
                coins.add(Coin(self.coin_img))
                coin_timer = now

            if now - enemy_timer >= 3:
                if level == 1:
                    pass
                elif level == 2:
                    img = random.choice([self.same_dir_enemy_img, self.rock_img])
                    enemies.add(Enemy(img, base_speed))
                elif level == 3:
                    for _ in range(random.randint(2, 4)):
                        img = random.choice([self.enemy_img, self.rock_img])
                        speed = street_speed + random.randint(0, 3)
                        enemies.add(Enemy(img, speed))
                enemy_timer = now

            if level >= 1 and now - same_dir_timer >= 5:
                same_direction_enemies.add(SameDirectionEnemy(self.same_dir_enemy_img))
                same_dir_timer = now

            coins.update()
            enemies.update()
            for e in same_direction_enemies:
                e.update(base_speed)

            coins.draw(self.screen)
            enemies.draw(self.screen)
            same_direction_enemies.draw(self.screen)

            player.update(keys)
            player_group.draw(self.screen)

            # Coin collisions
            coin_collisions = pygame.sprite.spritecollide(player, coins, True)
            for _ in coin_collisions:
                score += 1
                if self.coin_sound:
                    self.coin_sound.play()

            score_text = self.font.render(f"Score: {score}", True, BLACK)
            self.screen.blit(score_text, (10, 17))

            # Enemy collisions
            if self.check_collision(player, enemies) or self.check_collision(player, same_direction_enemies):
                if self.collision_sound:
                    self.collision_sound.play()
                pygame.mixer.music.stop()
                return self.game_over_screen()

            if start_time is None and keys[pygame.K_UP]:
                start_time = time.time()

            if start_time and now - start_time >= 60:
                if finishing_line_y < player.rect.top:
                    finishing_line_y += 2
                else:
                    finishing_line_reached = True
                self.screen.blit(self.finishing_line_img, (0, finishing_line_y))
                if finishing_line_reached:
                    if self.victory_sound:
                        self.victory_sound.play()
                    pygame.mixer.music.stop()
                    return self.level_complete_screen(level)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pause_screen()

            self.clock.tick(FPS)

    def game_over_screen(self):
        while True:
            self.screen.blit(self.lose_img, (0, 0))
            text2 = self.large_font.render("Press SPACE to return to Start", True, WHITE)
            self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return self.start_screen()
            self.clock.tick(FPS)

    def level_complete_screen(self, level):
        while True:
            self.screen.blit(self.win_img, (0, 0))
            text2 = self.large_font.render("Press SPACE to return to Start", True, WHITE)
            self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 120))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return self.start_screen()
            self.clock.tick(FPS)

    def run(self):
        self.start_screen()


if __name__ == "__main__":
    game = Game()
    game.run()
