import pygame
import os
import random
from Main_code_2_player import check_winning_state
pygame.init()

# Constants and Configuration
CARD_IMAGES = "card_images/"
GAME_IMAGES = "game_images/"
CARD_BACK_IMAGE_PATH = os.path.join(GAME_IMAGES, "card_back.png")

# Screen setup
screen_width, screen_height = 1024, 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Notty Game")
clock = pygame.time.Clock()

# Player configuration
PLAYER_POSITIONS = {
    1: ((screen_width - 100) // 2, 100), 
    2: (screen_width - 150, 350),         
    3: (50, 350)                          
}

PLAYER_NAMES = {
    1: "Human",
    2: "Computer 1",
    3: "Computer 2"
}

class Card:
    def __init__(self, colour, number):
        assert isinstance(number, int)
        self.colour = colour
        self.number = number

    def __str__(self):
        return f'{self.colour}_{self.number}'

class CollectionOfCards:
    def __init__(self, notty_cards_list):
        self.collection = []
        for card_info in notty_cards_list:
            colour, number = card_info.split('_')
            card = Card(colour, int(number))
            self.collection.append(card)

    def is_valid_group(self):
        if len(self.collection) < 3:
            return False

        color_groups = {}
        number_groups = {}

        for card in self.collection:
            if card.colour not in color_groups:
                color_groups[card.colour] = []
            color_groups[card.colour].append(card.number)

            if card.number not in number_groups:
                number_groups[card.number] = []
            number_groups[card.number].append(card.colour)

        if len(color_groups) == 1:
            for group_color, group_numbers in color_groups.items():
                if len(group_numbers) >= 3:
                    sorted_group_numbers = sorted(group_numbers)
                    if all(
                        sorted_group_numbers[i] + 1 == sorted_group_numbers[i + 1]
                        for i in range(len(sorted_group_numbers) - 1)
                    ):
                        return True
                break

        if len(number_groups) == 1:
            for group_number, group_colors in number_groups.items():
                if len(group_colors) >= 3 and len(set(group_colors)) == len(group_colors):
                    return True
                break

        return False

    def find_valid_group(self):
        print("Searching for valid group...")  # Debug
        number_groups = {}
        for card in self.collection:
            if card.number not in number_groups:
                number_groups[card.number] = []
            number_groups[card.number].append(card)

        # Check for same-number groups
        for same_number_cards in number_groups.values():
            unique_colors = set(card.colour for card in same_number_cards)
            if len(unique_colors) >= 3:
                result = [card for card in same_number_cards if card.colour in unique_colors][:3]
                print(f"Found valid same-number group: {[str(card) for card in result]}")  # Debug
                return result

        # Check for color runs
        color_groups = {}
        for card in self.collection:
            if card.colour not in color_groups:
                color_groups[card.colour] = []
            color_groups[card.colour].append(card.number)

        for group_color, group_numbers in color_groups.items():
            sorted_group_numbers = sorted(group_numbers)
            current_sequence = [sorted_group_numbers[0]]
            
            for i in range(1, len(sorted_group_numbers)):
                if sorted_group_numbers[i] == current_sequence[-1] + 1:
                    current_sequence.append(sorted_group_numbers[i])
                else:
                    if len(current_sequence) >= 3:
                        result = [Card(group_color, num) for num in current_sequence]
                        print(f"Found valid color run: {[str(card) for card in result]}")  # Debug
                        return result
                    current_sequence = [sorted_group_numbers[i]]
                    
            if len(current_sequence) >= 3:
                result = [Card(group_color, num) for num in current_sequence]
                print(f"Found valid color run: {[str(card) for card in result]}")  # Debug
                return result

        print("No valid group found")  # Debug
        return None

    def find_largest_valid_group(self):
        print("Searching for largest valid group...")  # Debug
        largest_valid_group = None
        
        # Check for color runs
        color_groups = {}
        for card in self.collection:
            if card.colour not in color_groups:
                color_groups[card.colour] = []
            color_groups[card.colour].append(card.number)

        for group_color, group_numbers in color_groups.items():
            sorted_group_numbers = sorted(group_numbers)
            current_sequence = [sorted_group_numbers[0]]
            
            for i in range(1, len(sorted_group_numbers)):
                if sorted_group_numbers[i] == current_sequence[-1] + 1:
                    current_sequence.append(sorted_group_numbers[i])
                else:
                    if len(current_sequence) >= 3 and (largest_valid_group is None or 
                                                     len(current_sequence) > len(largest_valid_group)):
                        largest_valid_group = [Card(group_color, num) for num in current_sequence]
                    current_sequence = [sorted_group_numbers[i]]
            
            if len(current_sequence) >= 3 and (largest_valid_group is None or 
                                             len(current_sequence) > len(largest_valid_group)):
                largest_valid_group = [Card(group_color, num) for num in current_sequence]

        # Check for same-number groups
        number_groups = {}
        for card in self.collection:
            if card.number not in number_groups:
                number_groups[card.number] = []
            number_groups[card.number].append(card.colour)

        for number, colors in number_groups.items():
            unique_colors = list(set(colors))
            if len(unique_colors) >= 3:
                color_group = [Card(color, number) for color in unique_colors]
                if largest_valid_group is None or len(color_group) > len(largest_valid_group):
                    largest_valid_group = color_group

        if largest_valid_group:
            print(f"Found largest valid group: {[str(card) for card in largest_valid_group]}")  # Debug
        else:
            print("No valid group found")  # Debug
        return largest_valid_group

class GameState2:
    def __init__(self):
        # Game state variables
        self.player_hands = {1: [], 2: [], 3: []}
        self.current_player = 1
        self.draw_count = {1: 0, 2: 0, 3: 0}
        self.max_draw_per_turn = 3
        self.drawn_cards = []
        self.max_cards_in_hand = 20
        self.valid_groups = {1: None, 2: None, 3: None}
        self.largest_groups = {1: None, 2: None, 3: None}
        self.ai_turn_delay = 2000
        self.ai_turn_timer = 0
        self.message = ""
        self.message_timer = 0
        self.MESSAGE_DISPLAY_TIME = 5000
        self.waiting_for_discard_decision = False
        self.full_deck = self.create_deck()
        self.shuffle_complete = False
        self.shuffle_count = 0
        self.dealing = True
        self.dealing_index = 0
        self.deal_frame_delay = 10
        self.frame_count = 0
        self.user_name = "Player 1"  # Name of the human player

    def create_deck(self):
        colours = ['red', 'blue', 'green', 'yellow']
        numbers = [str(i) for i in range(0, 10)]
        deck = [f"{colour}_{number}" for colour in colours for number in numbers]
        return deck + deck.copy()

game_state2 = GameState2()

# Game state variables
deck_width, deck_height = 90, 130
max_drawn_cards = 3
overlap_spacing = 30

vertical_offset = 50
deck_y = (screen_height - deck_height) // 2 - vertical_offset

space_between_deck_and_cards = 20
drawn_cards_width = game_state2.max_draw_per_turn * overlap_spacing
total_width = deck_width + space_between_deck_and_cards + ((max_drawn_cards - 1) * overlap_spacing)

# Button configurations
button_width, button_height = 100, 40
screen_midpoint = screen_width // 2

# Position Done button to end 10px left of midpoint
button_x = screen_midpoint - button_width - 10
button_y = deck_y + deck_height + 25
button_area = pygame.Rect(button_x, button_y, button_width, button_height)

# Position Return button to start 10px right of midpoint
return_button_x = screen_midpoint + 10
return_button_area = pygame.Rect(return_button_x, button_y, button_width, button_height)

# Align deck and drawn cards with buttons
deck_x = button_x  # Deck starts where Done button starts
deck_area = pygame.Rect(deck_x, deck_y, deck_width, deck_height)

# Drawn cards start where Return button starts
drawn_card_start_x = return_button_x
drawn_cards_area = pygame.Rect(drawn_card_start_x, deck_y, drawn_cards_width, deck_height)

snatch1_button_width, snatch1_button_height = 100, 40
snatch1_button_x = screen_width - 285
snatch1_button_y = deck_y + deck_height + 25 
snatch1_button_area = pygame.Rect(snatch1_button_x, snatch1_button_y, snatch1_button_width, snatch1_button_height)

snatch2_button_width, snatch2_button_height = 100,40
snatch2_button_x = 185
snatch2_button_y = deck_y + deck_height + 25
snatch2_button_area = pygame.Rect(snatch2_button_x, snatch2_button_y, snatch2_button_width, snatch2_button_height)

waiting_for_discard_decision = False
yes_button_area = pygame.Rect((screen_width // 2), deck_y + deck_height + 250, 50, 40)  # Moved more to the left
no_button_area = pygame.Rect((screen_width // 2), deck_y + deck_height + 250, 50, 40)   # Moved more to the right

# Load assets
card_images = {}
for filename in os.listdir(CARD_IMAGES):
    if filename.endswith(".png"):
        card_name = filename.replace(".png", "")
        image_path = os.path.join(CARD_IMAGES, filename)
        card_images[card_name] = pygame.image.load(image_path)

card_back_image = pygame.image.load(CARD_BACK_IMAGE_PATH)
card_back_image = pygame.transform.scale(card_back_image, (100, 140))
shuffle_sound = pygame.mixer.Sound("shuffle_sound.mp3")


def draw_button(text, x, y, width, height, color=(0, 122, 204), text_color=(0, 0, 0)):
    pygame.draw.rect(screen, color, (x, y, width, height))
    font = pygame.font.Font(None, 28)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surf, text_rect)

def draw_discard_buttons():
    if waiting_for_discard_decision:
        draw_button("Yes", yes_button_area.x, yes_button_area.y, 
                    yes_button_area.width, yes_button_area.height,
                    color=(242, 240, 239))
        draw_button("No", no_button_area.x, no_button_area.y, 
                    no_button_area.width, no_button_area.height,
                    color=(242, 240, 239))
        
def show_card(card_name, x, y, width=100, height=140, face_down=False):
    if face_down:
        screen.blit(card_back_image, (x, y))
    else:
        if card_name in card_images:
            card_image = card_images[card_name]
            card_image = pygame.transform.scale(card_image, (width, height))
            screen.blit(card_image, (x, y))
        else:
            print(f"Card {card_name} not found!")

def display_cards(player_id, spacing=30):
    # Human player settings
    base_y = 50 if player_id == 1 else (screen_height // 2)  # Center point for computer players

    valid_card_strs = []
    largest_card_strs = []

    if game_state2.valid_groups[player_id] is not None:
        valid_card_strs = [str(card) for card in game_state2.valid_groups[player_id]]
    if game_state2.largest_groups[player_id] is not None and len(game_state2.largest_groups[player_id]) > 3:
        largest_card_strs = [str(card) for card in game_state2.largest_groups[player_id]]

    regular_cards = [card for card in game_state2.player_hands[player_id]
                    if card not in valid_card_strs and card not in largest_card_strs]

    # Human player - horizontal layout
    if player_id == 1:
        # Calculate the total width needed for all cards
        card_width = 100  # Width of a single card
        num_regular_cards = len(regular_cards)
        num_valid_cards = len(valid_card_strs)
        num_largest_cards = len(largest_card_strs) if largest_card_strs != valid_card_strs else 0

        # Calculate total width including spacing between card groups
        total_width = (num_regular_cards * spacing)  # Regular cards
        if num_valid_cards > 0:
            total_width += 20 + (num_valid_cards * spacing)  # Valid group spacing + cards
        if num_largest_cards > 0:
            total_width += 60 + (num_largest_cards * spacing)  # Largest group spacing + cards

        # Calculate starting X position to center all cards
        current_x = (screen_width - total_width) // 2
        current_y = base_y

        # Draw regular cards
        for card in regular_cards:
            show_card(card, current_x, current_y)
            current_x += spacing

        # Draw valid groups with spacing
        if game_state2.valid_groups[player_id] is not None:
            current_x += 20  # Add spacing between regular cards and valid group
            for card_str in valid_card_strs:
                show_card(card_str, current_x, current_y)
                current_x += spacing

        # Draw largest groups with spacing
        if (game_state2.largest_groups[player_id] is not None and len(game_state2.largest_groups[player_id]) > 3 and
                largest_card_strs != valid_card_strs):
            current_x += 60  # Add spacing between valid group and largest group
            for card_str in largest_card_strs:
                show_card(card_str, current_x, current_y)
                current_x += spacing

    # Computer players - vertical layout
    else:
        vertical_spacing = 35
        card_height = 140  # Height of a single card

        # Calculate total height needed for all cards and groups
        total_height = (len(regular_cards) * vertical_spacing)
        if game_state2.valid_groups[player_id] is not None:
            total_height += 20 + (len(valid_card_strs) * vertical_spacing)
        if game_state2.largest_groups[player_id] is not None and len(game_state2.largest_groups[player_id]) > 3:
            if largest_card_strs != valid_card_strs:
                total_height += 40 + (len(largest_card_strs) * vertical_spacing)

        # Calculate starting Y position to center all cards vertically
        current_y = (screen_height - total_height) // 2

        # Set X position based on player (left or right side)
        current_x = screen_width - 150 if player_id == 2 else 50

        # Draw regular cards
        for card in regular_cards:
            show_card(card, current_x, current_y)
            current_y += vertical_spacing

        # Draw valid groups with spacing
        if game_state2.valid_groups[player_id] is not None:
            current_y += 20  # Add spacing between regular cards and valid group
            for card_str in valid_card_strs:
                show_card(card_str, current_x, current_y)
                current_y += vertical_spacing

        # Draw largest groups with spacing
        if game_state2.largest_groups[player_id] is not None and len(game_state2.largest_groups[player_id]) > 3:
            if largest_card_strs != valid_card_strs:
                current_y += 40  # Add spacing between valid group and largest group
                for card_str in largest_card_strs:
                    show_card(card_str, current_x, current_y)
                    current_y += vertical_spacing

def draw_player_name(name, x, y, color=(255, 255, 255)):
    font = pygame.font.Font(None, 30)
    text_surf = font.render(name, True, color)
    screen.blit(text_surf, (x, y))

def draw_player_names():
    draw_player_name("You", screen_width//2, 200)  
    draw_player_name("Computer 1", screen_width - 295, 390)
    draw_player_name("Computer 2", 185, 390)

def clear_drawn_card_area():
    clear_rect_x = drawn_card_start_x
    clear_rect_y = deck_y
    clear_rect_width = max_drawn_cards * (deck_width + overlap_spacing)
    clear_rect_height = deck_height
    pygame.draw.rect(screen, (0, 128, 0), (clear_rect_x, clear_rect_y, clear_rect_width, clear_rect_height))

def draw_message():
    if game_state2.message:
        # Message box width and height
        message_box_width = 650
        message_box_height = 225
        
        # Position the box at bottom with padding (original position)
        message_box_x = (screen_width - message_box_width) // 2
        message_box_y = screen_height - message_box_height - 30  # 30px padding from bottom
        
        # Increased font size
        font_size = 30
        font = pygame.font.Font(None, font_size)
        
        # Word wrapping logic
        words = game_state2.message.split()
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            test_surface = font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= (message_box_width - 60):
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        text_surfaces = [font.render(line.upper(), True, (255, 255, 255)) for line in lines]
        
        # Semi-transparent black background
        background_surface = pygame.Surface((message_box_width, message_box_height))
        background_surface.set_alpha(180)
        background_surface.fill((0, 0, 0))
        screen.blit(background_surface, (message_box_x, message_box_y))
        
        # Calculate text positioning
        total_text_height = sum(surface.get_height() for surface in text_surfaces)
        line_spacing = 10
        total_height = total_text_height + (line_spacing * (len(lines) - 1)) if len(lines) > 1 else total_text_height
        
        # Move text up 75px from center of box
        current_y = message_box_y + (message_box_height - total_height) // 2 - 50
        
        # Draw each line of text centered in the box
        for surface in text_surfaces:
            text_rect = surface.get_rect(centerx=screen_width // 2, y=current_y)
            screen.blit(surface, text_rect)
            current_y += surface.get_height() + line_spacing

def check_hand_validity(player_id):
    player_name = "Human" if player_id == 1 else "Computer"
    current_message = game_state2.message
    
    print(f"\nChecking {player_name}'s hand for groups...")  # Debug
    hand_collection = CollectionOfCards(game_state2.player_hands[player_id])
    valid_group = hand_collection.find_valid_group()
    largest_group = hand_collection.find_largest_valid_group()

    game_state2.valid_groups[player_id] = valid_group
    game_state2.largest_groups[player_id] = largest_group
    
    if player_id == game_state2.current_player:
        if not valid_group:
            print(f"No valid group found for {player_name}")  # Debug
            game_state2.message = current_message
        else:
            cards_str = ", ".join(str(card) for card in valid_group)
            print(f"{player_name} has a valid group: {cards_str}")  # Debug
            game_state2.message = "Valid group formed!"  # Simplified message
            
            if player_id == 1:
                game_state2.waiting_for_discard_decision = True
        
        if largest_group and (not valid_group or str(largest_group) != str(valid_group)):
            if len(largest_group) > 3 and not waiting_for_discard_decision:
                cards_str = ", ".join(str(card) for card in largest_group)
                print(f"{player_name} has a larger group: {cards_str}")  # Debug
                game_state2.message = "Larger group formed!"  # Simplified message
    else:
        if not valid_group:
            print(f"No valid group found for {player_name}")  # Debug

def handle_discard(player_id):

    if game_state2.valid_groups[player_id]:
        discarded_cards = [str(card) for card in game_state2.valid_groups[player_id]]
        print(f"{'Human' if player_id == 1 else 'Computer'} discards: {discarded_cards}")
        
        # Find the actual positions of the cards in the player's hand
        start_positions = []
        spacing = 30  # Card spacing
        
        if player_id == 1:  # Human player
            # Calculate total width of all cards
            regular_cards = [card for card in game_state2.player_hands[player_id]
                           if card not in discarded_cards]
            valid_card_strs = [str(card) for card in game_state2.valid_groups[player_id]]
            largest_card_strs = []
            if game_state2.largest_groups[player_id] and len(game_state2.largest_groups[player_id]) > 3:
                largest_card_strs = [str(card) for card in game_state2.largest_groups[player_id]]
                if largest_card_strs == valid_card_strs:
                    largest_card_strs = []
            
            # Calculate starting x position for regular cards
            total_width = (len(regular_cards) * spacing)
            if valid_card_strs:
                total_width += 20 + (len(valid_card_strs) * spacing)
            if largest_card_strs:
                total_width += 60 + (len(largest_card_strs) * spacing)
            
            start_x = (screen_width - total_width) // 2
            base_y = 50  # Human player's y position
            
            # Find positions of cards being discarded
            for card in discarded_cards:
                if card in valid_card_strs:
                    card_index = valid_card_strs.index(card)
                    x = start_x + len(regular_cards) * spacing + 20 + card_index * spacing
                    start_positions.append((x, base_y))
                elif card in largest_card_strs:
                    card_index = largest_card_strs.index(card)
                    x = (start_x + len(regular_cards) * spacing + 20 + len(valid_card_strs) * spacing + 60
                         + card_index * spacing)
                    start_positions.append((x, base_y))
                else:
                    card_index = regular_cards.index(card)
                    x = start_x + card_index * spacing
                    start_positions.append((x, base_y))
                    
        else:  # Computer players
            base_x = screen_width - 150 if player_id == 2 else 50
            base_y = 350
            
            # For computer players, calculate vertical positions
            regular_cards = [card for card in game_state2.player_hands[player_id]
                             if card not in discarded_cards]
            valid_card_strs = [str(card) for card in game_state2.valid_groups[player_id]]
            
            vertical_spacing = 35
            for card in discarded_cards:
                if card in valid_card_strs:
                    card_index = valid_card_strs.index(card)
                    y = base_y + len(regular_cards) * vertical_spacing + 20 + card_index * vertical_spacing
                    start_positions.append((base_x, y))
                else:
                    card_index = regular_cards.index(card)
                    y = base_y + card_index * vertical_spacing
                    start_positions.append((base_x, y))
        
        # End position (deck location)
        end_position = (deck_x, deck_y)
        
        # Store original hand
        original_hand = game_state2.player_hands[player_id][:]
        
        # Animate cards moving to deck
        for step in range(30):
            progress = step / 30
            screen.fill((15, 20, 45))
            
            # Display all players' cards
            for p in range(1, 4):
                if p != player_id:
                    display_cards(p)
                else:
                    # For animating player, show non-discarded cards in their original positions
                    temp_hand = game_state2.player_hands[p][:]
                    game_state2.player_hands[p] = [card for card in original_hand
                                                   if card not in discarded_cards]
                    display_cards(p)
                    game_state2.player_hands[p] = temp_hand
            
            # Draw animating cards
            for i, card in enumerate(discarded_cards):
                start_x, start_y = start_positions[i]
                current_x = start_x + (end_position[0] - start_x) * progress
                current_y = start_y + (end_position[1] - start_y) * progress
                show_card(card, current_x, current_y)
            
            # Draw deck
            if game_state2.full_deck:
                screen.blit(card_back_image, (deck_x, deck_y))
            
            draw_message()
            pygame.display.flip()
            pygame.time.wait(20)
        
        # After animation, update player's hand
        game_state2.player_hands[player_id] = [card for card in game_state2.player_hands[player_id]
                                               if card not in discarded_cards]
        
        # Add cards to deck and shuffle
        game_state2.full_deck.extend(discarded_cards)
        game_state2.shuffle_count = 0
        game_state2.shuffle_complete = False
        
        while not game_state2.shuffle_complete:
            shuffle_deck()
            pygame.display.flip()
            pygame.time.wait(50)
        
        random.shuffle(game_state2.full_deck)

        check_winning_state()

        game_state2.valid_groups[player_id] = None
        game_state2.largest_groups[player_id] = None

        game_state2.message = "Valid group discarded!"
        pygame.time.wait(500)

    game_state2.waiting_for_discard_decision = False
    game_state2.current_player = 2
    game_state2.message = "Computer 1's turn"
    
def handle_card_addition(player_id):
    # Add this print statement
    if player_id == 1:
        print(f"Human adds {len(game_state2.drawn_cards)} cards to hand")
    
    if player_id == game_state2.current_player:
        check_hand_validity(player_id)
        
        if player_id == 1 and game_state2.valid_groups[player_id]:
            game_state2.message = "Do you wish to discard valid group?"
            game_state2.waiting_for_discard_decision = True
            game_state2.message_timer = float('inf')
    else:
        check_hand_validity(player_id)
        game_state2.message_timer = pygame.time.get_ticks()

def handle_initial_deal():
    if all(len(hand) == 5 for hand in game_state2.player_hands.values()):
        game_state2.current_player = 1
        game_state2.message = "Your turn"

def draw_card():
    if game_state2.full_deck:
        return game_state2.full_deck.pop()
    return None

def can_add_cards(player_id, num_cards):
    return len(game_state2.player_hands[player_id]) + num_cards <= game_state2.max_cards_in_hand

def is_hand_full(player_id):
    return len(game_state2.player_hands[player_id]) >= game_state2.max_cards_in_hand

def handle_ai_discard():
    if game_state2.valid_groups[2] is None:
        return False
    
    print("\nComputer discard decision process:")  # Debug 
    print(f"- Valid group available: {[str(card) for card in game_state2.valid_groups[2]]}")  # Debug
    
    random_choice = random.random()
    print(f"- Random value: {random_choice:.2f} (Will discard if < 0.5)")  # Debug
    
    if random_choice < 0.5:
        print("- Decision: Computer WILL discard the group")  # Debug
        discarded_cards = [str(card) for card in game_state2.valid_groups[2]]
        game_state2.full_deck.extend(discarded_cards)
        random.shuffle(game_state2.full_deck)

        game_state2.player_hands[2] = [card for card in game_state2.player_hands[2]
                                       if card not in discarded_cards]

        game_state2.valid_groups[2] = None
        game_state2.largest_groups[2] = None

        game_state2.message = "Computer discards valid group!"
        print(f"- Cards discarded: {discarded_cards}")  # Debug
        print(f"- Remaining hand size: {len(game_state2.player_hands[2])}")  # Debug
        check_winning_state()
        pygame.time.wait(1000)  
        return True
    else:
        print("- Decision: Computer will NOT discard the group")  # Debug
        return False
    
def shuffle_deck():
    screen.fill((15, 20, 45))
    game_state2.shuffle_count += 1

    offset = 5 if game_state2.shuffle_count % 10 < 5 else -5
    deck_bounce_y = deck_y + offset
    screen.blit(card_back_image, (deck_x, deck_bounce_y))

    if game_state2.shuffle_count == 1:
        shuffle_sound.play()

    if game_state2.shuffle_count > 40:
        game_state2.shuffle_complete = True
        random.shuffle(game_state2.full_deck)
        print("Deck shuffled")  # Debug

def return_single_card():

    if game_state2.drawn_cards:
        # Get the last drawn card
        card_to_return = game_state2.drawn_cards.pop()
        
        # Animate the card returning to deck
        start_x = deck_x + deck_width + 20 + (len(game_state2.drawn_cards)) * overlap_spacing
        start_y = deck_y
        end_x = deck_x
        end_y = deck_y
        
        # Perform return animation
        for step in range(30):
            progress = step / 30
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            # Redraw game state
            screen.fill((15, 20, 45))
            display_cards(1)
            display_cards(2)
            display_cards(3)
            
            # Draw remaining drawn cards
            for i, _ in enumerate(game_state2.drawn_cards):
                drawn_card_x = deck_x + deck_width + 20 + i * overlap_spacing
                drawn_card_y = deck_y
                show_card(None, drawn_card_x, drawn_card_y, face_down=True)
            
            # Draw animating card
            show_card(None, current_x, current_y, face_down=True)
            
            # Draw deck
            if game_state2.full_deck:
                screen.blit(card_back_image, (deck_x, deck_y))
            
            draw_message()
            pygame.display.flip()
            pygame.time.wait(10)
        
        # Add the card back to deck and shuffle
        game_state2.full_deck.append(card_to_return)
        random.shuffle(game_state2.full_deck)
        
        cards_left = len(game_state2.drawn_cards)
        if cards_left > 0:
            game_state2.message = f"Card returned. {cards_left} {'cards' if cards_left > 1 else 'card'} left to return"
        else:
            game_state2.message = "All cards returned to deck"
            
        return True
    return False

def snatch_card():

    if is_hand_full(1):
        print("Human cannot snatch - hand full")
        game_state2.message = "Cannot snatch more cards - Human hand is full!"
        return False
        
    if game_state2.player_hands[2]:
        snatched_card = game_state2.player_hands[2].pop(random.randint(0, len(game_state2.player_hands[2]) - 1))
        print(f"Human snatches card: {snatched_card}")
        game_state2.player_hands[1].append(snatched_card)
        
        check_hand_validity(1)
        check_hand_validity(2)
        
        if game_state2.valid_groups[1]:
            game_state2.message = "Do you wish to discard valid group?"
            game_state2.waiting_for_discard_decision = True
            return True
        else:
            game_state2.current_player = 2
            game_state2.message = "Computer's turn"
            return True
    else:
        print("Human cannot snatch - no cards available")
        game_state2.message = "No cards available to snatch!"
        return False

def update_turn_message():
    if game_state2.current_player == 1:
        return "Your turn"
    elif game_state2.current_player == 2:
        return "Computer 1's turn"
    else:
        return "Computer 2's turn"

def draw_card_counter(screen, player_hand_size):
    # Position the counter near the human player's cards
    counter_x = screen_width - 460  # Right side of screen
    counter_y = 200  # Above the player's cards
    font = pygame.font.Font(None, 30)
    counter_text = f"{player_hand_size}/20"
    text_surf = font.render(counter_text, True, (255, 255, 255))
    screen.blit(text_surf, (counter_x, counter_y))

def ai_turn():

    print("\nComputer's turn:")  # Add this print
    if game_state2.current_player == 2 and game_state2.valid_groups[2] is not None:
        if handle_ai_discard():
            print("Computer discards valid group")  # Add this print
            game_state2.current_player = 1
            game_state2.message = "Your turn"
            game_state2.message_timer = pygame.time.get_ticks()
            return
    
    action = random.choice(['draw', 'snatch', 'skip'])
    print(f"Computer chooses to: {action}")  # Add this print
    
    if action == 'draw':
        if is_hand_full(2):
            print("Computer cannot draw - hand full")  # Add this print
            game_state2.message = "Computer's hand is full!"
        else:    
            num_draws = random.randint(1, min(3, game_state2.max_cards_in_hand - len(game_state2.player_hands[2])))
            print(f"Computer draws {num_draws} cards")  # Add this print
            temp_drawn_cards = []

            game_state2.message = f"Computer draws {num_draws} card{'s' if num_draws > 1 else ''}"
            
            for i in range(num_draws):
                card = draw_card()
                if card:
                    temp_drawn_cards.append(card)
                    screen.fill((15, 20, 45))
                    display_cards(1, 50)
                    display_cards(2, 50)
                    
                    if game_state2.full_deck:
                        screen.blit(card_back_image, (deck_x, deck_y))
                    
                    for j in range(len(temp_drawn_cards)):
                        drawn_card_x = deck_x + deck_width + 20 + j * overlap_spacing
                        drawn_card_y = deck_y
                        show_card(None, drawn_card_x, drawn_card_y, face_down=True)
                    
                    draw_message()
                    pygame.display.flip()
                    pygame.time.wait(500)
            
            pygame.time.wait(1000)
            
            start_positions = [(deck_x + deck_width + 20 + i * overlap_spacing, deck_y) 
                             for i in range(len(temp_drawn_cards))]
            end_positions = [(50 + (len(game_state2.player_hands[2]) + i) * 30, 450)
                           for i in range(len(temp_drawn_cards))]
            
            for step in range(30):
                progress = step / 30
                screen.fill((15, 20, 45))
                display_cards(1, 50, 50)
                display_cards(2, 50, 578)
                
                if game_state2.full_deck:
                    screen.blit(card_back_image, (deck_x, deck_y))
                
                for i in range(len(temp_drawn_cards)):
                    start_x, start_y = start_positions[i]
                    end_x, end_y = end_positions[i]
                    current_x = start_x + (end_x - start_x) * progress
                    current_y = start_y + (end_y - start_y) * progress
                    show_card(None, current_x, current_y, face_down=True)
                
                draw_message()
                pygame.display.flip()
                pygame.time.wait(20)

            game_state2.player_hands[2].extend(temp_drawn_cards)
            print(f"Cards drawn: {temp_drawn_cards}")  # Add this print
            check_hand_validity(2)
            
            if game_state2.current_player == 2 and game_state2.valid_groups[2] is not None:
                handle_ai_discard()
                pygame.time.wait(500)
            
    elif action == 'snatch':
        if is_hand_full(2):
            print("Computer cannot snatch - hand full")  # Add this print
            game_state2.message = "Computer's hand is full!"
        elif game_state2.player_hands[1]:
            game_state2.message = "Computer snatches Human's card"
            snatched_index = random.randint(0, len(game_state2.player_hands[1]) - 1)
            snatched_card = game_state2.player_hands[1].pop(snatched_index)
            print(f"Computer snatches: {snatched_card}")  # Add this print
            
            start_x = 50 + snatched_index * 30
            start_y = 10
            end_x = 50 + len(game_state2.player_hands[2]) * 30
            end_y = 450
            
            for step in range(30):
                progress = step / 30
                current_x = start_x + (end_x - start_x) * progress
                current_y = start_y + (end_y - start_y) * progress
                
                screen.fill((15, 20, 45))
                display_cards(1, 50, 50)
                display_cards(2, 50, 578)
                show_card(snatched_card, current_x, current_y)
                draw_message()
                pygame.display.flip()
                pygame.time.wait(20)

            game_state2.player_hands[2].append(snatched_card)
            check_hand_validity(2)
            
            if game_state2.current_player == 2 and game_state2.valid_groups[2] is not None:
                handle_ai_discard()
                pygame.time.wait(500)
        else:
            print("Computer cannot snatch - no cards available")  # Add this print
            game_state2.message = "No cards for Computer to snatch!"
    
    else:
        game_state2.message = "Computer skips turn"
        print("Computer skips turn")  # Add this print
        screen.fill((15, 20, 45))
        display_cards(1, 50, 50)
        display_cards(2, 50, 578)
        draw_message()
        pygame.display.flip()
        pygame.time.wait(1500)
    
    clear_drawn_card_area()
    
    if action != 'skip':
        pygame.time.wait(1500)

    if action == 'snatch':
        check_hand_validity(1)

    game_state2.current_player = 1
    game_state2.drawn_cards.clear()
    game_state2.message = "Your turn"
    game_state2.message_timer = pygame.time.get_ticks()
    game_state2.waiting_for_discard_decision = False
    
    screen.fill((15, 20, 45))
    display_cards(1, 50, 50)
    display_cards(2, 50, 578)
    draw_message()
    pygame.display.flip()

def strategic_ai_turn():

    print("\nStrategic Computer's turn:")  # Add this print
    opponent_hand_size = len(game_state2.player_hands[1])
    own_hand_size = len(game_state2.player_hands[2])
    has_valid_group = game_state2.valid_groups[2] is not None
    has_large_group = game_state2.largest_groups[2] and len(game_state2.largest_groups[2]) > 3
    
    print(f"Current state: Own cards: {own_hand_size}, Opponent cards: {opponent_hand_size}")  # Add this print
    print(f"Has valid group: {has_valid_group}, Has large group: {has_large_group}")  # Add this print
    
    if game_state2.current_player == 2 and (has_valid_group or has_large_group):
        group_to_discard = game_state2.largest_groups[2] if has_large_group else game_state2.valid_groups[2]
        if len(group_to_discard) > 3 or opponent_hand_size < own_hand_size:
            discarded_cards = [str(card) for card in group_to_discard]
            print(f"Computer decides to discard group: {discarded_cards}")  # Add this print
            game_state2.full_deck.extend(discarded_cards)
            random.shuffle(game_state2.full_deck)

            game_state2.player_hands[2] = [card for card in game_state2.player_hands[2]
                             if card not in discarded_cards]

            game_state2.valid_groups[2] = None
            game_state2.largest_groups[2] = None

            game_state2.message = "Computer discards group!"
            pygame.time.wait(1000)
            game_state2.current_player = 1
            game_state2.message = "Your turn"
            game_state2.message_timer = pygame.time.get_ticks()
            return
    
    if opponent_hand_size > 0 and own_hand_size < game_state2.max_cards_in_hand:
        action = 'snatch' if random.random() < 0.7 else 'draw'
    else:
        action = 'draw' if own_hand_size < game_state2.max_cards_in_hand else 'skip'
    
    print(f"Computer chooses to: {action}")  # Add this print
    
    if action == 'draw':
        if is_hand_full(2):
            print("Computer cannot draw - hand full")  # Add this print
            game_state2.message = "Computer's hand is full!"
        else:    
            optimal_draws = min(3, game_state2.max_cards_in_hand - own_hand_size)
            num_draws = random.randint(1, optimal_draws)
            temp_drawn_cards = []

            game_state2.message = f"Computer draws {num_draws} card{'s' if num_draws > 1 else ''}"
            print(f"Computer draws {num_draws} cards")  # Add this print
            
            for _ in range(num_draws):
                card = draw_card()
                if card:
                    temp_drawn_cards.append(card)
                    screen.fill((15, 20, 45))
                    display_cards(1, 50, 50)
                    display_cards(2, 50, 578)
                    
                    if game_state2.full_deck:
                        screen.blit(card_back_image, (deck_x, deck_y))
                    
                    for j in range(len(temp_drawn_cards)):
                        drawn_card_x = deck_x + deck_width + 20 + j * overlap_spacing
                        drawn_card_y = deck_y
                        show_card(None, drawn_card_x, drawn_card_y, face_down=True)
                    
                    draw_message()
                    pygame.display.flip()
                    pygame.time.wait(500)
            
            pygame.time.wait(1000)
            print(f"Cards drawn: {temp_drawn_cards}")  # Add this print
            game_state2.player_hands[2].extend(temp_drawn_cards)
            check_hand_validity(2)
            
    elif action == 'snatch':
        if is_hand_full(2):
            print("Computer cannot snatch - hand full")  # Add this print
            game_state2.message = "Computer's hand is full!"
        elif game_state2.player_hands[1]:
            game_state2.message = "Computer snatches card"
            snatched_index = random.randint(0, len(game_state2.player_hands[1]) - 1)
            snatched_card = game_state2.player_hands[1].pop(snatched_index)
            print(f"Computer snatches: {snatched_card}")  # Add this print
            game_state2.player_hands[2].append(snatched_card)
            check_hand_validity(2)
            
    else:
        game_state2.message = "Computer skips turn"
        print("Computer skips turn")
        pygame.time.wait(1500)
    
    clear_drawn_card_area()
    if action != 'skip':
        pygame.time.wait(1500)

    game_state2.current_player = 1
    game_state2.drawn_cards.clear()
    game_state2.message = "Your turn"
    game_state2.message_timer = pygame.time.get_ticks()
    game_state2.waiting_for_discard_decision = False

def display_game_message(new_message, wait_time=0):
    screen.fill((15, 20, 45))
    display_cards(1)
    display_cards(2)
    display_cards(3)
    if game_state2.full_deck:
        screen.blit(card_back_image, (deck_x, deck_y))
    game_state2.message = new_message
    draw_message()
    pygame.display.flip()
    if wait_time > 0:
        pygame.time.wait(wait_time)

def handle_computer_turn(player_id):

    print(f"\n=== Computer {player_id-1}'s Turn ===")
    display_game_message(f"Computer {player_id-1}'s turn", 1500)
    
    action = random.choice(['draw', 'snatch', 'skip'])
    print(f"Chosen action: {action}")
    
    if action == 'draw':
        if is_hand_full(player_id):
            display_game_message(f"Computer {player_id-1}'s hand is full!")
            print("Hand full - cannot draw")
        else:    
            num_draws = random.randint(1, min(3, game_state2.max_cards_in_hand - len(game_state2.player_hands[player_id])))
            print(f"Drawing {num_draws} cards")
            display_game_message(f"Computer {player_id-1} draws {num_draws} card{'s' if num_draws > 1 else ''}", 500)
            temp_drawn_cards = []
            
            for _ in range(num_draws):
                card = draw_card()
                if card:
                    temp_drawn_cards.append(card)
                    print(f"Drew card: {card}")
                    update_display_with_drawn_cards(temp_drawn_cards)
                    pygame.time.wait(500)

            game_state2.player_hands[player_id].extend(temp_drawn_cards)
            check_hand_validity(player_id)
            
            if game_state2.valid_groups[player_id] is not None:
                group_cards = [str(card) for card in game_state2.valid_groups[player_id]]
                print(f"Valid group formed: {group_cards}")
                display_game_message("Valid group formed!", 1000)  # Simplified message
                if random.random() < 0.5:
                    print("Deciding to discard group")
                    handle_ai_discard()
    
    elif action == 'snatch':
        if is_hand_full(player_id):
            display_game_message(f"Computer {player_id-1}'s hand is full!")
            print("Hand full - cannot snatch")
        elif available_players := [p for p in [1, 2, 3] if p != player_id and game_state2.player_hands[p]]:
            target_player = random.choice(available_players)
            target_name = 'Human' if target_player == 1 else f'Computer {target_player-1}'
            print(f"Snatching from {target_name}")
            display_game_message(f"Computer {player_id-1} snatches a card from {target_name}")
            
            snatched_card = handle_snatch(player_id, target_player)
            print(f"Snatched card: {snatched_card}")
            check_hand_validity(player_id)
            
            if game_state2.valid_groups[player_id] is not None:
                group_cards = [str(card) for card in game_state2.valid_groups[player_id]]
                print(f"Valid group formed: {group_cards}")
                display_game_message("Valid group formed!", 1000)  # Simplified message
                if random.random() < 0.5:
                    print("Deciding to discard group")
                    handle_ai_discard()
        else:
            print("No cards available to snatch")
            display_game_message(f"Computer {player_id-1} cannot snatch - no cards available!")
    else:
        print("Skipping turn")
        display_game_message(f"Computer {player_id-1} skips turn", 1000)
    
    next_player = 1 if player_id == 3 else player_id + 1
    game_state2.current_player = next_player
    game_state2.waiting_for_discard_decision = False

    if next_player == 1:
        display_game_message("Your turn", 1000)

def update_display_with_drawn_cards(temp_drawn_cards):
    screen.fill((15, 20, 45))
    for p in range(1, 4):
        display_cards(p)
    if game_state2.full_deck:
        screen.blit(card_back_image, (deck_x, deck_y))
    for j, _ in enumerate(temp_drawn_cards):
        drawn_card_x = deck_x + deck_width + 20 + j * overlap_spacing
        drawn_card_y = deck_y
        show_card(None, drawn_card_x, drawn_card_y, face_down=True)
    pygame.display.flip()

def handle_snatch(player_id, target_player):
    snatched_index = random.randint(0, len(game_state2.player_hands[target_player]) - 1)
    snatched_card = game_state2.player_hands[target_player].pop(snatched_index)
    game_state2.player_hands[player_id].append(snatched_card)
    pygame.time.wait(1000)
    return snatched_card

# Main game loop
def main_game3_loop():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if game_state2.current_player == 1 and not game_state2.dealing:
                    if not game_state2.waiting_for_discard_decision:
                        if game_state2.shuffle_complete and deck_area.collidepoint(mouse_pos):
                            if is_hand_full(1):
                                game_state2.message = "Cannot draw more cards - Human hand is full!"
                            else:
                                remaining_space = game_state2.max_cards_in_hand - len(game_state2.player_hands[1])
                                max_drawable = min(3 - len(game_state2.drawn_cards), remaining_space)
                                if max_drawable > 0:
                                    drawn_card = draw_card()
                                    if drawn_card:
                                        game_state2.drawn_cards.append(drawn_card)

                        elif button_area.collidepoint(mouse_pos):
                            if len(game_state2.drawn_cards) == 0:
                                print("Human skips turn")
                                game_state2.current_player = 2
                            else:
                                if can_add_cards(game_state2.current_player, len(game_state2.drawn_cards)):
                                    game_state2.player_hands[game_state2.current_player].extend(game_state2.drawn_cards)
                                    handle_card_addition(game_state2.current_player)
                                    game_state2.drawn_cards.clear()
                                    clear_drawn_card_area()
                                    if not game_state2.waiting_for_discard_decision:
                                        game_state2.current_player = 2
                                else:
                                    game_state2.drawn_cards.clear()
                                    clear_drawn_card_area()

                        elif return_button_area.collidepoint(mouse_pos):
                                if game_state2.drawn_cards:
                                    if return_single_card():
                                        print(f"Human returns a card to deck. {len(game_state2.drawn_cards)} cards remaining")
                                    clear_drawn_card_area()

                        # In the snatch1_button_area section:
                        elif snatch1_button_area.collidepoint(mouse_pos):
                            if len(game_state2.drawn_cards) > 0:
                                game_state2.message = "Cannot snatch after drawing cards. Click Done Drawing first."
                            else:
                                if is_hand_full(1):
                                    print("Human cannot snatch - hand full")  # Added print
                                    game_state2.message = "Cannot snatch more cards - Human hand is full!"
                                else:
                                    if game_state2.player_hands[2]:  # Computer 1
                                        snatched_card = game_state2.player_hands[2].pop(random.randint(0, len(game_state2.player_hands[2]) - 1))
                                        print(f"Human snatches from Computer 1: {snatched_card}")  # Added print
                                        game_state2.player_hands[1].append(snatched_card)
                                        game_state2.message = "Snatched card from Computer 1!"
                                        # Only check human's hand as they're the current player
                                        check_hand_validity(1)
                                        if game_state2.valid_groups[1]:
                                            game_state2.message = "Do you wish to discard valid group?"
                                            game_state2.waiting_for_discard_decision = True
                                        else:
                                            game_state2.current_player = 2
                                            game_state2.message = "Computer 1's turn"
                                    else:
                                        print("Human cannot snatch - Computer 1 has no cards")  # Added print
                                        game_state2.message = "No cards available to snatch from Computer 1!"

                        # In the snatch2_button_area section:
                        elif snatch2_button_area.collidepoint(mouse_pos):
                            if len(game_state2.drawn_cards) > 0:
                                game_state2.message = "Cannot snatch after drawing cards. Click Done Drawing first."
                            else:
                                if is_hand_full(1):
                                    print("Human cannot snatch - hand full")  # Added print
                                    game_state2.message = "Cannot snatch more cards - Human hand is full!"
                                else:
                                    if game_state2.player_hands[3]:  # Computer 2
                                        snatched_card = game_state2.player_hands[3].pop(random.randint(0, len(game_state2.player_hands[3]) - 1))
                                        print(f"Human snatches from Computer 2: {snatched_card}")  # Added print
                                        game_state2.player_hands[1].append(snatched_card)
                                        game_state2.message = "Snatched card from Computer 2!"
                                        # Only check human's hand as they're the current player
                                        check_hand_validity(1)
                                        if game_state2.valid_groups[1]:
                                            game_state2.message = "Do you wish to discard valid group?"
                                            game_state2.waiting_for_discard_decision = True
                                        else:
                                            game_state2.current_player = 2
                                            game_state2.message = "Computer 1's turn"
                                    else:
                                        print("Human cannot snatch - Computer 2 has no cards")  # Added print
                                        game_state2.message = "No cards available to snatch from Computer 2!"

                    if game_state2.waiting_for_discard_decision:
                        if yes_button_area.collidepoint(mouse_pos):
                            handle_discard(1)
                        elif no_button_area.collidepoint(mouse_pos):
                            game_state2.waiting_for_discard_decision = False
                            game_state2.current_player = 2
                            game_state2.message = "Computer 1's turn"

        if game_state2.current_player > 1 and not game_state2.dealing and game_state2.shuffle_complete:
            current_time = pygame.time.get_ticks()
            if game_state2.ai_turn_timer == 0:
                game_state2.ai_turn_timer = current_time
            elif current_time - game_state2.ai_turn_timer >= game_state2.ai_turn_delay:
                handle_computer_turn(game_state2.current_player)
                game_state2.ai_turn_timer = 0
                game_state2.message_timer = current_time

        if not game_state2.shuffle_complete:
            shuffle_deck()
        elif game_state2.dealing:
            if game_state2.frame_count % game_state2.deal_frame_delay == 0:
                player_id = (game_state2.dealing_index % 3) + 1
                if len(game_state2.player_hands[player_id]) < 5:
                    card = draw_card()
                    if card:
                        game_state2.player_hands[player_id].append(card)
                        game_state2.dealing_index += 1
                else:
                    if all(len(hand) == 5 for hand in game_state2.player_hands.values()):
                        game_state2.dealing = False
                        handle_initial_deal()
            game_state2.frame_count += 1

        screen.fill((15, 20, 45))

        # Draw player names and hands
        draw_player_name("You", screen_width//2, 200)
        draw_player_name("Computer 1", screen_width - 295, 390)
        draw_player_name("Computer 2", 185, 390)

        display_cards(1)      # Human
        display_cards(2)      # Computer 1
        display_cards(3)      # Computer 2

        draw_card_counter(screen, len(game_state2.player_hands[1]))

        if game_state2.full_deck:
            screen.blit(card_back_image, (deck_x, deck_y))

        # Draw UI elements
        draw_button("Done", button_x, button_y, button_width, button_height)
        draw_button("Return", return_button_x, button_y, button_width, button_height)
        draw_button("Snatch", snatch1_button_x, snatch1_button_y, snatch1_button_width, snatch1_button_height)
        draw_button("Snatch", snatch2_button_x, snatch2_button_y, snatch2_button_width, snatch2_button_height)

        for i, _ in enumerate(game_state2.drawn_cards):
            drawn_card_x = deck_x + deck_width + 20 + i * overlap_spacing
            drawn_card_y = deck_y
            show_card(None, drawn_card_x, drawn_card_y, face_down=True)

        if game_state2.waiting_for_discard_decision:
            game_state2.message = "Do you wish to discard this group?"
            game_state2.message_timer = float('inf')
            draw_discard_buttons()

        current_time = pygame.time.get_ticks()
        if game_state2.message and current_time - game_state2.message_timer > game_state2.MESSAGE_DISPLAY_TIME:
            # Only reset if it's a turn message
            if game_state2.message in ["Your turn", "Computer 1's turn", "Computer 2's turn"]:
                game_state2.message = update_turn_message()
                game_state2.message_timer = current_time

        draw_message()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
