from typing import Optional
import pygame

isNone = lambda x: (x == None)
pygame.font.init()

class Text():
    pos = pygame.Vector2(0,0)
    fontname = pygame.font.get_default_font()
    text = "None"
    size = 16
    font = pygame.font.Font(fontname,size)
    color = pygame.color.Color(255,255,255)

    def __init__(self,text:str, size:int, fontname:str, pos: pygame.Vector2 | None = None, color : pygame.Color | None = None) -> None:
        if pos != None: self.pos = pos
        if text != None: self.text = text
        if size != None: self.size = size
        if fontname != None: self.fontname = fontname
        if color != None: self.color = color
        self.font = pygame.font.SysFont(fontname,size)

    def changeSize(self,size:int):
        if size == None: raise ValueError("Size must be a number above 0 !")
        else: pygame.font.Font(self.fontname,size); self.size = size
    
    def getTextsize(self,text):
        return self.font.size(text)

    def update(self,text : str):
        self.surf = pygame.Surface(self.font.size(text),pygame.SRCALPHA)
        self.surf.fill((255,255,255,255)) #idk
        self.surf.blit(self.font.render(text,True,self.color,(0,0,0,0)),(0,0),special_flags=pygame.BLEND_RGBA_MULT)
        return self.surf