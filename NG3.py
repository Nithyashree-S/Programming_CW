import pygame
import random
from pygame.locals import *
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
black = (0, 0, 0)
blue = (100, 100, 255)
green = (53, 101, 77)
red = (186, 0, 0)

# Texts
Welcome_text = "Welcome to Notty - click start"
Begin_game_Text = "Begin Game"
Winning_Text = "You Win!"

# Card and Game Logic
class Card:
    def __init__(self, colour, number):
        self.colour = colour
        self.number = number

    def __str__(self):
        return f"{self.colour} {self.number}"

class Game:
    def __init__(self):
        self.deck = self.create_deck()
        self.player1_hand = []
        self.player2_hand = []
        self.table = []
        self.cards_drawn = 0  # Track the number of cards drawn in a round
        self.deal_done = False  # Ensure deal happens only once

    def create_deck(self):
        colors = ['red', 'blue', 'green', 'yellow']
        return [Card(color, number) for color in colors for number in range(1, 11) for _ in range(2)]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_cards(self):
        if not self.deal_done:  # Ensure cards are dealt only once
            self.player1_hand = [self.deck.pop() for _ in range(5)]
            self.player2_hand = [self.deck.pop() for _ in range(5)]
            self.deal_done = True

    def draw_card(self):
        if self.cards_drawn < 3 and len(self.deck) > 0:  # Allow only up to 3 cards to be drawn
            card = self.deck.pop()
            self.table.append(card)
            self.cards_drawn += 1
            return card
        elif self.cards_drawn >= 3:
            return "Max cards drawn"
        else:
            return "Deck is empty"

    def add_to_hand(self, player_hand):
        player_hand.extend(self.table)
        self.table.clear()
        self.cards_drawn = 0  # Reset the count for the next round

# GUI Classes
class Screen:
    def __init__(self, colour):
        self.colour = colour
        self.objects = []

    def render(self, screen):
        screen.fill(self.colour)
        for obj in self.objects:
            obj.render(screen)

    def update(self):
        for obj in self.objects:
            if hasattr(obj, 'update'):  # Only call update if the object has the method
                obj.update()

class Button:
    def __init__(self, x, y, image, scale):
        self.image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def render(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def is_clicked(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                return True
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        return False

class Text:
    def __init__(self, text, position, colour, size=30):
        self.text = text
        self.position = position
        self.colour = colour
        self.size = size
        self.font = pygame.font.SysFont(None, self.size)

    def render(self, screen):
        image = self.font.render(self.text, True, self.colour)
        screen.blit(image, self.position)

# Game Screens
class StartScreen(Screen):
    def __init__(self):
        super().__init__(blue)
        self.objects.append(Text(Welcome_text, (250, 50), black))
        start_image = pygame.image.load('Start_button.jpeg').convert_alpha()
        self.start_button = Button(250, 200, start_image, 0.2)
        self.objects.append(self.start_button)

    def update(self):
        if self.start_button.is_clicked():
            return "game_screen"

class GameScreen(Screen):
    def __init__(self, game):
        super().__init__(green)
        self.game = game
        self.objects.append(Text(Begin_game_Text, (350, 50), black))

        # Load button images
        shuffle_image = pygame.image.load('shuffle_icon.jpeg').convert_alpha()
        deal_image = pygame.image.load('deal_hand.jpeg').convert_alpha()
        draw_image = pygame.image.load('card_draw.jpeg').convert_alpha()
        add_to_hand_image = pygame.image.load('add_to_hand_icon.jpg').convert_alpha()  # New button image

        # Create buttons
        self.shuffle_button = Button(50, 400, shuffle_image, 0.6)
        self.deal_button = Button(200, 400, deal_image, 0.5)
        self.draw_button = Button(350, 400, draw_image, 0.35)
        self.add_to_hand_button = Button(500, 400, add_to_hand_image, 0.5)  # New button

        # Add buttons to objects list
        self.objects.extend([self.shuffle_button, self.deal_button, self.draw_button, self.add_to_hand_button])

    def update(self):
        # Shuffle Deck
        if self.shuffle_button.is_clicked():
            self.game.shuffle_deck()
            print("Deck shuffled!")

        # Deal Cards
        if self.deal_button.is_clicked():
            self.game.deal_cards()
            print("Cards dealt!")
            print(f"Player 1 hand: {[str(card) for card in self.game.player1_hand]}")
            print(f"Player 2 hand: {[str(card) for card in self.game.player2_hand]}")

        # Draw Card
        if self.draw_button.is_clicked():
            result = self.game.draw_card()
            if isinstance(result, Card):
                print(f"Card drawn to table: {result}")
            else:
                print(result)  # Print messages like "Max cards drawn" or "Deck is empty"

        # Add Cards from Table to Hand
        if self.add_to_hand_button.is_clicked():
            if self.game.table:
                self.game.add_to_hand(self.game.player1_hand)
                print(f"Cards added to Player 1 hand: {[str(card) for card in self.game.player1_hand]}")
            else:
                print("No cards on the table to add!")

class WinningScreen(Screen):
    def __init__(self):
        super().__init__(red)
        self.objects.append(Text(Winning_Text, (250, 50), black))
        exit_image = pygame.image.load('Exit_button.jpeg').convert_alpha()
        self.exit_button = Button(600, 450, exit_image, 0.6)
        self.objects.append(self.exit_button)

    def update(self):
        if self.exit_button.is_clicked():
            return "exit"

# Main Loop
def notty_loop():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Notty Game")
    clock = pygame.time.Clock()

    game = Game()
    game.shuffle_deck()

    start_screen = StartScreen()
    game_screen = GameScreen(game)
    winning_screen = WinningScreen()

    current_screen = start_screen

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Update and check for screen transitions
        if isinstance(current_screen, StartScreen):
            result = current_screen.update()
            if result == "game_screen":
                current_screen = game_screen
        elif isinstance(current_screen, GameScreen):
            game_screen.update()
        elif isinstance(current_screen, WinningScreen):
            result = current_screen.update()
            if result == "exit":
                running = False

        current_screen.render(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    notty_loop()
