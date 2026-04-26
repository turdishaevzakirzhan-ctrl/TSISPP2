import pygame
import random
import time

WIDTH, HEIGHT = 400, 600
LANES = [100, 200, 300]

class Player:
    def __init__(self, color):
        self.lane = 1
        self.y = 500
        self.speed = 5
        self.powerup = None
        self.powerup_end = 0
        self.shield = False
        self.image = pygame.image.load(f"assets/player_{color}.png")
        self.image = pygame.transform.scale(self.image, (60, 100))

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1

    def move_right(self):
        if self.lane < 2:
            self.lane += 1

    def activate_powerup(self, p):
        self.powerup = p
        if p == "nitro":
            self.speed = 10
            self.powerup_end = time.time() + 4
        elif p == "shield":
            self.shield = True
        elif p == "repair":
            return "repair"

    def update(self):
        if self.powerup == "nitro" and time.time() > self.powerup_end:
            self.speed = 5
            self.powerup = None


class Obstacle:
    def __init__(self):
        self.lane = random.randint(0, 2)
        self.y = -100
        self.type = random.choice(["car", "oil", "barrier"])

        if self.type == "car":
            try:
                self.image = pygame.image.load("assets/enemy.png")
            except:
                self.image = pygame.Surface((60, 100))
                self.image.fill((0, 0, 255))
            self.image = pygame.transform.scale(self.image, (60, 100))

        elif self.type == "barrier":
            try:
                self.image = pygame.image.load("assets/barrier.png")
            except:
                self.image = pygame.Surface((70, 70))
                self.image.fill((255, 0, 0))
            self.image = pygame.transform.scale(self.image, (70, 70))

        else:
            self.image = pygame.image.load("assets/oil.png")
            self.image = pygame.transform.scale(self.image, (70, 70))

    def move(self, speed):
        self.y += speed


class Coin:
    def __init__(self):
        self.lane = random.randint(0, 2)
        self.y = -50
        try:
            self.image = pygame.image.load("assets/coin.png")
            self.image = pygame.transform.scale(self.image, (30, 30))
        except:
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 255, 0))

    def move(self):
        self.y += 6


class PowerUp:
    def __init__(self):
        self.lane = random.randint(0, 2)
        self.y = -50
        self.type = random.choice(["nitro", "shield", "repair"])
        self.spawn_time = time.time()
        self.image = pygame.image.load(f"assets/{self.type}.png")
        self.image = pygame.transform.scale(self.image, (40, 40))

    def move(self):
        self.y += 5

    def expired(self):
        return time.time() - self.spawn_time > 6


class Game:
    def __init__(self, settings):
        self.player = Player(settings["car_color"])
        self.obstacles = []
        self.coins = []
        self.powerups = []
        self.score = 0
        self.distance = 0
        self.running = True
        self.spawn_rate = 30
        if settings["difficulty"] == "hard":
            self.spawn_rate = 20
        self.road = pygame.image.load("assets/road.png")
        self.road = pygame.transform.scale(self.road, (WIDTH, HEIGHT))

    def spawn(self):
        if random.randint(1, self.spawn_rate) == 1:
            self.obstacles.append(Obstacle())
        if random.randint(1, 40) == 1:
            self.coins.append(Coin())
        if random.randint(1, 150) == 1:
            self.powerups.append(PowerUp())

    def update(self):
        self.player.update()
        self.spawn()

        for o in self.obstacles:
            o.move(self.player.speed)

        for c in self.coins:
            c.move()

        for p in self.powerups:
            p.move()

        self.powerups = [p for p in self.powerups if not p.expired()]

        self.distance += 1
        self.score = self.distance

        if self.distance % 400 == 0:
            self.spawn_rate = max(10, self.spawn_rate - 2)

        self.check_collisions()

    def check_collisions(self):
        px = LANES[self.player.lane]
        player_rect = pygame.Rect(px - 30, self.player.y, 60, 100)

        for o in self.obstacles[:]:
            ox = LANES[o.lane]
            o_rect = pygame.Rect(ox - 35, o.y, 70, 70)
            if player_rect.colliderect(o_rect):
                if self.player.shield:
                    self.player.shield = False
                    self.obstacles.remove(o)
                else:
                    self.running = False
            elif o.y > HEIGHT:
                self.obstacles.remove(o)

        for c in self.coins[:]:
            cx = LANES[c.lane]
            c_rect = pygame.Rect(cx - 15, c.y, 30, 30)
            if player_rect.colliderect(c_rect):
                self.score += 10
                self.coins.remove(c)
            elif c.y > HEIGHT:
                self.coins.remove(c)

        for p in self.powerups[:]:
            px2 = LANES[p.lane]
            p_rect = pygame.Rect(px2 - 20, p.y, 40, 40)
            if player_rect.colliderect(p_rect):
                result = self.player.activate_powerup(p.type)
                if result == "repair" and self.obstacles:
                    self.obstacles.pop()
                self.powerups.remove(p)