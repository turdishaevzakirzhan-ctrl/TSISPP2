import pygame
from snake_game import Game
from config import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

state = "menu"
game = Game()

while True:
    screen.fill((0, 0, 0))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            exit()

        if state == "menu":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    game.reset()
                    state = "game"

        elif state == "game":
            game.handle_event(e)

        elif state == "over":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    game.reset()
                    state = "game"
                if e.key == pygame.K_m:
                    state = "menu"

    if state == "menu":
        title = font.render("SNAKE GAME", True, (255,255,255))
        start = font.render("Press ENTER to Play", True, (255,255,255))
        screen.blit(title, (180, 200))
        screen.blit(start, (130, 260))

    elif state == "game":
        if game.update():
            state = "over"
        game.draw(screen)

    elif state == "over":
        over = font.render("GAME OVER", True, (255,255,255))
        retry = font.render("R - Retry   M - Menu", True, (255,255,255))
        screen.blit(over, (200, 220))
        screen.blit(retry, (130, 280))

    pygame.display.flip()
    clock.tick(10)