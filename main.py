import copy
import random
import time
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
        


            

class GameController():
    def __init__(self, random_seed=True) -> None:
        pygame.init()# init pygame
        pygame.display.set_caption("Minesweeper")
        self.screen = pygame.display.set_mode((2*SIDE+GRIDSIZE[1]*CELLSIZE,2*SIDE+GRIDSIZE[0]*CELLSIZE))
        pygame.Surface.fill(self.screen, (255,255,255))
        self.random_seed = random_seed
        self.start_game()
        self.font = pygame.font.SysFont('SF', 32)



    def start_game(self):
        self.grid = np.zeros(GRIDSIZE, np.uint8) # 0-8 for how many mines around, 9 for mines
        self.visible = np.zeros(GRIDSIZE, np.uint8) # 0 for not visible, 1 for visible, 2 for flag
        if self.random_seed:
            self.seed = random.randint(0,1000000)
        else:
            self.seed = 25
        random.seed(self.seed)

        self.all_pos = [(x,y) for x,y in listrange(GRIDSIZE)]
        self.all_pos_shuffled = self.all_pos
        random.shuffle(self.all_pos_shuffled)
        self.mine_pos = self.all_pos_shuffled[:MINES]
        self.flags_remaining = MINES
        self.start_time = time.time()

        
        
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

        print(self.grid)

    def show(self, pos):
        if self.grid[pos] == 0:
            def show_around(pos, grid, visible):
                x_pos = [max(0,pos[1]-1),min(pos[1]+2, GRIDSIZE[1])]
                y_pos = [max(0,pos[0]-1),min(pos[0]+2, GRIDSIZE[0])]
                # visible[x_pos[0]:x_pos[1],y_pos[0]:y_pos[1]] = 1
                grid_part = copy.copy(grid[y_pos[0]:y_pos[1],x_pos[0]:x_pos[1]])
                # visible_part = visible[x_pos[0]:x_pos[1],y_pos[0]:y_pos[1]]
                
                to_return = []
                visible[pos] = 1

                for i, x in enumerate(grid_part):
                    for i2, y in enumerate(x):
                        posx = x_pos[0]+i2
                        posy = y_pos[0]+i
                        if visible[posy,posx] == 0:
                            if y == 0:
                                to_return.append((posy,posx))
                        visible[posy,posx] = 1

                return to_return
            # self.visible[pos] = 1
            to_run = [pos]
            while len(to_run) > 0:
                next_r = to_run.pop(0)
                to_run+=show_around(next_r, self.grid, self.visible)
                

        elif 1 <= self.grid[pos] <= 8:
            if self.visible[pos] == 2:
                self.flags_remaining += 1
            self.visible[pos] = 1
        else:
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
                if newpos[0] < 0 or newpos[0] >= GRIDSIZE[1] or newpos[1] < 0 or newpos[1] >= GRIDSIZE[0]:
                    continue
                newpos = (newpos[1],newpos[0])
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
        # time.sleep(5)
        self.referee()


    def graphics(self):
        pygame.Surface.fill(self.screen, (255,255,255))
        for x in range(GRIDSIZE[1]+1):
            pygame.draw.line(self.screen, (0,0,0), (SIDE+x*CELLSIZE, SIDE), (SIDE+x*CELLSIZE, SIDE+CELLSIZE*GRIDSIZE[0]))
        for y in range(GRIDSIZE[0]+1):
            pygame.draw.line(self.screen, (0,0,0), (SIDE, SIDE+y*CELLSIZE), (SIDE+CELLSIZE*GRIDSIZE[1], SIDE+y*CELLSIZE))

        for y,x in listrange(GRIDSIZE):
            gi = self.grid[y,x]
            isvisible = self.visible[y,x]

            if isvisible == 1:
                text_surface = self.font.render(str(gi), False, (0,0,0))
                self.screen.blit(text_surface, (SIDE+10+x*CELLSIZE,SIDE+8+y*CELLSIZE))
            elif isvisible == 2:
                text_surface = self.font.render("F", False, (0,0,0))
                self.screen.blit(text_surface, (SIDE+10+x*CELLSIZE,SIDE+8+y*CELLSIZE))

        text_surface = self.font.render(str(self.flags_remaining), False, (0,0,0))
        self.screen.blit(text_surface, (16,16))
        text_surface = self.font.render(str(int(time.time()-self.start_time)), False, (0,0,0))
        self.screen.blit(text_surface, (SIDE+CELLSIZE*GRIDSIZE[1]+16,16))
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
            self.end_time = time.time()
            self.duration = self.end_time-self.start_time
            print("The bombs were found in {} seconds. You did not explode! (SEED: {})".format(self.duration, self.seed))
            exit()

            
            
        


if __name__=="__main__":
    gc = GameController()

    while 1:
        gc.update()