import random
from constants import *

import pygame
from pygame.locals import *

import numpy as np

def listrange(x:list):
    if type(x) == int:
        return range(x)
    elif type(x) == list or type(x) == tuple:
        def loop(lst,d=0):
            if d < len(lst)-1:
                r = loop(lst,d+1)
                return [[i]+t for i in range(lst[d]) for t in r]
            else:
                return [[x] for x in range(lst[d])]
        return loop(x)
        
seed = 25

random.seed(seed)
            

class GameController():
    def __init__(self) -> None:
        pygame.init()# init pygame
        pygame.display.set_caption("Minesweeper")
        self.screen = pygame.display.set_mode((2*SIDE+GRIDSIZE[0]*CELLSIZE,2*SIDE+GRIDSIZE[1]*CELLSIZE))
        pygame.Surface.fill(self.screen, (255,255,255))
        self.start_game()
        self.font = pygame.font.SysFont('SF', 32)



    def start_game(self):
        self.grid = np.zeros(GRIDSIZE, np.uint8) # 0-8 for how many mines around, 9 for mines
        self.visible = np.zeros(GRIDSIZE, np.uint8) # 0 for not visible, 1 for visible, 2 for flag
        self.all_pos = [(x,y) for x,y in listrange(GRIDSIZE)]
        self.all_pos_shuffled = self.all_pos
        random.shuffle(self.all_pos_shuffled)
        self.mine_pos = self.all_pos_shuffled[:MINES]
        self.flags_remaining = MINES

        to_add = []
        for (ox,oy) in self.mine_pos:
            for x in range(ox-1, ox+2):
                for y in range(oy-1, oy+2):
                    if (x,y) == (ox,oy):
                        continue
                    if x >= 0 and y >= 0 and x < GRIDSIZE[0] and y < GRIDSIZE[1]:

                        self.grid[x,y] += 1


        for x,y in self.mine_pos:
            self.grid[x,y] = 9

    def show(self, pos):
        # if self.grid[pos] == 0:
        #     self.visible[pos] = 1
        # elif 1 <= self.grid[pos] <= 8:
        #     self.visible[pos] = 1
        self.visible[pos] = 1
        

    def flag(self, pos):
        if self.visible[pos] == 1:
            pass
        elif self.visible[pos] == 2:
            self.visible[pos] = 0
            self.flags_remaining += 1
        elif self.visible[pos] == 0 and self.flags_remaining > 0:
            self.visible[pos] = 2
            self.flags_remaining -= 1


    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == MOUSEBUTTONUP:
                pos = event.pos
                newpos = (pos[0] - SIDE, pos[1] - SIDE)
                newpos = (newpos[0]//CELLSIZE, newpos[1]//CELLSIZE)
                if newpos[0] < 0 or newpos[0] >= GRIDSIZE[0] or newpos[1] < 0 or newpos[1] >= GRIDSIZE[1]:
                    continue
                if event.button == 1:
                    self.show(newpos)
                elif event.button == 3:
                    self.flag(newpos)
            elif event.type == KEYDOWN:
                if event.key == K_r:
                    self.start_game()
                if event.key == K_q:
                    exit()

        
        self.graphics()
        self.referee()


    def graphics(self):
        pygame.Surface.fill(self.screen, (255,255,255))
        for x in range(GRIDSIZE[0]+1):
            pygame.draw.line(self.screen, (0,0,0), (SIDE, SIDE+x*CELLSIZE), (SIDE+CELLSIZE*GRIDSIZE[0], SIDE+x*CELLSIZE))
        for y in range(GRIDSIZE[1]+1):
            pygame.draw.line(self.screen, (0,0,0), (SIDE+y*CELLSIZE, SIDE), (SIDE+y*CELLSIZE, SIDE+CELLSIZE*GRIDSIZE[1]))

        for x,y in listrange(GRIDSIZE):
            gi = self.grid[x,y]
            isvisible = self.visible[x,y]

            if isvisible == 1:
                text_surface = self.font.render(str(gi), False, (0,0,0))
                self.screen.blit(text_surface, (SIDE+10+x*CELLSIZE,SIDE+8+y*CELLSIZE))
            elif isvisible == 2:
                text_surface = self.font.render("F", False, (0,0,0))
                self.screen.blit(text_surface, (SIDE+10+x*CELLSIZE,SIDE+8+y*CELLSIZE))

        text_surface = self.font.render(str(self.flags_remaining), False, (0,0,0))
        self.screen.blit(text_surface, (16,16))
        pygame.display.update()

    def referee(self):
        completed = True
        for x,y in listrange(GRIDSIZE):
            state = self.grid[x,y]
            visible = self.visible[x,y]
            if state == 9 and visible == 1:
                print("YOU EXPLODED")
                exit()
            if visible == 0:
                completed = False
            
        if completed:
            for x,y in listrange(GRIDSIZE):
                state = self.grid[x,y]
                visible = self.visible[x,y]
                if state != 9 and visible == 2:
                    print("BAD FLAG")
                    completed = False

        if completed:
            print("The bombs were found. You did not explode!")
            exit()

            
            
        


if __name__=="__main__":
    gc = GameController()

    while 1:
        gc.update()