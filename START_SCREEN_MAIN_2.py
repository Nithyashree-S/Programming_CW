import pygame
import button2
import os

SCREEN_HEIGHT = 768
SCREEN_WIDTH = 1024

pygame.init()

black = (0, 0, 0)
blue = (173, 216, 230)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Notty game start')
font = pygame.font.SysFont("Arial", 36)

#image paths
GAME_IMAGES = "game_images/"
START_IMAGE_PATH = os.path.join(GAME_IMAGES, "start-button-vector.png")
EXIT_IMAGE_PATH = os.path.join(GAME_IMAGES, "Exit-button.png")

#load button images
start_button_image = pygame.image.load(START_IMAGE_PATH).convert_alpha()
exit_button_image = pygame.image.load(EXIT_IMAGE_PATH).convert_alpha()

#create buttons
start_button = button2.Button(370, 300, start_button_image, 0.2)
exit_button = button2.Button(450, 450, exit_button_image, 0.5)

#Notty loop
def start_screen():
    running = True
    while running:
        #screen colour
        screen.fill(blue)
        
        #if start button clicked: run main game
        if start_button.draw(screen):
            return True

        #if exit button clicked: Quit Game
        if exit_button.draw(screen):
            return False

        #events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
        txtsurface = font.render("Welcome to Notty!", True, black)
        screen.blit(txtsurface,(512 - txtsurface.get_width() // 2, 150 - txtsurface.get_height() // 2))
        pygame.display.update()

    return False
