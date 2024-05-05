import sys, math, random

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
MAX_BALLS = 350
FPS = 60
BALLS_DELETED = 0
CURRENT_BALL = -1
BALL_SCREEN_FRICTION = 1
BALL_OTHERS_FRICTION = 0.9
MAX_HOLE_DISTANCE = 300

gravity = 0.05

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

        print("""
              Top Left : {0} <-> {1}
              Bottom Right : {2} <->  {3}

              Size : {4}
              
              """.format(self.topleft, rect.topleft, self.bottomright, rect.bottomright, rect.size))

    def update(self):
        #pygame.draw.rect(self.surface,self.color,self,self.tsize)
        
        pygame.draw.rect(self.surface,self.color,self.recttop,5)#self.tsize)
        pygame.draw.rect(self.surface,self.color,self.rectleft,5)#self.tsize)
        pygame.draw.rect(self.surface,self.color,self.rectright,5)#self.tsize)
        pygame.draw.rect(self.surface,self.color,self.rectbottom,5)#self.tsize)
        #print(self)
        self.suprise = max(0,self.suprise - 0.05)
        #self.tsize = 5 + self.suprise

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
        self.magn_max = 50
        self.tsize = 5
        self.speed = 0.0
        self.type = "Ball"
        self.selected_ball = -1

    def update(self,balls : list[Rect], rects : list[Rect], power : float):
        global BALLS_DELETED
        self.velocity = Vector2(pygame.mouse.get_rel())
        self.speed = self.velocity.magnitude()
        match(self.type):
            case "Ball":
                if self.velocity != VECTOR_ZERO:
                    self.tsize = pygame.math.clamp(
                        self.velocity.magnitude()*2,
                        self.size_min,
                        self.size_max)
                else: 
                    self.tsize = self.size_min

                self.rect = pygame.draw.circle(self.surface,self.color,pygame.mouse.get_pos(),self.tsize,5)
                self.topleft = self.rect.topleft
                self.width, self.height = self.tsize*2,self.tsize*2

            case "Selector":
                self.topleft = pygame.mouse.get_pos()
                """
                if pygame.mouse.get_pressed()[0]:
                    print("Pressed")
                    for ball in balls:
                        if ball.collidepoint(self.topleft):
                            ball.circle_direction = VECTOR_ZERO
                            ball.center = self.topleft
                """
                pass

            case "Eraser":
                self.topleft = pygame.mouse.get_pos()
                index = self.collidelist(balls)
                if index != -1:
                    del(balls[index])
                    BALLS_DELETED += 1
                    #print(index)
            case "White Hole":
                puissance = power
                self.topleft = pygame.mouse.get_pos()
                pygame.draw.circle(self.surface,(50,50,50),self.topleft,290,10)
                if pygame.mouse.get_pressed()[0]:
                    for ball in balls:
                        dist = Vector2(ball.center).distance_to(self.topleft)
                        direction = Vector2(Vector2(ball.center) - Vector2(self.topleft)).normalize()
                        if dist < MAX_HOLE_DISTANCE:
                            norme = int((1-dist/MAX_HOLE_DISTANCE)*puissance)
                            print(dist)
                            ball.circle_direction += direction * norme
                        



    
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
        self.circle_direction = direction
        self.speed = 3
        self.speed_up = 0.1
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

    def update(self,balls_list : list[Rect], cursor : CursorRect, other_col_rect: list[Rect] | list[Collition_Rect]):
        global gravity, BALLS_DELETED

        #region Screen Bounds
        if self.left <= 0:
            #print("Bounce Left")
            self.circle_direction[0] = 1
            self.speed += self.speed_up
        if self.top <= 0:
            #print("Bounce Up")
            self.circle_direction[1] = 1
            self.speed += self.speed_up

        if self.right >= self.screen_size[0]:
            #print("Bounce Right")
            self.circle_direction[0] = -1
            self.speed += self.speed_up

        if self.bottom >= self.screen_size[1]:
            #print("Bounce Down")
            self.circle_direction[1] = -abs(self.circle_direction[1])
            self.bottom = self.screen_size[1]
            self.speed += self.speed_up
        #endregion Screen Bounds
        
        # Collide with the cursor
        if self.colliderect(cursor):
            if cursor.type == "Ball":
                if Vector2(Vector2(self.center) - Vector2(cursor.center)) != VECTOR_ZERO:
                    self.circle_direction = Vector2(Vector2(self.center) - Vector2(cursor.center)).normalize()
            else:
                pass

        # Collition with every balls
        if len(balls_list) > 1:
            col_balls = self.collidelistall(balls_list)
            for collition in col_balls:
                if balls_list[collition] != self:
                    #print(self, "<->" ,balls_list[collition])
                    if (Vector2(self.center) - Vector2(balls_list[collition].center)) != Vector2(0,0):
                        self.circle_direction = Vector2(Vector2(self.center) - Vector2(balls_list[collition].center)).normalize()
                        balls_list[collition].circle_direction = Vector2(Vector2(balls_list[collition].center - Vector2(self.center))).normalize()
                    else:
                        del balls_list[collition]
                        balls_list.remove(self)
                        BALLS_DELETED += 2

        # Collition with rectangle
        if len(other_col_rect) > 0:
            for rectangle in other_col_rect:
                if self.colliderect(rectangle.recttop):
                    self.circle_direction.y = -abs(self.circle_direction.y)
                if self.colliderect(rectangle.rectleft):
                    self.circle_direction.x = -abs(self.circle_direction.x)
                if self.colliderect(rectangle.rectright):
                    self.circle_direction.x = abs(self.circle_direction.x)
                if self.colliderect(rectangle.rectbottom):  
                    self.circle_direction.y = abs(self.circle_direction.y)
                """
                if self.colliderect(rectangle.recttop) or self.colliderect(rectangle.rectbottom):
                    self.circle_direction.y *= -1
                elif self.colliderect(rectangle.rectleft) or self.colliderect(rectangle.rectright):
                    self.circle_direction.x *= -1
                """
                    
        if self.selected:
            self.circle_direction = VECTOR_ZERO
            self.center = cursor.topleft
            return pygame.draw.circle(self.surface,(255,255,255),self.center,self.tsize,self.twidth)
        else:
            self.circle_direction = Vector2(self.circle_direction + Vector2(0,gravity))
            self.topleft += self.circle_direction * 3 #* self.speed
            return pygame.draw.circle(self.surface,self.color,self.center,self.tsize,self.twidth)


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
        self.text_cursor_mode = Text("Mode",28,"impact",(0,0))
        self.text_cursor_moded = Text("2",28,"impact",(0,0),(200,255,200))
        self.text_info = Text("Info :",20,"comic sans",(0,0))
        self.nice_text = Text("Nice Balls",24,"calibri",(0,0))
        self.power = 10
        tracemalloc.start()
    
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
                            self.balls.append(Ball(self.screen,
                                Vector2(random.randint(0,self.size[0]),random.randint(0,self.size[1])),
                                Vector2(random.uniform(-1.0,1.0),random.uniform(-1.0,1.0)).normalize(),
                                (random.randint(50,200),
                                random.randint(50,200),
                                random.randint(50,200))))
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
                            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        if self.cursor.type == "Ball":
                            if len(self.balls) < MAX_BALLS:
                                self.balls.append(Ball(self.screen,
                                    Vector2(pygame.mouse.get_pos()),
                                    Vector2(pygame.mouse.get_rel()),
                                    (random.randint(50,200),
                                    random.randint(50,200),
                                    random.randint(50,200))))
                        elif self.cursor.type == "Selector":
                            index = self.cursor.collidelist(self.balls)
                            if index != -1:
                                self.cursor.selected_ball = index
                                self.balls[index].selected = True
                                print(index)
                if event.type == pygame.MOUSEBUTTONUP:
                    if not pygame.mouse.get_pressed()[0] and len(self.balls) > 0:
                        self.balls[self.cursor.selected_ball].selected = False
                        self.cursor.selected_ball = -1
                if event.type == pygame.MOUSEWHEEL:
                    self.power += event.y/10

            if self.running:
                self.screen.fill((30,30,30))
                self.step()
                pygame.display.flip()
#endregion
    #region Game Step
    def step(self):
        #if pygame.key.get_pressed()[pygame.K_SPACE]:
        #    self.balls.append(Ball(self.screen,
        #                        Vector2(random.randint(0,self.size[0]),random.randint(0,self.size[1])),
        #                        Vector2(random.uniform(-1.0,1.0),random.uniform(-1.0,1.0)).normalize(),
        #                        (random.randint(50,200),
        #                        random.randint(50,200),
        #                        random.randint(50,200))))

        self.cursor.update(self.balls,self.col_rect,self.power)
        self.screen.blit(self.text_cursor_mode.update("Cursor Type : "),(0,0))
        self.screen.blit(self.text_cursor_moded.update(self.cursor.type),(self.text_cursor_mode.getTextsize("Cursor Type : ")[0],0))
        if len(self.balls) > 0:
            self.screen.blit(self.text_info.update("Number of Balls : {}/{}".format(len(self.balls),MAX_BALLS)),(0,40))
            self.screen.blit(self.text_info.update("Deleted Balls : {}".format(BALLS_DELETED)),(0,70))
        self.screen.blit(self.text_info.update("FPS : " + str(round(self.clock.get_fps(),2))),(0,100))
        if tracemalloc_available:
            self.screen.blit(self.text_info.update(f"Memory : {convert_size(tracemalloc.get_traced_memory()[0])}, Peak : {convert_size(tracemalloc.get_traced_memory()[1])}"),(0,130))
        self.screen.blit(self.nice_text.update("Nice Ball Project"),(0,180))
        self.screen.blit(self.nice_text.update("Power : " + str(self.power)[0:4]),(1100,20))

        for balle in self.balls:
            balle.update(self.balls,self.cursor,self.col_rect)
        
        for rectangle in self.col_rect:
            rectangle.update()
        
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