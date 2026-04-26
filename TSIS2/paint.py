import pygame
import sys
from datetime import datetime

pygame.init()


WIDTH, HEIGHT = 1200, 700
TOOLBAR_HEIGHT = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App")

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)

palette_colors = [
    (0,0,0),(255,0,0),(0,255,0),
    (0,0,255),(255,255,0),(255,165,0),
    (128,0,128),(0,255,255),(255,255,255)
]

current_color = BLACK


tool = "pencil"

tools = [
    "pencil","line","rect","circle",
    "square","r_triangle","eq_triangle","rhombus",
    "eraser","fill","text"
]

tool_names = {
    "pencil":"Pencil","line":"Line","rect":"Rect","circle":"Circle",
    "square":"Square","r_triangle":"R-Tri","eq_triangle":"Eq-Tri",
    "rhombus":"Rhombus","eraser":"Eraser","fill":"Fill","text":"Text"
}


brush_sizes = {"S":2,"M":5,"L":10}
brush_size = brush_sizes["S"]


drawing = False
start_pos = None
last_pos = None


font = pygame.font.SysFont(None, 28)
typing = False
text = ""
text_pos = (0,0)
cursor_visible = True
cursor_timer = 0


class Button:
    def __init__(self,x,y,w,h,text,value,group):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text
        self.value = value
        self.group = group

    def draw(self,screen,selected):
        color = DARK_GRAY if selected else GRAY
        pygame.draw.rect(screen,color,self.rect)
        pygame.draw.rect(screen,BLACK,self.rect,2)
        txt = font.render(self.text,True,BLACK)
        screen.blit(txt,(self.rect.x+5,self.rect.y+5))


buttons = []
x = 10
for t in tools:
    buttons.append(Button(x,10,90,30,tool_names[t],t,"tool"))
    x += 95

x = 10
for s in ["S","M","L"]:
    buttons.append(Button(x,40,50,20,s,s,"size"))
    x += 60

color_buttons = []
x = 250
for c in palette_colors:
    color_buttons.append((pygame.Rect(x,40,25,20),c))
    x += 30


def draw_rect(s,c,a,b,w):
    pygame.draw.rect(s,c,(a[0],a[1],b[0]-a[0],b[1]-a[1]),w)

def draw_circle(s,c,a,b,w):
    r = int(((b[0]-a[0])**2+(b[1]-a[1])**2)**0.5)
    pygame.draw.circle(s,c,a,r,w)

def draw_square(s,c,a,b,w):
    size = max(abs(b[0]-a[0]),abs(b[1]-a[1]))
    pygame.draw.rect(s,c,(a[0],a[1],size,size),w)

def draw_r_triangle(s,c,a,b,w):
    pygame.draw.polygon(s,c,[a,(b[0],b[1]),(a[0],b[1])],w)

def draw_eq_triangle(s,c,a,b,w):
    base = b[0]-a[0]
    h = abs(base)*(3**0.5)/2
    pts=[(a[0],b[1]),(b[0],b[1]),((a[0]+b[0])//2,int(b[1]-h))]
    pygame.draw.polygon(s,c,pts,w)

def draw_rhombus(s,c,a,b,w):
    cx=(a[0]+b[0])//2
    cy=(a[1]+b[1])//2
    pts=[(cx,a[1]),(b[0],cy),(cx,b[1]),(a[0],cy)]
    pygame.draw.polygon(s,c,pts,w)


def flood_fill(surface,x,y,new_color):
    target = surface.get_at((x,y))
    if target == new_color: return
    stack=[(x,y)]
    while stack:
        px,py=stack.pop()
        if px<0 or px>=surface.get_width(): continue
        if py<0 or py>=surface.get_height(): continue
        if surface.get_at((px,py))!=target: continue
        surface.set_at((px,py),new_color)
        stack += [(px+1,py),(px-1,py),(px,py+1),(px,py-1)]


while True:

    screen.fill(GRAY)


    cursor_timer += 1
    if cursor_timer >= 30:
        cursor_visible = not cursor_visible
        cursor_timer = 0


    for b in buttons:
        selected = (b.value == tool) if b.group=="tool" else (brush_size==brush_sizes[b.value])
        b.draw(screen,selected)

    for rect,col in color_buttons:
        pygame.draw.rect(screen,col,rect)
        pygame.draw.rect(screen,BLACK,rect,3 if col==current_color else 1)

    screen.blit(canvas,(0,TOOLBAR_HEIGHT))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key==pygame.K_1: brush_size=brush_sizes["S"]
            if event.key==pygame.K_2: brush_size=brush_sizes["M"]
            if event.key==pygame.K_3: brush_size=brush_sizes["L"]

            if event.key==pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                name=datetime.now().strftime("drawing_%Y%m%d_%H%M%S.png")
                pygame.image.save(canvas,name)

            if typing:
                if event.key==pygame.K_RETURN:
                    canvas.blit(font.render(text,True,current_color),text_pos)
                    typing=False; text=""
                elif event.key==pygame.K_ESCAPE:
                    typing=False; text=""
                elif event.key==pygame.K_BACKSPACE:
                    text=text[:-1]
                else:
                    text+=event.unicode


        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = event.pos


            if my <= TOOLBAR_HEIGHT:
                for b in buttons:
                    if b.rect.collidepoint(event.pos):
                        if b.group=="tool": tool=b.value
                        elif b.group=="size": brush_size=brush_sizes[b.value]

                for rect,col in color_buttons:
                    if rect.collidepoint(event.pos):
                        current_color=col

                drawing = False
                continue  


            x = mx
            y = my - TOOLBAR_HEIGHT

            if y < 0:
                continue

            drawing = True
            start_pos = (x,y)
            last_pos = (x,y)

            if tool=="fill":
                flood_fill(canvas,x,y,current_color)

            if tool=="text":
                typing=True
                text=""
                text_pos=(x,y)


        if event.type == pygame.MOUSEBUTTONUP:
            mx,my = event.pos
            pos = (mx, my - TOOLBAR_HEIGHT)
            drawing=False

            if pos[1] < 0:
                continue

            if tool=="line":
                pygame.draw.line(canvas,current_color,start_pos,pos,brush_size)
            elif tool=="rect":
                draw_rect(canvas,current_color,start_pos,pos,brush_size)
            elif tool=="circle":
                draw_circle(canvas,current_color,start_pos,pos,brush_size)
            elif tool=="square":
                draw_square(canvas,current_color,start_pos,pos,brush_size)
            elif tool=="r_triangle":
                draw_r_triangle(canvas,current_color,start_pos,pos,brush_size)
            elif tool=="eq_triangle":
                draw_eq_triangle(canvas,current_color,start_pos,pos,brush_size)
            elif tool=="rhombus":
                draw_rhombus(canvas,current_color,start_pos,pos,brush_size)


        if event.type == pygame.MOUSEMOTION and drawing:
            mx,my = event.pos
            pos = (mx,my-TOOLBAR_HEIGHT)
            if pos[1] < 0:
                continue

            if tool=="pencil":
                pygame.draw.line(canvas,current_color,last_pos,pos,brush_size)
                last_pos=pos
            elif tool=="eraser":
                pygame.draw.line(canvas,WHITE,last_pos,pos,brush_size)
                last_pos=pos


    if drawing:
        mx,my = pygame.mouse.get_pos()
        pos=(mx,my-TOOLBAR_HEIGHT)
        if pos[1]>=0 and tool in ["line","rect","circle","square","r_triangle","eq_triangle","rhombus"]:
            temp=canvas.copy()
            if tool=="line": pygame.draw.line(temp,current_color,start_pos,pos,brush_size)
            elif tool=="rect": draw_rect(temp,current_color,start_pos,pos,brush_size)
            elif tool=="circle": draw_circle(temp,current_color,start_pos,pos,brush_size)
            elif tool=="square": draw_square(temp,current_color,start_pos,pos,brush_size)
            elif tool=="r_triangle": draw_r_triangle(temp,current_color,start_pos,pos,brush_size)
            elif tool=="eq_triangle": draw_eq_triangle(temp,current_color,start_pos,pos,brush_size)
            elif tool=="rhombus": draw_rhombus(temp,current_color,start_pos,pos,brush_size)
            screen.blit(temp,(0,TOOLBAR_HEIGHT))


    if typing:
        img=font.render(text,True,current_color)
        screen.blit(img,(text_pos[0],text_pos[1]+TOOLBAR_HEIGHT))
        if cursor_visible:
            x=text_pos[0]+img.get_width()
            y=text_pos[1]+TOOLBAR_HEIGHT
            pygame.draw.line(screen,current_color,(x,y),(x,y+img.get_height()),2)

    pygame.display.flip()
    clock.tick(60)