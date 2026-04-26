import pygame
from racer import Game, LANES
from persistence import load_json, save_json

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

settings = load_json("settings.json", {
    "sound": True,
    "car_color": "white",
    "difficulty": "normal"
})

leaderboard = load_json("leaderboard.json", [])

state = "menu"
game = None
last_score = 0
last_distance = 0

play_btn = pygame.Rect(150, 180, 100, 50)
lead_btn = pygame.Rect(120, 260, 160, 50)
settings_btn = pygame.Rect(130, 340, 140, 50)
quit_btn = pygame.Rect(150, 420, 100, 50)

retry_btn = pygame.Rect(140, 300, 120, 50)
menu_btn_go = pygame.Rect(140, 380, 120, 50)

color_btn = pygame.Rect(120, 200, 160, 50)
difficulty_btn = pygame.Rect(120, 280, 160, 50)
sound_btn = pygame.Rect(120, 360, 160, 50)
back_btn = pygame.Rect(150, 440, 100, 50)

colors = ["white" , "green"]
difficulties = ["easy", "normal", "hard"]

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == "game":
                if event.key == pygame.K_LEFT:
                    game.player.move_left()
                if event.key == pygame.K_RIGHT:
                    game.player.move_right()
            if state == "leaderboard":
                if event.key == pygame.K_ESCAPE:
                    state = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "menu":
                if play_btn.collidepoint(event.pos):
                    game = Game(settings)
                    state = "game"
                elif lead_btn.collidepoint(event.pos):
                    state = "leaderboard"
                elif settings_btn.collidepoint(event.pos):
                    state = "settings"
                elif quit_btn.collidepoint(event.pos):
                    running = False

            elif state == "settings":
                if color_btn.collidepoint(event.pos):
                    i = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(i + 1) % 3]
                elif difficulty_btn.collidepoint(event.pos):
                    i = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(i + 1) % 3]
                elif sound_btn.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                elif back_btn.collidepoint(event.pos):
                    save_json("settings.json", settings)
                    state = "menu"

            elif state == "gameover":
                if retry_btn.collidepoint(event.pos):
                    game = Game(settings)
                    state = "game"
                elif menu_btn_go.collidepoint(event.pos):
                    state = "menu"

    if state == "menu":
        pygame.draw.rect(screen, (200, 200, 200), play_btn)
        pygame.draw.rect(screen, (200, 200, 200), lead_btn)
        pygame.draw.rect(screen, (200, 200, 200), settings_btn)
        pygame.draw.rect(screen, (200, 200, 200), quit_btn)

        screen.blit(font.render("Play", True, (0, 0, 0)), (170, 195))
        screen.blit(font.render("Leaderboard", True, (0, 0, 0)), (130, 275))
        screen.blit(font.render("Settings", True, (0, 0, 0)), (145, 355))
        screen.blit(font.render("Quit", True, (0, 0, 0)), (170, 435))

    elif state == "game":
        game.update()

        screen.blit(game.road, (0, 0))

        px = LANES[game.player.lane]
        screen.blit(game.player.image, (px - 30, game.player.y))

        for o in game.obstacles:
            x = LANES[o.lane]
            screen.blit(o.image, (x - 30, o.y))

        for c in game.coins:
            x = LANES[c.lane]
            screen.blit(c.image, (x - 15, c.y))

        for p in game.powerups:
            x = LANES[p.lane]
            screen.blit(p.image, (x - 20, p.y))

        screen.blit(font.render(f"Score: {game.score}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Distance: {game.distance}", True, (255, 255, 255)), (10, 40))

        if not game.running:
            last_score = game.score
            last_distance = game.distance
            leaderboard.append({
                "name": "Player",
                "score": game.score,
                "distance": game.distance
            })
            leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]
            save_json("leaderboard.json", leaderboard)
            state = "gameover"

    elif state == "gameover":
        pygame.draw.rect(screen, (200, 200, 200), retry_btn)
        pygame.draw.rect(screen, (200, 200, 200), menu_btn_go)

        screen.blit(font.render("GAME OVER", True, (255, 0, 0)), (120, 150))
        screen.blit(font.render(f"Score: {last_score}", True, (255, 255, 255)), (130, 210))
        screen.blit(font.render(f"Distance: {last_distance}", True, (255, 255, 255)), (120, 250))

        screen.blit(font.render("Retry", True, (0, 0, 0)), (160, 315))
        screen.blit(font.render("Menu", True, (0, 0, 0)), (165, 395))

    elif state == "leaderboard":
        y = 100
        for entry in leaderboard:
            text = font.render(f"{entry['name']} {entry['score']}", True, (255, 255, 255))
            screen.blit(text, (80, y))
            y += 40

        screen.blit(font.render("ESC to return", True, (200, 200, 200)), (100, 550))

    elif state == "settings":
        pygame.draw.rect(screen, (200, 200, 200), color_btn)
        pygame.draw.rect(screen, (200, 200, 200), difficulty_btn)
        pygame.draw.rect(screen, (200, 200, 200), sound_btn)
        pygame.draw.rect(screen, (200, 200, 200), back_btn)

        screen.blit(font.render(f"Car: {settings['car_color']}", True, (0, 0, 0)), (130, 215))
        screen.blit(font.render(f"Difficulty: {settings['difficulty']}", True, (0, 0, 0)), (130, 295))
        screen.blit(font.render(f"Sound: {settings['sound']}", True, (0, 0, 0)), (130, 375))
        screen.blit(font.render("Back", True, (0, 0, 0)), (170, 455))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()