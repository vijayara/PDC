from PIL import Image
from tmp_image_decoding import *
import pygame, sys
import pygame.camera
from pygame.locals import *


def take_shots(n_shots=20, capture_interval=1000, n_tons=2):
    N_COLORS = n_tons**3
    pygame.init()
    pygame.camera.init()
    
    RESOLUTION = (1280, 720)
    cam = pygame.camera.Camera("/dev/video0", RESOLUTION)
    cam.start()
    USABLE_RECT = (RESOLUTION[0]//3, RESOLUTION[1]//3)*2
        
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    FILENAME = 'shots/pic'
    
    preparation = 1
    run = 1
    images = []
    PIL_images = []
    times = []
    while preparation:
        display.blit(cam.get_image().subsurface(USABLE_RECT), (0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.time.delay(1000)# you have 1 sec to remove hands of canal
                cam.get_image()# needed to refresh camera
                pygame.time.set_timer(USEREVENT, capture_interval)
                preparation = 0
                display.fill((0,0,0))
                pygame.display.flip()
            if event.type == KEYDOWN and event.key == K_q:
                preparation = 0
                run = 0
                cam.stop()
                pygame.quit()
    while run:
        for event in pygame.event.get():
            if event.type == USEREVENT:
                image = cam.get_image().subsurface(USABLE_RECT)
                images.append(image)
                times.append(pygame.time.get_ticks())
            if (event.type == KEYDOWN):
                run = 0
                cam.stop()
                pygame.quit()
    
    print("Number of images:" + str(len(images)))
    for i in range(1, len(images)):
        string_image = pygame.image.tostring(images[i], 'RGB', False)
        PIL_image = Image.frombytes('RGB', USABLE_RECT[2:], string_image)
        PIL_images.append(PIL_image)
        PIL_image.save(FILENAME+str(i)+'.png')
        print("Interval", str(i-1)+"-"+str(i)+": "+str(times[i]-times[i-1]))
    
    decoded_text = decodeImage(PIL_images, N_COLORS)
    print(decoded_text)
    
                
take_shots(10, 110)
