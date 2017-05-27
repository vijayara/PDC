from PIL import Image
import textwrap
from image_decoding import *
import pygame, sys
import pygame.camera
from pygame.locals import *


def take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5):
    N_COLORS = n_tons**3
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.camera.init()
    
    RESOLUTION = (1280, 720)
    cam = pygame.camera.Camera("/dev/video0", RESOLUTION)
    cam.start()
    USABLE_RECT = (RESOLUTION[0]//3, RESOLUTION[1]//3)*2
        
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    FILENAME = 'shots/pic'
    
    preparation = 1
    run = 1
    grand_final = 1

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
    

    # add every image into a PIL list
    for i in range(1, len(images)):
        string_image = pygame.image.tostring(images[i], 'RGB', False)
        PIL_image = Image.frombytes('RGB', USABLE_RECT[2:], string_image)
        PIL_images.append(PIL_image)
        PIL_image.save(FILENAME+str(i)+'.png')
        print("Interval", str(i-1)+"-"+str(i)+": "+str(times[i]-times[i-1]))
    
    # decode the images into a string
    decoded_text = decodeImage(PIL_images, N_COLORS, coding, rows, columns)

    # save the decoded message in a file
    with open("output.txt", "w") as text_file:
        print(decoded_text, file=text_file)
    
    # print the decoded message in terminal
    print(decoded_text)

    # Display the decoded message in the screen as soon as it is decoded
    text_to_display =  decoded_text.replace('\r', ' ').replace('\n', ' ')
    lines = textwrap.wrap(text_to_display, 100)
    display.fill((255, 255, 255))
    myfont = pygame.font.SysFont("ubuntu", 22, True)
    text_rect = pygame.Rect(50, 50, 50, 1200)
    while lines:
        line = lines[0]
        lines.pop(0)

        label = myfont.render(line, 10, (41, 83, 80))
        display.blit(label, text_rect)
        text_rect.centery += 40
    pygame.display.flip()

    # displays the message until we push on "q"
    while grand_final:
        for event in pygame.event.get():
            if (event.type == KEYDOWN and event.key == K_q):
                grand_final = 0
    
    pygame.quit()
    
    # save the images in the disk (to have a )
    #for i in range(len(PIL_images)):
    #    PIL_images[i].save(FILENAME+str(i)+'.png')

config_safe = (110, 2, 10, 3, 5)
config1 = (110, 2, 30, 4, 6)

# take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5):   
take_shots(*config1)
