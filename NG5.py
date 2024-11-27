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
        self.cards_drawn = 0
        self.deal_done = False

    def create_deck(self):
        colors = ['red', 'blue', 'green', 'yellow']
        return [Card(color, number) for color in colors for number in range(1, 11) for _ in range(2)]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_cards(self):
        if not self.deal_done:
            self.player1_hand = [self.deck.pop() for _ in range(5)]
            self.player2_hand = [self.deck.pop() for _ in range(5)]
            self.deal_done = True

    def draw_card(self):
        if self.cards_drawn < 3 and len(self.deck) > 0:
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
        self.cards_drawn = 0

    def is_valid_group(self, cards):
        """
        Check if a group of cards is valid.
        - A valid set: All cards have the same number but different colors.
        - A valid run: Cards have consecutive numbers and the same color.
        """
        if not cards or len(cards) < 3:
            return False

        # Check for set: all cards have the same number but different colors
        if all(card.number == cards[0].number for card in cards) and len(set(card.colour for card in cards)) == len(cards):
            return True

        # Check for run: consecutive numbers with the same color
        sorted_cards = sorted(cards, key=lambda card: card.number)
        if all(sorted_cards[i].number + 1 == sorted_cards[i + 1].number for i in range(len(sorted_cards) - 1)) and \
           all(card.colour == sorted_cards[0].colour for card in sorted_cards):
            return True

        return False

    def check_winner(self, player_hand):
        """
        Check if a player has formed valid groups and discarded all cards.
        """
        return len(player_hand) == 0

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
        self.player_turn = 1  # 1 for Player 1, 2 for Player 2
        self.objects.append(Text(Begin_game_Text, (350, 50), black))

        # Load button images
        shuffle_image = pygame.image.load('shuffle_icon.jpeg').convert_alpha()
        deal_image = pygame.image.load('deal_hand.jpeg').convert_alpha()
        draw_image = pygame.image.load('card_draw.jpeg').convert_alpha()
        add_to_hand_image = pygame.image.load('add_to_hand_icon.jpg').convert_alpha()

        # Create buttons
        self.shuffle_button = Button(50, 400, shuffle_image, 0.6)
        self.deal_button = Button(200, 400, deal_image, 0.5)
        self.draw_button = Button(350, 400, draw_image, 0.35)
        self.add_to_hand_button = Button(500, 400, add_to_hand_image, 0.5)

        self.objects.extend([self.shuffle_button, self.deal_button, self.draw_button, self.add_to_hand_button])

    def update(self):
        if self.shuffle_button.is_clicked():
            self.game.shuffle_deck()
            print("Deck shuffled!")

        if self.deal_button.is_clicked():
            self.game.deal_cards()
            print(f"Player 1 hand: {self.game.player1_hand}")
            print(f"Player 2 hand: {self.game.player2_hand}")

        if self.draw_button.is_clicked() and self.player_turn == 1:
            result = self.game.draw_card()
            if isinstance(result, Card):
                print(f"Player 1 drew: {result}")

        if self.add_to_hand_button.is_clicked() and self.player_turn == 1:
            if self.game.table:
                self.game.add_to_hand(self.game.player1_hand)
                print(f"Player 1 hand: {[str(card) for card in self.game.player1_hand]}")
                if self.game.check_winner(self.game.player1_hand):
                    return "winner_screen"
                self.ai_turn()

    def ai_turn(self):
        num_cards_to_draw = random.choice([1, 2, 3])
        for _ in range(num_cards_to_draw):
            if len(self.game.deck) > 0:
                self.game.player2_hand.append(self.game.deck.pop())
        print(f"Player 2 hand: {self.game.player2_hand}")
        if self.game.check_winner(self.game.player2_hand):
            return "winner_screen"
        self.player_turn = 1

class WinningScreen(Screen):
    def __init__(self, winner):
        super().__init__(red)
        self.objects.append(Text(f"{winner} Wins!", (250, 50), black))

# Main Loop
def notty_loop():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game = Game()
    game.shuffle_deck()
    start_screen = StartScreen()
    game_screen = GameScreen(game)
    current_screen = start_screen
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
        if isinstance(current_screen, StartScreen):
            if current_screen.update() == "game_screen":
                current_screen = game_screen
        elif isinstance(current_screen, GameScreen):
            result = current_screen.update()
            if result == "winner_screen":
                break
        current_screen.render(screen)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    notty_loop()
