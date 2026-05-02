import pygame
import sys
import random
import time

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

clock = pygame.time.Clock()


player_img = pygame.image.load("assets/spaceship.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 60))

background = pygame.image.load("assets/background.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

meteor_img = pygame.image.load("assets/meteor.png").convert_alpha()
meteor_img = pygame.transform.scale(meteor_img, (40, 40))

explosion_img = pygame.image.load("assets/explosion.png").convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (50, 50))


player_x = WIDTH // 2
player_y = HEIGHT - 80
player_speed = 6


bullets = []
bullet_speed = 8


enemies = []
spawn_delay = 40
frame_count = 0


explosions = []  


score = 0
lives = 3


start_time = time.time()
game_duration = 60

font = pygame.font.SysFont(None, 36)

def draw_text(text, x, y):
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (x, y))

running = True
while running:
    screen.blit(background, (0, 0))
    frame_count += 1

    elapsed_time = int(time.time() - start_time)
    remaining_time = max(0, game_duration - elapsed_time)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append([player_x + 25, player_y])

    # PLAYER MOVEMENT
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    player_x = max(0, min(WIDTH - 60, player_x))

    # SPAWN METEORS
    if frame_count % spawn_delay == 0:
        enemies.append({
            "x": random.randint(20, WIDTH - 20),
            "y": 0,
            "angle": random.randint(0, 360),
            "speed": random.uniform(2, 4)
        })

    # UPDATE BULLETS
    for bullet in bullets:
        bullet[1] -= bullet_speed
    bullets = [b for b in bullets if b[1] > 0]

    # UPDATE METEORS
    for enemy in enemies:
        enemy["y"] += enemy["speed"]
        enemy["angle"] += 3  # rotation

    # BULLET COLLISION
    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if abs(enemy["x"] - bullet[0]) < 25 and abs(enemy["y"] - bullet[1]) < 25:
                enemies.remove(enemy)
                bullets.remove(bullet)

                explosions.append([enemy["x"], enemy["y"], 10])
                score += 10
                break

    # PLAYER COLLISION
    for enemy in enemies[:]:
        if abs(enemy["x"] - player_x) < 40 and abs(enemy["y"] - player_y) < 40:
            enemies.remove(enemy)

            explosions.append([enemy["x"], enemy["y"], 10])
            score -= 10
            lives -= 1

    enemies = [e for e in enemies if e["y"] < HEIGHT]

    # DRAW PLAYER
    screen.blit(player_img, (player_x, player_y))

    # DRAW BULLETS
    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 255), (bullet[0], bullet[1], 4, 10))

    # DRAW METEORS (ROTATING)
    for enemy in enemies:
        rotated = pygame.transform.rotate(meteor_img, enemy["angle"])
        rect = rotated.get_rect(center=(enemy["x"], enemy["y"]))
        screen.blit(rotated, rect.topleft)

    # DRAW EXPLOSIONS
    for exp in explosions[:]:
        screen.blit(explosion_img, (exp[0], exp[1]))
        exp[2] -= 1
        if exp[2] <= 0:
            explosions.remove(exp)

    # UI
    draw_text(f"Score: {score}", 10, 10)
    draw_text(f"Lives: {lives}", 10, 40)
    draw_text(f"Time: {remaining_time}", 10, 70)

    # GAME OVER
    if lives <= 0 or remaining_time <= 0:
        screen.fill((0, 0, 0))
        draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2)
        draw_text(f"Final Score: {score}", WIDTH // 2 - 100, HEIGHT // 2 + 40)
        pygame.display.update()
        pygame.time.delay(3000)
        running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()