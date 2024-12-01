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

class Card:
    def __init__(self, colour, number):
        assert isinstance(number, int)
        self.colour = colour
        self.number = number

    def __str__(self):
        return f'{self.colour}_{self.number}'

# Initialize player hands and game state
player_hands = {1: [], 2: []}  # Example for 2 players
current_player = 1
draw_count = {1: 0, 2: 0}
max_draw_per_turn = 3
drawn_cards = []
max_cards_in_hand = 20  # Maximum number of cards a player can have

# Add these two new lines:
ai_turn_delay = 2000  # Delay in milliseconds (1 second)
ai_turn_timer = 0

message = ""
message_timer = 0
MESSAGE_DISPLAY_TIME = 2000  # 2 seconds in milliseconds

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
dealing = True
dealing_index = 0
deal_frame_delay = 10
frame_count = 0

# Variables for drawn card display
drawn_card = None
drawn_card_timer = 0
card_display_time = 60

# Deck position and size
deck_width, deck_height = 100, 140
max_drawn_cards = 3  # Maximum number of cards that can be drawn
overlap_spacing = 30  # Space between drawn cards
total_width = deck_width + (max_drawn_cards * overlap_spacing) + 20  # Total width of deck + drawn cards
deck_x = (screen_width - total_width) // 2  # Starting position that centers the whole unit
deck_y = (screen_height - deck_height) // 2
deck_area = pygame.Rect(deck_x, deck_y, deck_width, deck_height)

# Button constants
button_width, button_height = 120, 40
button_x = 615
button_y = 300
button_area = pygame.Rect(button_x, button_y, button_width, button_height)

# Snatch button constants
snatch_button_width, snatch_button_height = 120, 40
snatch_button_x = 615
snatch_button_y = 400
snatch_button_area = pygame.Rect(snatch_button_x, snatch_button_y, snatch_button_width, snatch_button_height)

# Load card images
card_images = {}
for filename in os.listdir(CARD_IMAGES):
    if filename.endswith(".png"):
        card_name = filename.replace(".png", "")
        image_path = os.path.join(CARD_IMAGES, filename)
        card_images[card_name] = pygame.image.load(image_path)

# Load the card back image
card_back_image = pygame.image.load(CARD_BACK_IMAGE_PATH)
card_back_image = pygame.transform.scale(card_back_image, (100, 140))

# Load shuffle sound
shuffle_sound = pygame.mixer.Sound("shuffle_sound.mp3")

def draw_button(text, x, y, width, height, color=(0, 122, 204), text_color=(255, 255, 255), border_color=(255, 255, 255), border_width=3):
    """Draw a button with a border and centered text."""
    pygame.draw.rect(screen, border_color, (x - border_width, y - border_width, width + 2 * border_width, height + 2 * border_width))
    pygame.draw.rect(screen, color, (x, y, width, height))
    font = pygame.font.Font(None, 25)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surf, text_rect)

def show_card(card_name, x, y, width=100, height=140, face_down=False):
    """Display a card, either face up or face down."""
    if face_down:
        screen.blit(card_back_image, (x, y))
    else:
        if card_name in card_images:
            card_image = card_images[card_name]
            card_image = pygame.transform.scale(card_image, (width, height))
            screen.blit(card_image, (x, y))
        else:
            print(f"Card {card_name} not found!")

def display_cards(player_id, x, y, spacing=30):
    """Display all cards in the player's hand."""
    for i, card in enumerate(player_hands[player_id]):
        show_card(card, x + i * spacing, y, face_down=False)

def draw_player_name(name, x, y, color=(255, 255, 255)):
    """Draw player name on the screen."""
    font = pygame.font.Font(None, 25)
    text_surf = font.render(name, True, color)
    screen.blit(text_surf, (x, y))

def clear_drawn_card_area():
    """Clear the area where drawn cards are displayed."""
    clear_rect_x = deck_x + deck_width + 20
    clear_rect_y = deck_y
    clear_rect_width = 3 * 110
    clear_rect_height = 140
    pygame.draw.rect(screen, (0, 128, 0), (clear_rect_x, clear_rect_y, clear_rect_width, clear_rect_height))

def draw_card():
    """Draw a card from the full_deck."""
    if full_deck:
        return full_deck.pop()
    return None

def can_add_cards(player_id, num_cards):
    """Check if a player can add more cards to their hand."""
    return len(player_hands[player_id]) + num_cards <= max_cards_in_hand

def is_hand_full(player_id):
    """Check if a player's hand is at the maximum limit."""
    return len(player_hands[player_id]) >= max_cards_in_hand

def ai_turn():
    """Automate Player 2's turn to mirror Human player's actions."""
    global current_player, drawn_cards, message
    
    # Random decision to either draw cards, snatch, or skip
    action = random.choice(['draw', 'snatch', 'skip'])
    
    if action == 'draw':
        if is_hand_full(2):
            print("Player 2 (AI) cannot draw more cards - hand is full!")
            message = "Computer's hand is full!"
        else:    
            num_draws = random.randint(1, min(3, max_cards_in_hand - len(player_hands[2])))
            for _ in range(num_draws):
                card = draw_card()
                if card:
                    player_hands[2].append(card)
            message = f"Computer drew {num_draws} card{'s' if num_draws > 1 else ''}"
            print(message)
    
    elif action == 'snatch':
        if is_hand_full(2):
            print("Cannot snatch more cards - AI hand is full!")
            message = "Computer's hand is full!"
        elif player_hands[1]:  # If Human has cards
            snatched_card = player_hands[1].pop(random.randint(0, len(player_hands[1]) - 1))
            player_hands[2].append(snatched_card)
            message = "Computer snatched a card!"
            print(message)
        else:
            print("No cards left for AI to snatch!")
            message = "No cards for Computer to snatch!"
    
    else:  # skip turn
        message = "Computer skipped its turn"
        print(message)
    
    clear_drawn_card_area()
    current_player = 1  # Always change to Human's turn after AI completes its action
    drawn_cards.clear()  # Ensure drawn_cards is cleared after AI's turn

def shuffle_deck():
    """Shuffle the deck with a visual animation."""
    global shuffle_count, shuffle_complete
    screen.fill((0, 128, 0))
    shuffle_count += 1

    offset = 5 if shuffle_count % 10 < 5 else -5
    deck_bounce_y = deck_y + offset
    screen.blit(card_back_image, (deck_x, deck_bounce_y))

    if shuffle_count == 1:
        shuffle_sound.play()

    if shuffle_count > 40:
        shuffle_complete = True
        random.shuffle(full_deck)

def snatch_card():
    """Allow Human player to snatch one card from the Computer."""
    global current_player
    
    if is_hand_full(1):  # Check if Human's hand is full
        print("Cannot snatch more cards - Human hand is full!")
        return False
        
    if player_hands[2]:  # If Computer (Player 2) has cards
        snatched_card = player_hands[2].pop(random.randint(0, len(player_hands[2]) - 1))
        player_hands[1].append(snatched_card)
        print(f"Snatched card: {snatched_card}")
        current_player = 2  # Force turn change to Computer after snatch
        return True
    else:
        print("No cards left to snatch!")
        return False
    
def draw_message():
    """Display game messages on screen."""
    if message:
        font = pygame.font.Font(None, 32)
        text_surface = font.render(message, True, (255, 255, 255))
        
        # Center vertically on screen
        screen_center_y = screen_height // 2
        
        # Create text rectangle
        text_rect = text_surface.get_rect(left=50, centery=screen_center_y)
        
        # Create border rectangle centered vertically - for all messages
        border_rect = pygame.Rect(
            50,  # x position aligned with text
            screen_center_y - 35,  # Half of border height subtracted from center
            300,  # Width of the rectangle
            70   # Height of the rectangle
        )
        
        # Draw border (white rectangle)
        pygame.draw.rect(screen, (255, 255, 255), border_rect, 2)  # 2 is border thickness
        
        # Center the text within the border rectangle
        text_rect.centerx = border_rect.centerx
        text_rect.centery = border_rect.centery
        
        # Draw text
        screen.blit(text_surface, text_rect)

# Main game loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Only process Human player actions when it's their turn
            if current_player == 1 and not dealing:
                # Deck area - Draw card
                if shuffle_complete and deck_area.collidepoint(mouse_pos):
                    if is_hand_full(1):
                        print("Cannot draw more cards - Human hand is full!")
                    else:
                        remaining_space = max_cards_in_hand - len(player_hands[1])
                        max_drawable = min(3 - len(drawn_cards), remaining_space)
                        if max_drawable > 0:
                            drawn_card = draw_card()
                            if drawn_card:
                                drawn_cards.append(drawn_card)
                                print("Player 1 drew a card")
                
                # Done Drawing button
                elif button_area.collidepoint(mouse_pos):
                    if len(drawn_cards) == 0:
                        print("Player 1 skips their turn")
                        clear_drawn_card_area()
                        current_player = 2  # Skip turn, pass to Computer
                    else:
                        if can_add_cards(current_player, len(drawn_cards)):
                            player_hands[current_player].extend(drawn_cards)
                            drawn_cards.clear()
                            clear_drawn_card_area()
                            current_player = 2  # Done drawing, pass to Computer
                        else:
                            print("Cannot add drawn cards - Hand limit exceeded!")
                            drawn_cards.clear()
                            clear_drawn_card_area()
                
                # Snatch button
                elif snatch_button_area.collidepoint(mouse_pos):
                    if len(drawn_cards) > 0:  # Can't snatch after drawing cards
                        print("Cannot snatch after drawing cards. Click Done Drawing first.")
                    else:
                        if is_hand_full(1):
                            print("Cannot snatch more cards - Human hand is full!")
                        else:
                            if snatch_card():  # If snatch was successful
                                current_player = 2  # Change to AI's turn

    # AI's turn - process immediately when it's Player 2's turn
    if current_player == 2 and not dealing and shuffle_complete:
        current_time = pygame.time.get_ticks()
        if ai_turn_timer == 0:
            # First time entering AI turn, set the timer
            ai_turn_timer = current_time
        elif current_time - ai_turn_timer >= ai_turn_delay:
            # Delay has passed, execute AI turn
            ai_turn()  # ai_turn will set current_player back to 1
            ai_turn_timer = 0  # Reset timer for next AI turn
            message_timer = current_time  # Start message timer after AI turn
    elif current_player == 1 and not dealing and shuffle_complete:
        message = "Your turn"

    if not shuffle_complete:
        shuffle_deck()
    elif dealing:
        if frame_count % deal_frame_delay == 0:
            player_id = (dealing_index % 2) + 1
            if len(player_hands[player_id]) < 5:
                card = draw_card()
                if card:
                    player_hands[player_id].append(card)
                    dealing_index += 1
            else:
                if all(len(hand) == 5 for hand in player_hands.values()):
                    dealing = False
        frame_count += 1

    # Display game state
    screen.fill((15, 20, 45))  
    
    draw_player_name("Human", 50, 170)
    draw_player_name("Computer", 50, 410)
    
    display_cards(1, 50, 10)  # Human player's hand
    display_cards(2, 50, 450)  # Computer's hand

    if full_deck:
        screen.blit(card_back_image, (deck_x, deck_y))

    draw_button("Done Drawing", button_x, button_y, button_width, button_height)
    draw_button("Snatch", snatch_button_x, snatch_button_y, snatch_button_width, snatch_button_height, color=(0, 122, 204))

    # Display drawn cards face down
    for i, _ in enumerate(drawn_cards):
        drawn_card_x = deck_x + deck_width + 20 + i * overlap_spacing
        drawn_card_y = deck_y
        show_card(None, drawn_card_x, drawn_card_y, face_down=True)

    # Add message handling
    current_time = pygame.time.get_ticks()
    if message and current_time - message_timer > MESSAGE_DISPLAY_TIME:
        if current_player == 1:
            message = "Your turn"
        else:
            message = ""
        message_timer = current_time

    # Draw the message
    draw_message()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()