import pygame, sys
import pygame.camera
from pygame.locals import *

def closest_color(detected_color, n_tons):
    delta = 256//(2*(n_tons-1))

    r = ((detected_color[0]+delta)*(n_tons-1))//255
    g = ((detected_color[1]+delta)*(n_tons-1))//255
    b = ((detected_color[2]+delta)*(n_tons-1))//255
    
    color_index = r*n_tons**2 + g*n_tons + b
    return color_index

def take_shots(n_shots=20, capture_interval=1000):
    pygame.init()
    pygame.camera.init()
    
    RESOLUTION = (1280, 720)
    cam = pygame.camera.Camera("/dev/video0", RESOLUTION)
    cam.start()
    USABLE_RECT = (RESOLUTION[0]//3, RESOLUTION[1]//3)*2
    
    SIZE = (480, 320)
    display = pygame.display.set_mode(SIZE, 0)
    FILENAME = 'shots/pic'
    
    run = 1
    images = []
    times = []
    while run:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.time.set_timer(USEREVENT, capture_interval)
                # take one more shot because we throw away the 1st one
                pygame.time.set_timer(USEREVENT+1, (n_shots+1)*capture_interval+100)
            if event.type == USEREVENT:
                if cam.query_image():
                    image = cam.get_image().subsurface(USABLE_RECT)
                    images.append(image)
                    times.append(pygame.time.get_ticks())
                else:
                    print("CAMERA NOT READY")
            if (event.type == USEREVENT+1) or (event.type == QUIT):
                run = 0
                cam.stop()
                pygame.quit()
    print("Number of images:" + str(len(images)))
    for i in range(len(images)-1):
        pygame.image.save(images[i+1], FILENAME+str(i+1)+'.jpg')
        print("Interval", str(i)+"-"+str(i+1)+": "+str(times[i+1]-times[i]))
    
                
take_shots(100, 110)
