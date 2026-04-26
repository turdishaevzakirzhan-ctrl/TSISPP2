import pygame, random, json
from config import *

class Game:
    def __init__(self):
        self.load_settings()
        self.reset()

    def load_settings(self):
        try:
            with open("settings.json") as f:
                s = json.load(f)
        except:
            s = {"snake_color":[0,255,0],"grid":True,"sound":True}
        self.snake_color = tuple(s["snake_color"])
        self.grid = s["grid"]

    def reset(self):
        self.snake=[(10,10)]
        self.dir=(1,0)
        self.score=0
        self.level=1
        self.speed=10
        self.food=None
        self.poison=None
        self.power=None
        self.power_type=None
        self.power_end=0
        self.obstacles=[]
        self.spawn_food()
        self.spawn_poison()

    def spawn_food(self):
        while True:
            p=(random.randint(0,29),random.randint(0,29))
            if p not in self.snake and p not in self.obstacles:
                self.food=p
                break

    def spawn_poison(self):
        while True:
            p=(random.randint(0,29),random.randint(0,29))
            if p not in self.snake:
                self.poison=p
                break

    def spawn_power(self):
        types=["speed","slow","shield"]
        while True:
            p=(random.randint(0,29),random.randint(0,29))
            if p not in self.snake:
                self.power=p
                self.power_type=random.choice(types)
                self.power_end=pygame.time.get_ticks()+5000
                break

    def gen_obstacles(self):
        self.obstacles=[]
        for _ in range(self.level*3):
            while True:
                p=(random.randint(0,29),random.randint(0,29))
                if p not in self.snake:
                    self.obstacles.append(p)
                    break

    def handle_event(self,e):
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_UP and self.dir!=(0,1): self.dir=(0,-1)
            if e.key==pygame.K_DOWN and self.dir!=(0,-1): self.dir=(0,1)
            if e.key==pygame.K_LEFT and self.dir!=(1,0): self.dir=(-1,0)
            if e.key==pygame.K_RIGHT and self.dir!=(-1,0): self.dir=(1,0)

    def update(self):
        head=(self.snake[0][0]+self.dir[0],self.snake[0][1]+self.dir[1])

        if head in self.snake or head in self.obstacles:
            return True

        if head[0]<0 or head[1]<0 or head[0]>=30 or head[1]>=30:
            return True

        self.snake.insert(0,head)

        if head==self.food:
            self.score+=1
            if self.score%5==0:
                self.level+=1
                self.speed+=2
                if self.level>=3:
                    self.gen_obstacles()
            self.spawn_food()
            if random.random()<0.3:
                self.spawn_power()
        else:
            self.snake.pop()

        if head==self.poison:
            self.snake=self.snake[:-2]
            if len(self.snake)<=1:
                return True
            self.spawn_poison()

        if self.power:
            if pygame.time.get_ticks()>self.power_end:
                self.power=None

        return False

    def draw(self,screen):
        if self.grid:
            for x in range(0,WIDTH,CELL):
                pygame.draw.line(screen,(40,40,40),(x,0),(x,HEIGHT))
            for y in range(0,HEIGHT,CELL):
                pygame.draw.line(screen,(40,40,40),(0,y),(WIDTH,y))

        for s in self.snake:
            pygame.draw.rect(screen,self.snake_color,(s[0]*CELL,s[1]*CELL,CELL,CELL))

        for o in self.obstacles:
            pygame.draw.rect(screen,(100,100,100),(o[0]*CELL,o[1]*CELL,CELL,CELL))

        pygame.draw.rect(screen,(255,255,0),(self.food[0]*CELL,self.food[1]*CELL,CELL,CELL))
        pygame.draw.rect(screen,(150,0,0),(self.poison[0]*CELL,self.poison[1]*CELL,CELL,CELL))

        if self.power:
            pygame.draw.rect(screen,(0,0,255),(self.power[0]*CELL,self.power[1]*CELL,CELL,CELL))