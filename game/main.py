import pygame
import random
import sys
import os

# ================= INIT =================
pygame.init()
pygame.mixer.init()

# ================= PATH =================
BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "assets")

# ================= SCREEN =================
WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Runner - Full Game")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 42)

# ================= LOAD IMAGES =================
player_img = pygame.image.load(os.path.join(ASSET_DIR, "orang.png")).convert_alpha()
cactus_img = pygame.image.load(os.path.join(ASSET_DIR, "kaktus.png")).convert_alpha()
bird_img   = pygame.image.load(os.path.join(ASSET_DIR, "burung.png")).convert_alpha()
ground_img = pygame.image.load(os.path.join(ASSET_DIR, "tanah.png")).convert_alpha()

player_img = pygame.transform.scale(player_img, (90, 90))
cactus_img = pygame.transform.scale(cactus_img, (90, 90))
bird_img   = pygame.transform.scale(bird_img, (60, 60))
ground_img = pygame.transform.scale(ground_img, (WIDTH, 40))

# ================= LOAD SOUND =================
pygame.mixer.music.load(os.path.join(ASSET_DIR, "bgm.mp3"))
pygame.mixer.music.set_volume(0.4)

# ================= COLORS =================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CLOUD_COLOR = (255, 255, 255)

SKY_MORNING_TOP = (70, 160, 230)
SKY_MORNING_BOTTOM = (180, 225, 255)

SKY_EVENING_TOP = (255, 140, 60)
SKY_EVENING_BOTTOM = (255, 210, 150)

SKY_NIGHT_TOP = (20, 20, 60)
SKY_NIGHT_BOTTOM = (60, 60, 120)

# ================= SAVE SYSTEM =================
SAVE_FILE = os.path.join(BASE_DIR, "save_data.txt")
high_score = 0
max_level = 1

if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        for line in f:
            if line.startswith("highscore"):
                high_score = int(line.split("=")[1])
            elif line.startswith("maxlevel"):
                max_level = int(line.split("=")[1])

def save_data():
    with open(SAVE_FILE, "w") as f:
        f.write(f"highscore={high_score}\n")
        f.write(f"maxlevel={max_level}\n")

# ================= PLAYER =================
PLAYER_W, PLAYER_H = 90, 90
dino_img_rect = pygame.Rect(80, 220, PLAYER_W, PLAYER_H)

dino_hitbox = pygame.Rect(
    dino_img_rect.x + 28,   # geser ke kanan
    dino_img_rect.y + 18,   # geser ke bawah
    PLAYER_W - 56,          # lebar diperkecil
    PLAYER_H - 36           # tinggi diperkecil
)

dino_vel_y = 0
gravity = 0.8
jump_power = -18
is_jump = False

# ================= SPAWN =================
def spawn_cactus(level):
    jarak = max(200, 350 - level * 30)
    return pygame.Rect(WIDTH + random.randint(jarak, jarak + 200), 220, 40, 60)

def spawn_bird():
    return pygame.Rect(WIDTH + random.randint(400, 600),
                       random.choice([140, 160]), 40, 30)

def spawn_cloud():
    return {
        "rect": pygame.Rect(WIDTH + random.randint(0, 300),
                            random.randint(40, 100), 60, 20),
        "speed": random.uniform(0.3, 0.7)
    }

# ================= GAME STATE =================
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "gameover"
state = MENU

# ================= VARIABLES =================
cactus_list = []
bird_list = []
clouds = []

score = 0
level = 1
speed = 4

ground_x = 0
ground_y = 260

# ================= RESET =================
def reset_game():
    global score, level, speed, state, dino_vel_y, is_jump

    score = 0
    level = 1
    speed = 4

    cactus_list.clear()
    bird_list.clear()
    clouds.clear()

    dino_img_rect.y = 220
    dino_vel_y = 0
    is_jump = False

    pygame.mixer.music.stop()
    pygame.mixer.music.play(-1)

    state = PLAYING

# ================= DRAW SKY =================
def draw_sky(surface, level):
    if level < 3:
        top, bottom = SKY_MORNING_TOP, SKY_MORNING_BOTTOM
    elif level < 5:
        top, bottom = SKY_EVENING_TOP, SKY_EVENING_BOTTOM
    else:
        top, bottom = SKY_NIGHT_TOP, SKY_NIGHT_BOTTOM

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = top[0] + (bottom[0] - top[0]) * ratio
        g = top[1] + (bottom[1] - top[1]) * ratio
        b = top[2] + (bottom[2] - top[2]) * ratio
        pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (WIDTH, y))

# ================= MAIN LOOP =================
while True:
    clock.tick(60)
    draw_sky(screen, level)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if state == MENU and event.key == pygame.K_SPACE:
                reset_game()

            elif state == PLAYING and event.key == pygame.K_SPACE and not is_jump:
                dino_vel_y = jump_power
                is_jump = True

            elif state == GAME_OVER and event.key == pygame.K_SPACE:
                state = MENU

    # ================= CLOUD =================
    if state == PLAYING and level < 5:
        if len(clouds) < 3:
            clouds.append(spawn_cloud())

        for cloud in clouds[:]:
            cloud["rect"].x -= cloud["speed"]
            if cloud["rect"].x < -60:
                clouds.remove(cloud)
            else:
                r = cloud["rect"]
                pygame.draw.ellipse(screen, CLOUD_COLOR, (r.x, r.y, 30, 20))
                pygame.draw.ellipse(screen, CLOUD_COLOR, (r.x + 20, r.y - 10, 30, 30))
                pygame.draw.ellipse(screen, CLOUD_COLOR, (r.x + 35, r.y, 30, 20))

    # ================= MENU =================
    if state == MENU:
        screen.blit(big_font.render("DINO RUNNER", True, BLACK), (WIDTH//2 - 150, 80))
        screen.blit(font.render("Tekan SPACE untuk mulai", True, BLACK), (WIDTH//2 - 120, 130))
        screen.blit(font.render(f"High Score: {high_score}", True, BLACK), (WIDTH//2 - 80, 170))
        screen.blit(font.render(f"Max Level: {max_level}", True, BLACK), (WIDTH//2 - 80, 195))

    # ================= PLAYING =================
    elif state == PLAYING:
        ground_x -= speed
        if ground_x <= -WIDTH:
            ground_x = 0

        dino_vel_y += gravity
        dino_img_rect.y += dino_vel_y
        if dino_img_rect.y >= 220:
            dino_img_rect.y = 220
            is_jump = False

        dino_hitbox.x = dino_img_rect.x + 28
        dino_hitbox.y = dino_img_rect.y + 18

        if len(cactus_list) == 0 or cactus_list[-1].x < WIDTH - 350:
            cactus_list.append(spawn_cactus(level))

        if level >= 2 and random.randint(0, 200) == 1:
            bird_list.append(spawn_bird())

        for cactus in cactus_list[:]:
            cactus.x -= speed
            if cactus.x < -40:
                cactus_list.remove(cactus)
                score += 1
            elif dino_hitbox.colliderect(cactus):
                state = GAME_OVER

        for bird in bird_list[:]:
            bird.x -= speed
            if bird.x < -40:
                bird_list.remove(bird)
            elif dino_hitbox.colliderect(bird):
                state = GAME_OVER

        level = score // 10 + 1
        speed = 4 + level * 0.5

        screen.blit(ground_img, (ground_x, ground_y))
        screen.blit(ground_img, (ground_x + WIDTH, ground_y))
        screen.blit(player_img, dino_img_rect)

        for cactus in cactus_list:
            screen.blit(cactus_img, cactus)
        for bird in bird_list:
            screen.blit(bird_img, bird)

        screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, BLACK), (10, 30))

    # ================= GAME OVER =================
    elif state == GAME_OVER:
        if score > high_score:
            high_score = score
        if level > max_level:
            max_level = level
        save_data()

        screen.blit(big_font.render("GAME OVER", True, BLACK), (WIDTH//2 - 130, 80))
        screen.blit(font.render(f"Score: {score}", True, BLACK), (WIDTH//2 - 50, 130))
        screen.blit(font.render("SPACE ke Menu", True, BLACK), (WIDTH//2 - 80, 170))

    pygame.display.update()
