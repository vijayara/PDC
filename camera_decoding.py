import pygame, sys
import pygame.camera
from pygame.locals import *

def take_shots(n_shots=20, capture_interval=1000):
    pygame.init()
    pygame.camera.init()
    SIZE = (480, 320)
    RESOLUTION = (1280, 720)
    
    FILENAME = 'shots/pic'
    
    display = pygame.display.set_mode(SIZE, 0)
    cam = pygame.camera.Camera("/dev/video0", RESOLUTION)
    cam.start()
    
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
                    image = cam.get_image()
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
