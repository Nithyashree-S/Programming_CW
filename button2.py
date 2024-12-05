import pygame

#button class
class Button(): #changed from inheriting Graphic default class to just Button class
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.unscaled_image = image
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rectangle = self.image.get_rect()
        self.rectangle.topleft = (x, y)
        self.clicked = False

    def draw(self, screen):
        click = False
        screen.blit(self.image, (self.rectangle.x, self.rectangle.y))

        #check mouse hovering over button
        curser_position = pygame.mouse.get_pos()

        if self.rectangle.collidepoint(curser_position):
            #scale up button at hover
            self.image = pygame.transform.scale(self.unscaled_image, (int(self.rectangle.width * 1.1), int(self.rectangle.height * 1.1)))
            #if clicked return to default scale
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                click = True
                self.image = pygame.transform.scale(self.image, (int(self.rectangle.width), int(self.rectangle.height)))
            elif pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        else:
            #reset when not hover
            self.image = pygame.transform.scale(self.unscaled_image, (int(self.rectangle.width), int(self.rectangle.height)))

        return click