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
pygame.display.set_caption("Notty Game")
clock = pygame.time.Clock()

# given by Daniel
class Card:
    def __init__(self, colour, number):
        assert isinstance(number, int)
        self.colour = colour
        self.number = number

    def __str__(self):
        return f'{self.colour}_{self.number}'  # Changed to match `colour_number` format

# Initialize player hands
player_hands = {1: [], 2: []}  # Example for 2 players
current_player = 1
draw_count = {1: 0, 2: 0}
max_draw_per_turn = 3
drawn_cards = []

def create_deck():
    """Create a deck of cards in the `colour_number` format."""
    colours = ['red', 'blue', 'green', 'yellow']
    numbers = [str(i) for i in range(0, 10)]
    return [f"{colour}_{number}" for colour in colours for number in numbers]

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

# Deck position and size (for clicking)
deck_width, deck_height = 100, 140  # Width and height of the card back
deck_x = (screen_width - deck_width) // 2  # Center the deck horizontally
deck_y = (screen_height - deck_height) // 2  # Center the deck vertically
deck_area = pygame.Rect(deck_x, deck_y, deck_width, deck_height)

# Additional constants for the "Done Drawing" button
button_width, button_height = 120, 50
button_x = deck_x - button_width - 20  # Position to the left of the deck
button_y = deck_y + (deck_height - button_height) // 2
button_area = pygame.Rect(button_x, button_y, button_width, button_height)

# Load card images
card_images = {}
for filename in os.listdir(CARD_IMAGES):
    if filename.endswith(".png"):
        card_name = filename.replace(".png", "")  # Use the exact `colour_number` format
        image_path = os.path.join(CARD_IMAGES, filename)
        card_images[card_name] = pygame.image.load(image_path)

# Load the card back image
card_back_image = pygame.image.load(CARD_BACK_IMAGE_PATH)
card_back_image = pygame.transform.scale(card_back_image, (100, 140))

# Load shuffle sound
shuffle_sound = pygame.mixer.Sound("shuffle_sound.mp3")

def draw_button(text, x, y, width, height, color=(0, 0, 255), text_color=(255, 255, 255)):
    """Draw a button with centered text."""
    pygame.draw.rect(screen, color, (x, y, width, height))  # Draw the button rectangle
    font = pygame.font.Font(None, 25)  # Set the font size
    text_surf = font.render(text, True, text_color)  # Render the text surface
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))  # Center the text
    screen.blit(text_surf, text_rect)

def show_card(card_name, x, y, width=100, height=140):
    """Display a card based on its `colour_number` name."""
    if card_name in card_images:
        card_image = card_images[card_name]
        card_image = pygame.transform.scale(card_image, (width, height))  # Resize the card
        screen.blit(card_image, (x, y))
    else:
        print(f"Card {card_name} not found!")

# display cards
def display_cards(player_id, x, y, spacing=30):
    """Display all cards in the player's hand."""
    for i, card in enumerate(player_hands[player_id]):
        show_card(card, x + i * spacing, y)

def clear_drawn_card_area():
    """Clear the area where drawn cards are displayed."""
    clear_rect_x = deck_x + deck_width + 20  # Starting position of the drawn card display
    clear_rect_y = deck_y
    clear_rect_width = 3 * 110  # Maximum width for three cards displayed side-by-side
    clear_rect_height = 140  # Height of a card
    pygame.draw.rect(screen, (0, 128, 0), (clear_rect_x, clear_rect_y, clear_rect_width, clear_rect_height))  # Green background

def draw_card():
    """Draw a card from the full_deck."""
    if full_deck:
        return full_deck.pop()
    return None

def ai_turn():
    """Automate Player 2's turn."""
    global current_player
    num_draws = random.randint(1, 3)  # Randomly decide how many cards to draw
    print(f"Player 2 (AI) is drawing {num_draws} card(s).")

    for _ in range(num_draws):
        card = draw_card()
        if card:
            player_hands[2].append(card)  # Add drawn cards to Player 2's hand

    print(f"Player 2 (AI) hand: {player_hands[2]}")
    clear_drawn_card_area()  # Clear the drawn card visuals
    current_player = 1  # Switch back to Player 1

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
def detect_valid_groups(hand):
    """Detect valid groups in a player's hand.
    
    A valid group can be:
    - Same numbers but different colors.
    - Consecutive numbers of the same color.
    """
    groups = []  # Store valid groups
    remaining_cards = hand.copy()  # Copy the hand to modify it safely

    # Check for groups with same numbers but different colors
    numbers = {}
    for card in hand:
        color, number = card.split("_")
        if number not in numbers:
            numbers[number] = []
        numbers[number].append(card)

    for number, cards in numbers.items():
        if len(cards) >= 3:  # At least 3 cards with the same number but different colors
            groups.append(cards)
            for card in cards:
                if card in remaining_cards:
                    remaining_cards.remove(card)

    # Check for groups with consecutive numbers of the same color
    colors = {}
    for card in hand:
        color, number = card.split("_")
        if color not in colors:
            colors[color] = []
        colors[color].append(int(number))

    for color, numbers in colors.items():
        numbers.sort()
        temp_group = []
        for i in range(len(numbers)):
            if i > 0 and numbers[i] == numbers[i - 1] + 1:  # Check for consecutive numbers
                temp_group.append(f"{color}_{numbers[i]}")
                if len(temp_group) >= 3:  # At least 3 consecutive cards
                    groups.append(temp_group.copy())
            else:
                if len(temp_group) >= 3:
                    groups.append(temp_group.copy())
                temp_group = [f"{color}_{numbers[i]}"]
        if len(temp_group) >= 3:
            groups.append(temp_group)

        # Remove the grouped cards from the remaining cards
        for group in groups:
            for card in group:
                if card in remaining_cards:
                    remaining_cards.remove(card)

    return groups, remaining_cards


def check_for_win(player_id):
    """Check if a player has won by having no cards left."""
    if not player_hands[player_id]:
        print(f"Player {player_id} wins!")
        return True
    return False


def discard_groups(player_id):
    """Check for valid groups in a player's hand and discard them."""
    groups, remaining_cards = detect_valid_groups(player_hands[player_id])
    if groups:
        print(f"Player {player_id} formed valid groups: {groups}")
        player_hands[player_id] = remaining_cards
    else:
        print(f"Player {player_id} could not form any groups.")
    return check_for_win(player_id)

# Main game loop
running = True  # Initialize the `running` variable to control the game loop

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            mouse_pos = pygame.mouse.get_pos()
            if not dealing and shuffle_complete and deck_area.collidepoint(mouse_pos) and current_player == 1:
                if len(drawn_cards) < 3:  # Allow drawing up to 3 cards
                    drawn_card = draw_card()
                    if drawn_card:
                        drawn_cards.append(drawn_card)  # Add to the temporary drawn cards list
                        print(f"Player {current_player} drew: {drawn_card}")
            elif not dealing and button_area.collidepoint(mouse_pos) and current_player == 1:
                player_hands[current_player].extend(drawn_cards)  # Add drawn cards to the player's hand
                drawn_cards.clear()  # Clear the temporary drawn cards list
                clear_drawn_card_area()  # Clear the drawn card visuals

                # Check for valid groups and discard them
                if discard_groups(current_player):  # If Player 1 wins, end the game
                    running = False
                else:
                    current_player = 2  # Switch to Player 2's turn

    if current_player == 2 and not dealing:  # Automatically trigger Player 2's turn
        ai_turn()
        # Check for valid groups and discard them for AI
        if discard_groups(current_player):  # If Player 2 wins, end the game
            running = False

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

    # Display the "Done Drawing" button
    draw_button("Done Drawing", button_x, button_y, button_width, button_height)

    # Display drawn cards
    for i, card in enumerate(drawn_cards):
        drawn_card_x = deck_x + deck_width + 20 + i * 110  # Offset drawn cards
        drawn_card_y = deck_y
        show_card(card, drawn_card_x, drawn_card_y, width=100, height=140)

    # Update the display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
