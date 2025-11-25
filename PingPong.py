import sys, math, random
from time import sleep, monotonic
import gc
gc.disable()

try:
    import pygame
except:
    showerror("Pygame not found","'Pygame' module for python haven't been found.")
    sys.exit(-1)
try:
    import tracemalloc
    tracemalloc_available = True
except ModuleNotFoundError:
    tracemalloc_available = False
    showwarning("Tracemalloc","'tracemalloc' not found in python's modules\n\n\n\nDumbass.")
try:
    from additional.text import Text
except ImportError:
    showerror("Text missing","'Text' module from 'addition' haven't been found.")

from tkinter.messagebox import askyesno, showerror, showwarning
from pygame import Vector2, Rect, Color, Surface

CURSOR_SIZE = (10,10)
MAX_BALLS = 1000 
FPS = 120
BALLS_DELETED = 0
CURRENT_BALL = -1
BALL_SCREEN_FRICTION = 1
BALL_OTHERS_FRICTION = 0.9
BALL_RECT_FRICTION = 0.95
MAX_HOLE_DISTANCE = 300

gravity = 0.05

def get_gravity(): return Vector2(0,gravity)

VECTOR_ZERO = Vector2(0,0)

def convert_size(size_bytes : int):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

class Button:
    rect : Rect
    surf : Surface
    text : str
    font : pygame.font.Font
    def __init__(self, text : str, margin : int, f_color : Color, bg_color : Color):
        self.font = pygame.font.SysFont("arial",16)
        self.surf = Text()

class Collition_Rect(Rect):
    def __init__(self, screen, rect) -> None:
        self.color = Color(255,255,255)
        self.surface = screen
        self.tsize = 5
        self.suprise = 0

        if isinstance(rect,tuple):
            self.topleft = (rect[0],rect[1])
            self.size = (rect[2],rect[3])
        if isinstance(rect,Rect):
            self.topleft = rect.topleft
            self.size = rect.size

        self.coltop = (self.topleft,self.topright)
        self.colleft = (self.topleft,self.bottomleft)
        self.colright = (self.topright,self.bottomright)
        self.colbottom = (self.bottomleft,self.bottomright)
        self.recttop = Rect(self.left,self.top,self.size[0],self.tsize)
        self.rectleft = Rect(self.left,self.top,self.tsize,self.size[1])
        self.rectright = Rect(self.right - self.tsize,self.top,self.tsize,self.size[1])
        self.rectbottom = Rect(self.left,self.bottom - self.tsize,self.size[0],self.tsize)

        self.col_rect = [self.recttop,self.rectleft,self.rectright,self.rectbottom]

        # print("""
        #       Top Left : {0} <-> {1}
        #       Bottom Right : {2} <->  {3}

        #       Size : {4}
              
        #       """.format(self.topleft, rect.topleft, self.bottomright, rect.bottomright, rect.size))

    def update(self, balls_list = []):
        #pygame.draw.rect(self.surface,self.color,self,self.tsize)
        
        pygame.draw.rect(self.surface,self.color,self.recttop,5)#self.tsize)
        pygame.draw.rect(self.surface,self.color,self.rectleft,5)#self.tsize)
        pygame.draw.rect(self.surface,self.color,self.rectright,5)#self.tsize)
        pygame.draw.rect(self.surface,self.color,self.rectbottom,5)#self.tsize)
        #print(self)
        self.suprise = max(0,self.suprise - 0.05)
        #self.tsize = 5 + self.suprise

    def check_col_ball(self, ball : Rect):
        if ball.colliderect(self):
            if ball.colliderect(self.recttop):
                ball.vector.y = -abs(ball.vector.y) * BALL_SCREEN_FRICTION
            if ball.colliderect(self.rectleft):
                ball.vector.x = -abs(ball.vector.x)
            if ball.colliderect(self.rectright):
                ball.vector.x = abs(ball.vector.x)
            if self.colliderect(self.rectbottom):  
                ball.vector.y = abs(ball.vector.y)
    
    def surprize(self):
        self.surprise = 3

#region Cursor Class
class CursorRect(Rect):
    def __init__(self,screen) -> None:
        self.color = "white"
        self.surface = screen
        self.size_min = 10
        self.size_max = 15
        self.magn_min = 5
        self.magn_max = 70
        self.tsize = 5
        self.speed = 0.0
        self.type = "Ball"
        self.selected_ball = -1
        self.vector : Vector2 = Vector2(0,0)

    def update(self,balls : list[Rect], rects : list[Rect], power : float, delta_time : 1):
        global BALLS_DELETED
        self.vector = Vector2(pygame.mouse.get_rel())
        self.speed = self.vector.magnitude()
        match(self.type):
            case "Ball":
                if self.vector != VECTOR_ZERO:
                    self.tsize = pygame.math.clamp(
                        math.sqrt(self.vector.magnitude()*5),
                        self.size_min,
                        self.size_max)
                else: 
                    self.tsize = self.size_min

                self.rect = pygame.draw.circle(self.surface,self.color,pygame.mouse.get_pos(),self.tsize,5)
                self.topleft = self.rect.topleft
                self.width, self.height = self.tsize*2,self.tsize*2

                for ball in balls:
                    if ball.colliderect(self) and (ball.position - self.center) != VECTOR_ZERO:
                        ball.static_ballrect_collision (self)
            case "Selector":
                self.topleft = pygame.mouse.get_pos()
            case "Eraser":
                self.topleft = pygame.mouse.get_pos()
                index = self.collidelist(balls)
                if index != -1:
                    BALLS_DELETED += 1
                    del(balls[index])
                    BALLS_DELETED += 1
                    #print(index)
            case "White Hole":
                puissance = power
                self.topleft = pygame.mouse.get_pos()
                pygame.draw.circle(self.surface,(50,50,50),self.topleft,MAX_HOLE_DISTANCE-1/puissance,10)
                if pygame.mouse.get_pressed()[0]:
                    for ball in balls:
                        if ball.center == self.topleft: continue
                        dist = ball.position.distance_to(self.topleft)
                        direction = Vector2(ball.position - Vector2(self.topleft)).normalize()
                        if dist < MAX_HOLE_DISTANCE:
                            norme = (1-(dist/MAX_HOLE_DISTANCE))*-puissance
                            print(dist)
                            ball.vector += direction * norme
            case "Black Hole":
                puissance = -power
                self.topleft = pygame.mouse.get_pos()
                pygame.draw.circle(self.surface,(50,50,50),self.topleft,290,10)
                if pygame.mouse.get_pressed()[0]:
                    for ball in balls:
                        if ball.center == self.topleft: continue
                        dist = ball.position.distance_to(self.topleft)
                        direction = Vector2(ball.position - Vector2(self.topleft)).normalize()
                        if dist < MAX_HOLE_DISTANCE:
                            norme = (1-(dist/MAX_HOLE_DISTANCE))*puissance
                            print(dist)
                            ball.vector += direction * norme
    
    def get_norm_velocity_not_null(self):
        if self.velocity != Vector2(0,0):
            return self.velocity.normalize()
        else:
            return Vector2(0,0)
    
    def explose(balls):
        
        pass
#endregion

#region Ball Class
class Ball(Rect):

    def __init__(self, surface, start_coordinate : Vector2 = Vector2(10,10), direction : Vector2 = Vector2(1,1), color = Color(255,255,255), tsize : int | None = None, twidth : int | None = None):
        self.topleft = start_coordinate
        #self.size = (30,30)
        self.screen_size = (1280,720)
        self.vector : Vector2 = direction
        self.speed_up = 0.8
        self.surface = surface
        self.color = color
        self.selected = False

        if tsize == None: self.tsize = random.randint(10,20)
        else: self.tsize = tsize
        if twidth == None: self.twidth = random.randint(4,6)
        else: self.twidth = twidth
        self.width, self.height = self.tsize*2, self.tsize*2
        #pygame.draw.circle(self.surface,self.color,self.center,self.tsize,self.twidth,True,True,True,True)
        #print("New Rect",self)
        self.position = Vector2(self.topleft) + Vector2(self.tsize)
    
    def screen_bounds_check(self, screen_bounds : Rect):
        if self.colliderect(screen_bounds):
            if self.bottom >= screen_bounds.bottom:
                #print("Bounce Down")
                self.vector.y = -abs(self.vector.y) * BALL_SCREEN_FRICTION
                self.position.y = screen_bounds.bottom - (self.size[1]/2)
                self.vector *= self.speed_up
            if self.left <= screen_bounds.left:
                #print("Bounce Left")
                self.vector.x = max(abs(self.vector.x) * BALL_SCREEN_FRICTION,0.1)
                self.vector *= self.speed_up
            if self.top <= screen_bounds.top:
                #print("Bounce Up")
                self.vector.y  = max(abs(self.vector.y) * BALL_SCREEN_FRICTION,0.1)
                self.vector *= self.speed_up

            if self.right >= screen_bounds.right:
                #print("Bounce Right")
                self.vector.x = min(-abs(self.vector.x) * BALL_SCREEN_FRICTION,-0.1)
                self.vector *= self.speed_up

    def static_ballrect_collision(self, other : Rect, other_vel : Vector2 = Vector2(0,0)):
        # autre = balle statique
        delta = Vector2(other.center) - self.position
        distance = delta.magnitude()

        if distance == 0:
            return
        if distance > self.tsize + other.width/2:
            return  # pas de collision

        # --- 1) Correction : reculer la balle mobile ---
        overlap = self.tsize + other.width/2 - distance
        direction = delta.normalize()

        # La balle statique ne bouge pas
        self.position -= direction * overlap

        # --- 2) Calcul du rebond ---
        normal = direction

        # Projection de la vitesse sur normal et tangent
        v_n = self.vector.dot(normal)      # composante normale
        v_t = self.vector.dot(Vector2(-normal.y, normal.x))  # tangent

        # Inversion de la composante normale (rebond)
        v_n = -v_n

        # Reconstruction de la vitesse
        tangent = Vector2(-normal.y, normal.x)
        self.vector = tangent * v_t + normal * v_n
        

    def collide_with_other_ball(self, other):
        # vecteur entre les deux centres
        delta : Vector2 = other.position - self.position
        distance = delta.magnitude()

        # --- 1) Détection de collision ---
        if distance == 0:
            return
        if distance > self.tsize + other.tsize:
            return  # pas de collision

        # --- 2) Correction : les séparer pour éviter la superposition ---
        overlap = self.tsize + other.tsize - distance
        direction = delta.normalize()

        self.position -= direction * (overlap / 2)
        other.position += direction * (overlap / 2)

        # --- 3) Collision élastique réaliste ---
        # Vecteur normal
        normal = direction

        # Vecteur tangent
        tangent = Vector2(-normal.y, normal.x)

        # Projections des vitesses
        v1n = self .vector.dot(normal)
        v1t = self .vector.dot(tangent)
        v2n = other.vector.dot(normal)
        v2t = other.vector.dot(tangent)

        # Échange des composantes normales (collision élastique)
        v1n, v2n = v2n, v1n

        # Reconstruction des vitesses
        self.vector = tangent * v1t + normal * v1n
        other.vector = tangent * v2t + normal * v2n

        # Mise à jour des rectangles
        #self.position = Vector2(self.position.x - self.tsize*2, self.position.y - (self.tsize*2))
        #self.position = Vector2(other.position.x - other.tsize*2, other.position.y - (other.tsize*2))
 

    def update(self,balls_list : list[Rect], cursor : CursorRect, other_col_rect: list[Rect] | list[Collition_Rect]):
        global BALLS_DELETED, BALL_OTHERS_FRICTION, BALL_SCREEN_FRICTION

        if self.selected:
            self.vector = Vector2(pygame.mouse.get_rel())
            self.position = Vector2(cursor.topleft)
            return pygame.draw.circle(self.surface,(255,255,255),self.position,self.tsize,self.twidth)

        #region Screen Bounds
        self.screen_bounds_check(Rect(VECTOR_ZERO,self.screen_size))
        #endregion Screen Bounds

        # Collition with every balls
        if len(balls_list) > 1:
            col_balls = self.collidelistall(balls_list)
            for collition in col_balls:
                self.collide_with_other_ball(balls_list[collition])

        self.vector += get_gravity()
        self.position += self.vector
        self.center = self.position
        return pygame.draw.circle(self.surface,self.color,self.position if self.vector.magnitude() > 1 else self.center,self.tsize,self.twidth)

#endregion

#region Game Class
class Game:
    def __init__(self) -> None:
        self.size = (1280,720)
        self.flags = pygame.SCALED
        self.running = True
        self.screen = pygame.display.set_mode(self.size,self.flags)
        self.clock = pygame.time.Clock()
        self.balls = list[Ball]
        self.col_rect = list[Collition_Rect]
        self.cursor = CursorRect(self.screen)
        self.ping = 1
        self.fps = 0
        pygame.key.set_repeat(700,40)
        self.text_cursor_mode = Text("Mode",28,"rubik",(0,0))
        self.text_cursor_moded = Text("2",28,"rubik",(0,0),(100,155,100))
        self.text_info = Text("Info :",20,"comic sans",(0,0))
        self.nice_text = Text("Nice Balls",24,"calibri",(0,0))
        self.power = 10
        tracemalloc.start()
    
    def summon_random_ball(self, pos : Vector2 = None):
        if pos is None:
            pos = Vector2(random.randint(0,self.size[0]),random.randint(0,self.size[1]))
        r_color = (random.randint(0,360),50,50,100)
        rand_color = Color(0,0,0,1)
        rand_color.hsla = r_color

        self.balls.append(Ball(self.screen,
            pos,
            Vector2(random.uniform(-1.0,1.0),random.uniform(-1.0,1.0)).normalize(),
            (rand_color)))


    def run(self):
        global BALLS_DELETED
        #region Run
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if askyesno("Quit ?","Tu veux vraiment quitter ?"):
                        pygame.quit()
                        self.running = False
                #endregion Run
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if len(self.balls) < MAX_BALLS:
                            r_color = (random.randint(0, 360),50,50,100)
                            rand_color = Color(0,0,0,1)
                            rand_color.hsla = r_color

                            self.balls.append(Ball(self.screen,
                                Vector2(random.randint(0,self.size[0]),random.randint(0,self.size[1])),
                                Vector2(random.uniform(-1.0,1.0),random.uniform(-1.0,1.0)).normalize(),
                                (rand_color)))
                    if event.key == pygame.K_BACKSPACE:
                        if len(self.balls) > 0:
                            self.balls.pop(len(self.balls)-1)
                            BALLS_DELETED += 1
                    if event.key == pygame.K_RETURN:
                        match(self.cursor.type):
                            case "Ball":
                                self.cursor.type = "Selector"
                            case "Selector":
                                self.cursor.type = "Eraser"
                            case "Eraser":
                                self.cursor.type = "White Hole"
                            case "White Hole":
                                self.cursor.type = "Black Hole"
                            case "Black Hole":
                                self.cursor.type = "Ball"
                    if event.key == pygame.K_1:
                        if len(self.balls)>100:
                            for i in range(len(self.balls)-1,100-1,-1):
                                del(self.balls[i])
                        else:
                            for i in range(len(self.balls),100,1):
                                self.summon_random_ball()
                            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        if self.cursor.type == "Ball":
                            if len(self.balls) < MAX_BALLS:
                                rel = pygame.mouse.get_rel()
                                tsize = random.randint(6,10)
                                self.balls.append(Ball(self.screen,
                                    Vector2(pygame.mouse.get_pos()) + (Vector2(rel) if rel != (0,0) else Vector2(1,1)).normalize()*tsize*2,
                                    Vector2(rel),
                                    (random.randint(50,200),
                                    random.randint(50,200),
                                    random.randint(50,200)),tsize))
                        elif self.cursor.type == "Selector":
                            index = self.cursor.collidelist(self.balls)
                            if index != -1:
                                self.cursor.selected_ball = index
                                self.balls[index].selected = True
                                print(index)
                if event.type == pygame.MOUSEBUTTONUP:
                    if not pygame.mouse.get_pressed()[0] and len(self.balls) > 0 and self.cursor.type == "Selector":
                        self.balls[self.cursor.selected_ball].selected = False
                        self.cursor.selected_ball = -1
                if event.type == pygame.MOUSEWHEEL:
                    self.power = pygame.math.clamp(self.power + event.y/10,1,100)

            if self.running:
                self.screen.fill((30,30,30))
                self.step()
                pygame.display.flip()
#endregion
    #region Game Step
    def step(self):
        delta_time = 1/max(self.clock.get_fps(),0.001)

        self.cursor.update(self.balls,self.col_rect,self.power,delta_time)
        self.screen.blit(self.text_cursor_mode.update("Cursor Type : "),(0,0))
        self.screen.blit(self.text_cursor_moded.update(self.cursor.type),(self.text_cursor_mode.getTextsize("Cursor Type : ")[0],0))
        if len(self.balls) > 0:
            self.screen.blit(self.text_info.update("Number of Balls : {}/{}".format(len(self.balls),MAX_BALLS)),(0,40))
            self.screen.blit(self.text_info.update("Deleted Balls : {}".format(BALLS_DELETED)),(0,70))
        self.screen.blit(self.text_info.update("FPS : " + str(round(self.clock.get_fps(),2))),(0,100))
        self.screen.blit(self.nice_text.update("Nice Ball Project"),(0,180))
        self.screen.blit(self.nice_text.update("Power : " + str(self.power)[0:4]),(1100,20))

        if tracemalloc_available:
            self.screen.blit(self.text_info.update(f"Memory : {convert_size(tracemalloc.get_traced_memory()[0])}, Peak : {convert_size(tracemalloc.get_traced_memory()[1])}"),(0,130))

        for balle in self.balls:
            balle.update(self.balls,self.cursor,self.col_rect)
        
        for rectangle in self.col_rect:
            rectangle.update()
        
        last_check = monotonic()
        
        tracemalloc.take_snapshot()            
        self.ping = self.clock.tick(60)
#endregion

if __name__ == "__main__":

    game = Game()
    game.balls = [Ball(game.screen,Vector2(20,20),Vector2(1,1),(224, 80, 147)),
                  Ball(game.screen,Vector2(100,100),Vector2(1,1),(224, 80, 147))]
    game.col_rect = [Collition_Rect(game.screen,Rect(200,200,100,50)),
                     Collition_Rect(game.screen,Rect(340,300,100,70)),
                     Collition_Rect(game.screen,Rect(900,400,50,100))]
    game.run()