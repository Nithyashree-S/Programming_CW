# - Ed's code
import pygame
from pygame.locals import *
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

#need global?
#colours
black = (0, 0, 0)
blue = (100, 100, 255)
green = (53, 101, 77)
red = (186, 0, 0)

#texts - Ed's code
Welcome_text = "Welcome to Notty - click start"
Begin_game_Text = "Begin Game"
Click_to_shuffle_text = "Shuffle cards"
Shuffling_text = "Shuffling..."
Click_to_deal_text = "Deal cards"
Dealing_text = "Dealing..."
Winning_Text = "You Win!"
Draw_Card_Text = "Draw card"
Card_Drawn_Text = "Card Drawn"

#default screen class - Daniels code modified by Ed
class Screen:
    def __init__(self, colour):
        self.colour = colour
        self.objects = []

    def render(self, screen):
        screen.fill(self.colour)
        for object in self.objects:
            object.render(screen)
        
    def update(self):
        for object in self.objects:
            object.update()

#class to change the screen to another - Ed's code
class Change_Screen:
    def __init__(self):
        self.current_screen = None
    
    def render(self, screen):
        if self.current_screen:
            self.current_screen.render(screen)
        
    def update(self):
        if self.current_screen:
            self.current_screen.update() 

    def define_screen(self, screen):
        self.current_screen = screen

# differnet types of screens - Ed's code
class Start_Screen(Screen):
    def __init__(self):
        super().__init__(blue)
        #screen text
        self.objects.append(Text(Welcome_text, (250, 50), black))
        #load images
        start_button_image = pygame.image.load('start-button-vector.png').convert_alpha()
        #add button to object list
        self.objects.append(StartButton(250, 200, start_button_image, 0.2))

class Winning_Screen(Screen):
    def __init__(self):
        super().__init__(red)
        #screen text
        self.objects.append(Text(Winning_Text, (250, 50), black))
        #load images
        exit_button_image = pygame.image.load('Exit-button.png').convert_alpha()
        #add button to object list
        self.objects.append(ExitButton(50, 400, exit_button_image, 0.6))

    def render(self, screen):
        super().render(screen)

    def update(self):
        self.exit.update()

# - Ed's code
class Game_Screen(Screen):
    def __init__(self):
        super().__init__(green)
        #display welcome text - Ed's code
        self.objects.append(Text(Begin_game_Text, (350, 50), black))
        #load images
        shuffle_button_image = pygame.image.load('shuffle_icon.png').convert_alpha()
        deal_button_image = pygame.image.load('deal_hand_icon.png').convert_alpha()
        draw_button_image = pygame.image.load('card-draw.png').convert_alpha()
        exit_button_image = pygame.image.load('Exit-button.png').convert_alpha()

        #add buttons to objects list
        self.objects.append(ShuffleButton(50, 400, shuffle_button_image, 0.6))
        self.objects.append(DealButton(200, 400, deal_button_image, 0.5))
        self.objects.append(DrawButton(350, 400, draw_button_image, 0.35))
        self.objects.append(ExitButton(600, 450, exit_button_image, 0.6))


        #button instruction text
        self.shuffle_text = (Text(Click_to_shuffle_text, (50, 550), black))
        self.deal_text = (Text(Click_to_deal_text, (200, 550), black))
        self.draw_text = (Text(Draw_Card_Text, (350, 550), black))

        #button click text
        self.objects.append(self.shuffle_text)
        self.objects.append(self.deal_text)
        self.objects.append(self.draw_text)


    def render(self, screen):
        super().render(screen)

    def update(self):
#        self.ShuffleButton.update()
#        self.DealButton.update()
#        self.DrawButton.update()
# - Ed's code
        for object in self.objects:
            if isinstance(object, Button):
                object.update()
        #if buttons are clicked do (x)
            if isinstance(object, ShuffleButton) and object.check_clicked():
                self.shuffle_text.text = Shuffling_text
                pass             #INSERT SHUFFLE LOGIC?********************************************************************************************************************
            if isinstance(object, DealButton) and object.check_clicked():
                self.deal_text.text = Dealing_text
                pass             #INSERT DEAL LOGIC?********************************************************************************************************************
            elif isinstance(object, DrawButton) and object.check_clicked():
                self.draw_text.text = Card_Drawn_Text
                pass             #INSERT DRAW LOGIC?********************************************************************************************************************

#generic graphic object class - from Daniel's lecture code
class Graphic:
    def __init__(self):
        pass

    def render(self, screen):
        pass

    def update(self):
        pass

#text type graphic object - modified from Daniel's lecture code
class Text(Graphic):
    def __init__(self, text, position, colour):
        self.text = text
        self.position = position
        self.colour = colour
        self.size = 30
        self.font = pygame.font.SysFont(None, self.size)

    def render(self, screen):
        image = self.font.render(self.text, True, self.colour)
        self.width = image.get_width()
        self.height = image.get_height()
        screen.blit(image, self.position)

#button type graphic object - from Daniel's lecture code
class Button(Graphic):
    def __init__(self, x, y, image, scale):#, name=None):
        super().__init__()
        self.unscaled_image = image
#        self.name = name
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rectangle = self.image.get_rect()
        self.rectangle.topleft = (x, y)
        self.click = False

    def render(self, screen):
        screen.blit(self.image, (self.rectangle.x, self.rectangle.y))

    def update(self):
        #check mouse hovering over button
# modified by Ed from this tutorial: https://www.youtube.com/watch?v=G8MYGDf_9ho
        curser_position = pygame.mouse.get_pos()
        if self.rectangle.collidepoint(curser_position):
            #scale up button at hover
            self.image = pygame.transform.scale(self.unscaled_image, (int(self.rectangle.width * 1.1), int(self.rectangle.height * 1.1)))
            #if clicked return to default scale
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                self.click = True
                self.image = pygame.transform.scale(self.image, (int(self.rectangle.width), int(self.rectangle.height)))
            elif pygame.mouse.get_pressed()[0] == 0:
                self.click = False
        else:
            #reset when not hover
            self.image = pygame.transform.scale(self.unscaled_image, (int(self.rectangle.width), int(self.rectangle.height)))

    def check_clicked(self):
        return self.click     

#classes for each button type - Ed's code
class StartButton(Button):
    def __init__ (self, x, y, image, scale):
        super().__init__(x, y, image, scale)

class ShuffleButton(Button):
    def __init__ (self, x, y, image, scale):
        super().__init__(x, y, image, scale)

class DealButton(Button):
    def __init__ (self, x, y, image, scale):
        super().__init__(x, y, image, scale)

class DrawButton(Button):
    def __init__ (self, x, y, image, scale):
        super().__init__(x, y, image, scale)

class ExitButton(Button):
    def __init__ (self, x, y, image, scale):
        super().__init__(x, y, image, scale)

#game loop - Ed's code (a bit messy and in progress)
def notty_loop():

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Notty Game')

    start_screen = Start_Screen()
    game_screen = Game_Screen()
    winning_screen = Winning_Screen()
    change_screen = Change_Screen()

    change_screen.define_screen(start_screen)

    game_running = True

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False #exit game
#MOVE BUTTON PRESS LOGIC TO screen classes to simplify game loop~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #check button click and do something (e.g. go to new screen) - start screen/main screen switch logic
        current_screen = change_screen.current_screen
        for object in current_screen.objects:
            if isinstance(object, Button) and object.check_clicked():
                if isinstance(current_screen, Start_Screen) and isinstance(object, StartButton):#object.name == "start_button":
                    change_screen.define_screen(game_screen)
                elif isinstance(current_screen, Winning_Screen) and isinstance(object, ExitButton):
                    change_screen.define_screen(start_screen)
#                elif isinstance(current_screen, Game_Screen):
#                    if isinstance(object, ShuffleButton):
#                        pass #insert Shuffle logic?
#                    if isinstance(object, DealButton):
#                        pass #insert Deal logic?
#                    elif isinstance(object, DrawButton):
#                        pass #insert Draw logic?
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        change_screen.update()
        change_screen.render(screen)
        pygame.display.flip()
        pygame.time.wait(20)

    pygame.quit()

notty_loop()        
