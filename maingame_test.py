#example
import pygame
import os
import random
pygame.init()

CARD_IMAGES = "card_images/"
GAME_IMAGES = "game_images/"
CARD_BACK_IMAGE_PATH = os.path.join(GAME_IMAGES, "card_back.png")

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Card Game")
clock = pygame.time.Clock()


# given by Daniel
class Card:
    def __init__(self, colour, number):
        assert isinstance(number, int)
        self.colour = colour
        self.number = number

    def __str__(self):
        return f'{self.colour} {self.number}'


# Initialize player hands
player_hands = {1: [], 2: []}  # Example for 2 players
current_player = 1
draw_count = {1: 0, 2: 0}
max_draw_per_turn = 3


def create_deck():
    colours = ['red', 'blue', 'green', 'yellow']
    numbers = [str(i) for i in range(0, 10)]
    return [f"{number}_{colour}" for colour in colours for number in numbers]


# full deck of cards
full_deck = create_deck()
full_deck.extend(full_deck.copy())

# Shuffle control variables
shuffle_complete = False
shuffle_count = 0

# Dealing control variables
dealing = True  # Indicates if dealing is ongoing
dealing_index = 0  # Tracks the number of cards dealt
deal_frame_delay = 10  # Frames to wait between dealing cards
frame_count = 0

# Variables for drawn card display
drawn_card = None
drawn_card_timer = 0  # Timer to clear the displayed card
card_display_time = 60

card_images = {}
for filename in os.listdir(CARD_IMAGES):
    if filename.endswith(".png"):
        card_name = filename.replace(".png","")
        image_path = os.path.join(CARD_IMAGES,filename)
        card_images[card_name] = pygame.image.load(image_path)


# Load the card back image
card_back_image = pygame.image.load(CARD_BACK_IMAGE_PATH)
card_back_image = pygame.transform.scale(card_back_image, (100, 140))

# Load shuffle sound
shuffle_sound = pygame.mixer.Sound("shuffle_sound.mp3")


def show_card(card_name,x,y, width=100, height=140):
    if card_name in card_images:
        card_image = card_images[card_name]
        card_image = pygame.transform.scale(card_image, (width, height))  # Resize the card
        screen.blit(card_image, (x, y))
    else:
        print(f"Card {card_name} not found!")


# display cards
def display_cards(player_id, x, y, spacing=30):
    # Display all cards in the player's hand
    for i, card in enumerate(player_hands[player_id]):
        show_card(card, x + i * spacing, y)


def draw_card():
    """Draw a card from the full_deck."""
    if full_deck:
        return full_deck.pop()
    return None


# Deck position and size (for clicking)
deck_width, deck_height = 100, 140  # Width and height of the card back
deck_x = (screen_width - deck_width) // 2  # Center the deck horizontally
deck_y = (screen_height - deck_height) // 2  # Center the deck vertically
deck_area = pygame.Rect(deck_x, deck_y, deck_width, deck_height)


# Shuffle the deck with animation
def shuffle_deck():
    """Shuffle the deck with a visual animation."""
    global shuffle_count, shuffle_complete
    screen.fill((0, 128, 0))  # Green background
    shuffle_count += 1

    # Display the deck bouncing slightly
    offset = 5 if shuffle_count % 10 < 5 else -5  # Bounce effect
    deck_bounce_y = deck_y + offset
    screen.blit(card_back_image, (deck_x, deck_bounce_y))

    # Play the shuffle sound
    if shuffle_count == 1:
        shuffle_sound.play()

    if shuffle_count > 40:  # After 60 frames (or enough time for shuffle animation)
        shuffle_complete = True
        random.shuffle(full_deck)


# Main game loop
running = True
drawn_card = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            mouse_pos = pygame.mouse.get_pos()
            if not dealing and shuffle_complete and deck_area.collidepoint(mouse_pos):  # Check if the full_deck was clicked
                drawn_card = draw_card()
                if drawn_card:
                    player_hands[current_player].append(drawn_card)  # Add to player's hand
                    print(f"Player {current_player} drew: {drawn_card}")
                    current_player = 2 if current_player == 1 else 1

    if not shuffle_complete:
        shuffle_deck()

    # If shuffle is complete, deal cards
    elif dealing:
        if frame_count % deal_frame_delay == 0:  # Delay between card deals
            player_id = (dealing_index % 2) + 1  # Alternate between players 1 and 2
            if len(player_hands[player_id]) < 5:  # Deal only if the player has fewer than 5 cards
                card = draw_card()
                if card:
                    player_hands[player_id].append(card)
                    dealing_index += 1
            else:
                if all(len(hand) == 5 for hand in player_hands.values()):
                    dealing = False  # Stop dealing once all players have 5 cards
        frame_count += 1

    # Display player hands
    display_cards(1, 50, 10)  # Player 1's hand at the top
    display_cards(2, 50, 450)  # Player 2's hand at the bottom

    # Display the deck (back of a card)
    if full_deck:
        screen.blit(card_back_image, (deck_x, deck_y))

    # Show last drawn card
    if drawn_card:
        drawn_card_x = deck_x + deck_width + 20  # Position 20 pixels to the right of the deck
        drawn_card_y = deck_y  # Same vertical position as the deck
        show_card(drawn_card, drawn_card_x, drawn_card_y, width=80, height=112)

    # Update the display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
