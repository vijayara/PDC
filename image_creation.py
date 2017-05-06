import math
import pygame
from pygame.locals import *


def camstream():
    pygame.init()
    pygame.mouse.set_visible(False)
    
    #total screen size
    SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    #separating cross width
    CROSS_SIZE = 30
    QUADRANT_SIZE = ((SIZE[0]-CROSS_SIZE)/2, (SIZE[1]-CROSS_SIZE)/2)
    #quadrant offsets
    W_OFFSET = QUADRANT_SIZE[0] + CROSS_SIZE
    H_OFFSET = QUADRANT_SIZE[1] + CROSS_SIZE
    
    #number of lines and columns per quadrant
    LINE = 3
    COLUMN = 3
    
    #number of possible levels for each color
    N_TONS = 2
    TON = [(i)*255/(N_TONS-1) for i in range(0, N_TONS)]

    #number of colors
    N_COLORS = N_TONS**3
    
    COMBINATIONS = N_TONS**(3*LINE*COLUMN)
    BITS_BY_QUADRAND = math.log(COMBINATIONS, 2)
    
    # 0 0 0
    # 255 0 0
    # 0 255 0
    # 255 255 0
    # 0 0 255
    # 255 0 255
    # 0 255 255
    # 255 255 255
    #
    # most distances are colors 1, 2, 4, 7
    COLOR = []
    for i in range(0, N_TONS):
        for j in range(0, N_TONS):
            for k in range (0, N_TONS):
                color = ((TON[i], TON[j], TON[k]))
                COLOR.append(color)
    
    MOST_DISTANCES = []
    for i in range (0, 3):
        MOST_DISTANCES.append((N_TONS**i)*(N_TONS-1))
    MOST_DISTANCES.append(N_COLORS-1)
        
    display = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    screen = [pygame.surface.Surface(QUADRANT_SIZE, 0, display)]*4
    
    for i in range(0, 4):
        screen[i].fill(COLOR[MOST_DISTANCES[i]])
        display.blit(screen[i], (((i&1)*W_OFFSET), ((i&2)>>1)*H_OFFSET))
    
    capture = True
    while capture:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                capture = False
    pygame.quit()
    return

camstream()
