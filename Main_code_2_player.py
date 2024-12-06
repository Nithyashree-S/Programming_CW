import pygame
import os
import random
from end_screen import show_winning_screen
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


class GameState:
    def __init__(self):
        # Game state variables
        self.player_hands = {1: [], 2: []}
        self.current_player = 1
        self.draw_count = {1: 0, 2: 0}
        self.max_draw_per_turn = 3
        self.drawn_cards = []
        self.max_cards_in_hand = 20
        self.valid_groups = {1: None, 2: None}
        self.largest_groups = {1: None, 2: None}
        self.ai_turn_delay = 2000
        self.ai_turn_timer = 0
        self.message = ""
        self.message_timer = 0
        self.MESSAGE_DISPLAY_TIME = 2000
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


game_state = GameState()

# Card positioning and dimensions
deck_width, deck_height = 100, 140
overlap_spacing = 30
total_width = deck_width + (game_state.max_draw_per_turn * overlap_spacing) + 20
deck_x = (screen_width - total_width) // 2
deck_y = (screen_height - deck_height) // 2
deck_area = pygame.Rect(deck_x, deck_y, deck_width, deck_height)
yes_button_area = pygame.Rect(125, 400, 40, 30)  # Moved more to the left
no_button_area = pygame.Rect(270, 400, 40, 30)   # Moved more to the right

# Button configurations
button_width, button_height = 200, 50
button_x = 774
button_y = 315
button_area = pygame.Rect(button_x, button_y, button_width, button_height)

snatch_button_width, snatch_button_height = 200, 50
snatch_button_x = 774
snatch_button_y = 405
snatch_button_area = pygame.Rect(snatch_button_x, snatch_button_y, snatch_button_width, snatch_button_height)

# Button for "Play for Me"
play_for_me_button_width, play_for_me_button_height = 200, 50
play_for_me_button_x = 774
play_for_me_button_y = 495  # Positioned below the other buttons
play_for_me_button_area = pygame.Rect(play_for_me_button_x, play_for_me_button_y, play_for_me_button_width,
                                      play_for_me_button_height)

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
    if game_state.waiting_for_discard_decision:
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


def display_cards(player_id, x, y, spacing=30):
    valid_card_strs = []
    largest_card_strs = []
    
    if game_state.valid_groups[player_id]:
        valid_card_strs = [str(card) for card in game_state.valid_groups[player_id]]
    if game_state.largest_groups[player_id] and len(game_state.largest_groups[player_id]) > 3:
        largest_card_strs = [str(card) for card in game_state.largest_groups[player_id]]
    
    regular_cards = [card for card in game_state.player_hands[player_id]
                     if card not in valid_card_strs and card not in largest_card_strs]
    current_x = x
    for i, card in enumerate(regular_cards):
        show_card(card, current_x + i * spacing, y, face_down=False)
    current_x = x + len(regular_cards) * spacing + 20  # Add 50 pixels of space

    if game_state.valid_groups[player_id]:
        for i, card in enumerate(game_state.valid_groups[player_id]):
            show_card(str(card), current_x + i * spacing, y, face_down=False)
        current_x += len(game_state.valid_groups[player_id]) * spacing
    
    if game_state.largest_groups[player_id] and len(game_state.largest_groups[player_id]) > 3:
        if largest_card_strs != valid_card_strs:
            current_x += 60
            
            for i, card in enumerate(game_state.largest_groups[player_id]):
                show_card(str(card), current_x + i * spacing, y, face_down=False)


def draw_player_name(name, x, y, color=(255, 255, 255)):
    font = pygame.font.Font(None, 30)
    text_surf = font.render(name, True, color)
    screen.blit(text_surf, (x, y))


def clear_drawn_card_area():
    clear_rect_x = deck_x + deck_width + 20
    clear_rect_y = deck_y
    clear_rect_width = 3 * 110
    clear_rect_height = 140
    pygame.draw.rect(screen, (0, 128, 0), (clear_rect_x, clear_rect_y, clear_rect_width, clear_rect_height))


def draw_message():
    if game_state.message:
        message_box_x = 50
        message_box_width = deck_x - message_box_x - 20
        message_box_height = deck_height
        message_box_y = deck_y
        
        font_size = 30
        font = pygame.font.Font(None, font_size)
        
        words = game_state.message.split()
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            test_surface = font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= (message_box_width - 40):  
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        text_surfaces = [font.render(line.upper(), True, (255, 255, 255)) for line in lines]
        
        background_surface = pygame.Surface((message_box_width, message_box_height))
        background_surface.set_alpha(128)
        background_surface.fill((0, 0, 0))
        screen.blit(background_surface, (message_box_x, message_box_y))
        
        total_text_height = sum(surface.get_height() for surface in text_surfaces)
        line_spacing = 5
        total_height = total_text_height + (line_spacing * (len(lines) - 1)) if len(lines) > 1 else total_text_height
        current_y = message_box_y + (message_box_height - total_height) // 2
        
        for surface in text_surfaces:
            text_rect = surface.get_rect(centerx=message_box_x + message_box_width // 2, y=current_y)
            screen.blit(surface, text_rect)
            current_y += surface.get_height() + line_spacing


def check_hand_validity(player_id):
    player_name = "You" if player_id == 1 else "Computer"
    current_message = game_state.message
    
    print(f"\nChecking {player_name}'s hand for groups...")  # Debug
    hand_collection = CollectionOfCards(game_state.player_hands[player_id])
    valid_group = hand_collection.find_valid_group()
    largest_group = hand_collection.find_largest_valid_group()

    game_state.valid_groups[player_id] = valid_group
    game_state.largest_groups[player_id] = largest_group
    
    if player_id == game_state.current_player:
        if not valid_group:
            print(f"No valid group found for {player_name}")  # Debug
            game_state.message = current_message
        else:
            cards_str = ", ".join(str(card) for card in valid_group)
            game_state.message = f"{player_name} has a valid group: {cards_str}"
            print(f"{player_name} has a valid group: {cards_str}")  # Debug
            
            if player_id == 1:  # Only show discard prompt for human player
                game_state.message = "Do you wish to discard valid group?"
                game_state.waiting_for_discard_decision = True
        
        if largest_group and (not valid_group or str(largest_group) != str(valid_group)):
            if len(largest_group) > 3 and not game_state.waiting_for_discard_decision:
                cards_str = ", ".join(str(card) for card in largest_group)
                game_state.message = f"{player_name} has a larger group: {cards_str}"
                print(f"{player_name} has a larger group: {cards_str}")  # Debug
    else:
        if not valid_group:
            print(f"No valid group found for {player_name}")  # Debug


def handle_discard(player_id):

    if game_state.valid_groups[player_id]:
        discarded_cards = [str(card) for card in game_state.valid_groups[player_id]]
        
        # Animate cards moving to deck
        start_positions = [(50 + i * 30, 10 if player_id == 1 else 450) for i in range(len(discarded_cards))]
        end_position = (deck_x, deck_y)
        
        for step in range(30):
            progress = step / 30
            screen.fill((15, 20, 45))
            
            remaining_cards = [card for card in game_state.player_hands[player_id] if card not in discarded_cards]
            for i, card in enumerate(remaining_cards):
                x = 50 + i * 30
                y = 10 if player_id == 1 else 450
                show_card(card, x, y)
            
            for i, (start_x, start_y) in enumerate(start_positions):
                current_x = start_x + (end_position[0] - start_x) * progress
                current_y = start_y + (end_position[1] - start_y) * progress
                show_card(discarded_cards[i], current_x, current_y)
            
            other_player = 2 if player_id == 1 else 1
            display_cards(other_player, 50, 450 if player_id == 1 else 10)
            
            draw_message()
            pygame.display.flip()
            pygame.time.wait(20)
        
        # Reuse existing shuffle animation
        game_state.shuffle_count = 0
        game_state.shuffle_complete = False
        while not game_state.shuffle_complete:
            shuffle_deck()
            pygame.display.flip()
            pygame.time.wait(50)

        game_state.full_deck.extend(discarded_cards)
        random.shuffle(game_state.full_deck)

        game_state.player_hands[player_id] = [card for card in game_state.player_hands[player_id]
                                              if card not in discarded_cards]
        
        check_winning_state()

        game_state.valid_groups[player_id] = None
        game_state.largest_groups[player_id] = None

        game_state.message = "Valid group discarded!"
        pygame.time.wait(500)

    game_state.waiting_for_discard_decision = False
    check_hand_validity(2)
    game_state.current_player = 2


def handle_card_addition(player_id):

    if player_id == game_state.current_player:
        check_hand_validity(player_id)
        
        if player_id == 1 and game_state.valid_groups[player_id]:
            game_state.message = "Do you wish to discard valid group?"
            game_state.waiting_for_discard_decision = True
            game_state.message_timer = float('inf')
    else:
        check_hand_validity(player_id)
        game_state.message_timer = pygame.time.get_ticks()


def handle_initial_deal():
    if all(len(hand) == 5 for hand in game_state.player_hands.values()):
        check_hand_validity(1)
        check_hand_validity(2)
        game_state.message = "Your turn"


def draw_card():
    if game_state.full_deck:
        return game_state.full_deck.pop()
    return None


def can_add_cards(player_id, num_cards):
    return len(game_state.player_hands[player_id]) + num_cards <= game_state.max_cards_in_hand


def is_hand_full(player_id):
    return len(game_state.player_hands[player_id]) >= game_state.max_cards_in_hand


def handle_ai_discard():

    if game_state.valid_groups[2] is None:
        return False
    
    print("\nComputer discard decision process:")  # Debug 
    print(f"- Valid group available: {[str(card) for card in game_state.valid_groups[2]]}")  # Debug
    
    random_choice = random.random()
    print(f"- Random value: {random_choice:.2f} (Will discard if < 0.8)")  # Debug
    
    if random_choice < 0.8:
        print("- Decision: Computer WILL discard the group")  # Debug
        discarded_cards = [str(card) for card in game_state.valid_groups[2]]
        game_state.full_deck.extend(discarded_cards)
        random.shuffle(game_state.full_deck)

        game_state.player_hands[2] = [card for card in game_state.player_hands[2]
                                      if card not in discarded_cards]

        game_state.valid_groups[2] = None
        game_state.largest_groups[2] = None

        game_state.message = "Computer discards valid group!"
        print(f"- Cards discarded: {discarded_cards}")  # Debug
        print(f"- Remaining hand size: {len(game_state.player_hands[2])}")  # Debug
        check_winning_state()
        pygame.time.wait(1000)  
        return True
    else:
        print("- Decision: Computer will NOT discard the group")  # Debug
        return False


def ai_turn():

    if game_state.current_player == 2 and game_state.valid_groups[2] is not None:
        if handle_ai_discard():
            check_winning_state()
            game_state.current_player = 1
            game_state.message = "Your turn"
            game_state.message_timer = pygame.time.get_ticks()
            return
    
    action = random.choice(['draw', 'snatch', 'skip'])
    print(f"AI choosing action: {action}")  # Debug
    
    if action == 'draw':
        if is_hand_full(2):
            game_state.message = "Computer's hand is full!"
            print("AI cannot draw - hand full")  # Debug
        else:    
            num_draws = random.randint(1, min(3, game_state.max_cards_in_hand - len(game_state.player_hands[2])))
            temp_drawn_cards = []

            game_state.message = f"Computer draws {num_draws} card{'s' if num_draws > 1 else ''}"
            print(f"AI drawing {num_draws} cards")  # Debug
            
            for i in range(num_draws):
                card = draw_card()
                if card:
                    temp_drawn_cards.append(card)
                    screen.fill((15, 20, 45))
                    display_cards(1, 50, 50)
                    display_cards(2, 50, 578)
                    
                    if game_state.full_deck:
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
            end_positions = [(50 + (len(game_state.player_hands[2]) + i) * 30, 450)
                             for i in range(len(temp_drawn_cards))]
            
            for step in range(30):
                progress = step / 30
                screen.fill((15, 20, 45))
                display_cards(1, 50, 50)
                display_cards(2, 50, 578)
                
                if game_state.full_deck:
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

            game_state.player_hands[2].extend(temp_drawn_cards)
            check_hand_validity(2)
            
            if game_state.current_player == 2 and game_state.valid_groups[2] is not None:
                handle_ai_discard()
                pygame.time.wait(500)
            
    elif action == 'snatch':
        if is_hand_full(2):
            game_state.message = "Computer's hand is full!"
            print("AI cannot snatch - hand full")  # Debug
        elif game_state.player_hands[1]:
            game_state.message = "Computer snatches Your card"
            print("AI snatching card from human")  # Debug
            
            snatched_index = random.randint(0, len(game_state.player_hands[1]) - 1)
            snatched_card = game_state.player_hands[1].pop(snatched_index)
            
            start_x = 50 + snatched_index * 30
            start_y = 10
            end_x = 50 + len(game_state.player_hands[2]) * 30
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

            game_state.player_hands[2].append(snatched_card)
            check_hand_validity(2)
            
            if game_state.current_player == 2 and game_state.valid_groups[2] is not None:
                handle_ai_discard()
                pygame.time.wait(500)
        else:
            game_state.message = "No cards for Computer to snatch!"
            print("AI cannot snatch - no cards available")  # Debug
    
    else:
        game_state.message = "Computer skips turn"
        print("AI skipping turn")  # Debug
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

    game_state.current_player = 1
    game_state.drawn_cards.clear()
    game_state.message = "Your turn"
    game_state.message_timer = pygame.time.get_ticks()
    game_state.waiting_for_discard_decision = False
    
    screen.fill((15, 20, 45))
    display_cards(1, 50, 50)
    display_cards(2, 50, 578)
    draw_message()
    pygame.display.flip()


def shuffle_deck():
    screen.fill((15, 20, 45))
    game_state.shuffle_count += 1

    offset = 5 if game_state.shuffle_count % 10 < 5 else -5
    deck_bounce_y = deck_y + offset
    screen.blit(card_back_image, (deck_x, deck_bounce_y))

    if game_state.shuffle_count == 1:
        shuffle_sound.play()

    if game_state.shuffle_count > 40:
        game_state.shuffle_complete = True
        random.shuffle(game_state.full_deck)
        print("Deck shuffled")  # Debug


def snatch_card():

    if is_hand_full(1):
        print("You cannot snatch - hand full")  # Debug
        game_state.message = "Cannot snatch more cards - Your hand is full!"
        return False
        
    if game_state.player_hands[2]:
        snatched_card = game_state.player_hands[2].pop(random.randint(0, len(game_state.player_hands[2]) - 1))
        print(f"You snatch card: {snatched_card}")  # Debug
        game_state.player_hands[1].append(snatched_card)
        
        check_hand_validity(1)
        
        if game_state.valid_groups[1]:
            game_state.message = "Do you wish to discard valid group?"
            game_state.waiting_for_discard_decision = True
            return True
        else:
            check_hand_validity(2)
            game_state.current_player = 2
            game_state.message = "Computer's turn"
            return True
    else:
        print("You cannot snatch - no cards available")  # Debug
        game_state.message = "No cards available to snatch!"
        return False


def play_for_me():
    if is_hand_full(1):
        game_state.message = "Cannot play - Human hand is full!"
        return

    # Simulate computer decision-making for the player
    if random.random() < 0.8:  # 80% chance to draw cards
        num_draws = random.randint(1, min(3, game_state.max_cards_in_hand - len(game_state.player_hands[1])))
        for _ in range(num_draws):
            card = draw_card()
            if card:
                game_state.player_hands[1].append(card)
        game_state.message = f"Drew {num_draws} card(s)!"
    else:  # Snatch action
        if game_state.player_hands[2]:
            snatched_card = game_state.player_hands[2].pop(random.randint(0, len(game_state.player_hands[2]) - 1))
            game_state.player_hands[1].append(snatched_card)
            game_state.message = f"Snatched a card from the Computer!"
        else:
            game_state.message = "No cards available to snatch!"

    # Check for valid groups
    check_hand_validity(1)

    # Handle discard if there's a valid group
    if game_state.valid_groups[1]:
        handle_discard(1)

    # End turn
    game_state.current_player = 2
    game_state.drawn_cards.clear()
    clear_drawn_card_area()
    game_state.message = "Computer's turn"


def check_winning_state():  # check win function
    if len(game_state.player_hands[1]) == 0:
        winner_name = game_state.user_name  # The human player wins
        print("Player wins!")
        show_winning_screen(winner_name, game_state.user_name)  # Show the winning screen
        return True

    elif len(game_state.player_hands[2]) == 0:
        winner_name = "Computer"  # The computer wins
        print("Computer wins!")
        show_winning_screen(winner_name, game_state.user_name)  # Show the losing screen
        return True

    return False


# Main game loop
def main_game2_loop():

    global deck_x, deck_y

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if game_state.current_player == 1 and not game_state.dealing:
                    if not game_state.waiting_for_discard_decision:
                        if game_state.shuffle_complete and deck_area.collidepoint(mouse_pos):
                            if is_hand_full(1):
                                print("You cannot draw - hand full")  # Debug
                                game_state.message = "Cannot draw more cards - Your hand is full!"
                            else:
                                remaining_space = game_state.max_cards_in_hand - len(game_state.player_hands[1])
                                max_drawable = min(3 - len(game_state.drawn_cards), remaining_space)
                                if max_drawable > 0:
                                    drawn_card = draw_card()
                                    if drawn_card:
                                        game_state.drawn_cards.append(drawn_card)
                                        print(f"You draw card: {drawn_card}")  # Debug
                        
                        elif button_area.collidepoint(mouse_pos):
                            if len(game_state.drawn_cards) == 0:
                                print("You skip turn")  # Debug
                                game_state.current_player = 2
                            else:
                                if can_add_cards(game_state.current_player, len(game_state.drawn_cards)):
                                    game_state.player_hands[game_state.current_player].extend(game_state.drawn_cards)
                                    handle_card_addition(game_state.current_player)
                                    game_state.drawn_cards.clear()
                                    clear_drawn_card_area()
                                    if not game_state.waiting_for_discard_decision:
                                        game_state.current_player = 2
                                else:
                                    print("You cannot add cards - hand limit exceeded")  # Debug
                                    game_state.drawn_cards.clear()
                                    clear_drawn_card_area()
                        
                        elif snatch_button_area.collidepoint(mouse_pos):
                            if len(game_state.drawn_cards) > 0:
                                print("Cannot snatch after drawing cards")  # Debug
                                game_state.message = "Cannot snatch after drawing cards. Click Done Drawing first."
                            else:
                                if is_hand_full(1):
                                    print("You cannot snatch - hand full")  # Debug
                                    game_state.message = "Cannot snatch more cards - Your hand is full!"
                                else:
                                    snatch_card()

                        elif play_for_me_button_area.collidepoint(mouse_pos) and game_state.current_player == 1:
                            play_for_me()

                    if game_state.waiting_for_discard_decision:
                        if yes_button_area.collidepoint(mouse_pos):
                            handle_discard(1)
                        elif no_button_area.collidepoint(mouse_pos):
                            game_state.waiting_for_discard_decision = False
                            game_state.current_player = 2
                            game_state.message = "Computer's turn"

        if game_state.current_player == 2 and not game_state.dealing and game_state.shuffle_complete:
            current_time = pygame.time.get_ticks()
            if game_state.ai_turn_timer == 0:
                game_state.ai_turn_timer = current_time
            elif current_time - game_state.ai_turn_timer >= game_state.ai_turn_delay:
                ai_turn()
                game_state.ai_turn_timer = 0
                game_state.message_timer = current_time
        elif game_state.current_player == 1 and not game_state.dealing and game_state.shuffle_complete:
            game_state.message = "Your turn"

        if not game_state.shuffle_complete:
            shuffle_deck()
        elif game_state.dealing:
            if game_state.frame_count % game_state.deal_frame_delay == 0:
                player_id = (game_state.dealing_index % 2) + 1
                if len(game_state.player_hands[player_id]) < 5:
                    card = draw_card()
                    if card:
                        game_state.player_hands[player_id].append(card)
                        game_state.dealing_index += 1
                        print(f"Dealing card to Player {player_id}: {card}")  # Debug
                else:
                    if all(len(hand) == 5 for hand in game_state.player_hands.values()):
                        game_state.dealing = False
                        handle_initial_deal()
                        print("Initial dealing complete")  # Debug

            game_state.frame_count += 1

        screen.fill((15, 20, 45))
        
        draw_player_name("You", 50, 210)
        draw_player_name("Computer", 50, 532)
        
        display_cards(1, 50, 50)
        display_cards(2, 50, 578)

        if game_state.full_deck:
            screen.blit(card_back_image, (deck_x, deck_y))

        draw_button("Done Drawing", button_x, button_y, button_width, button_height)
        draw_button("Snatch", snatch_button_x, snatch_button_y, snatch_button_width, snatch_button_height,
                    color=(0, 122, 204))
        draw_button("Play for Me", play_for_me_button_x, play_for_me_button_y, play_for_me_button_width,
                    play_for_me_button_height, color=(0, 122, 204))

        # Display drawn cards
        for i, _ in enumerate(game_state.drawn_cards):
            drawn_card_x = deck_x + deck_width + 20 + i * overlap_spacing
            drawn_card_y = deck_y
            show_card(None, drawn_card_x, drawn_card_y, face_down=True)

        if game_state.waiting_for_discard_decision:
            game_state.message = "Do you wish to discard this group?"
        message_timer = float('inf') 

        # Message handling
        current_time = pygame.time.get_ticks()
        if game_state.waiting_for_discard_decision:
            game_state.message = "Do you wish to discard this group?"
            game_state.message_timer = float('inf')
        elif game_state.message and current_time - message_timer > game_state.MESSAGE_DISPLAY_TIME:
            if game_state.current_player == 1:
                game_state.message = "Your turn"
            else:
                game_state.message = ""
            game_state.message_timer = current_time

        draw_message()
        if game_state.waiting_for_discard_decision:
            draw_discard_buttons()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main_game2_loop()
