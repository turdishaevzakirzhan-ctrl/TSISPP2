import pygame

class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, font):
        pygame.draw.rect(screen, (200,200,200), self.rect)
        txt = font.render(self.text, True, (0,0,0))
        screen.blit(txt, (self.rect.x+10, self.rect.y+10))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)