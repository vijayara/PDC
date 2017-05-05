import pygame
from pygame.locals import *


def camstream():
    pygame.init()
    pygame.mouse.set_visible(False)
    
    #total screen size
    SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    #separating cross width
    CROSS_SIZE = 50
    QUADRANT_SIZE = ((SIZE[0]-CROSS_SIZE)/2, (SIZE[1]-CROSS_SIZE)/2)
    #quadrant offsets
    W_OFFSET = QUADRANT_SIZE[0] + CROSS_SIZE
    H_OFFSET = QUADRANT_SIZE[1] + CROSS_SIZE
    
    #number of possible levels for each color
    N_TONS = 2
    TON = [(i)*255/(N_TONS-1) for i in range(0, N_TONS)]
    
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

        
    display = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    
    screen1 = pygame.surface.Surface(QUADRANT_SIZE, 0, display)
    screen2 = pygame.surface.Surface(QUADRANT_SIZE, 0, display)
    screen3 = pygame.surface.Surface(QUADRANT_SIZE, 0, display)
    screen4 = pygame.surface.Surface(QUADRANT_SIZE, 0, display)
    
    screen1.fill(COLOR[1])
    screen2.fill(COLOR[2])
    screen3.fill(COLOR[4])
    screen4.fill(COLOR[7])
    
    display.blit(screen1, (0,0))
    display.blit(screen2, (W_OFFSET,0))
    display.blit(screen3, (0,H_OFFSET))
    display.blit(screen4, (W_OFFSET,H_OFFSET))
    
    capture = True
    while capture:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                capture = False
    pygame.quit()
    return

camstream()
