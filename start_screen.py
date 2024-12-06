import pygame
import os
import math
import Main_code_2_player
import Main_code_3_player

# Screen dimensions
SCREEN_HEIGHT = 768
SCREEN_WIDTH = 1024

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BACKGROUND_COLOR = (15, 20, 45)  # Background color for the main screen
GREEN = (0, 200, 0)  # Green for "1 Player" and "2 Player" buttons
LIGHT_GREEN = (0, 255, 0)  
RED = (200, 0, 0)  # Red for the "Exit" button
LIGHT_RED = (255, 100, 100) 

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Notty Game Start Screen')

# Fonts
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Load UNO card images
notty_card_images = []
for i in range(1, 5): 
    image = pygame.image.load(f"game_images/notty_card_{i}.png").convert_alpha()
    notty_card_images.append(pygame.transform.scale(image, (80, 120)))

# Initialize snake animation cards
def initialize_snake_cards():
    """
    Initialize snake cards with positions and images.
    """
    snake_cards = []
    card_spacing = 100  # Distance between each card
    num_cards = 10  # Total number of cards in the animation
    for i in range(num_cards):
        x_position = i * card_spacing - card_spacing
        snake_cards.append({
            "x": x_position,
            "y": SCREEN_HEIGHT - 150,
            "image": notty_card_images[i % len(notty_card_images)]
        })
    return snake_cards

# Update and draw snake animation
def update_snake_animation(snake_cards):
    """
    Update the snake animation and draw cards on the screen.
    """
    card_spacing = 100
    for card in snake_cards:
        # Move card horizontally
        card["x"] += 4  
        card["y"] = SCREEN_HEIGHT - 150 + int(20 * math.sin(card["x"] / 50))

        # Reset position if card exits the screen
        if card["x"] > SCREEN_WIDTH:
            card["x"] = -card_spacing

        # Draw the card
        screen.blit(card["image"], (card["x"], card["y"]))

# Function to draw buttons with hover effect
def draw_text_button(text, x, y, width, height, color, hover_color, action=None):
    """
    Draw a button with text.
    """
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, width, height)

    # Change button color on hover
    if button_rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, button_rect)
        if click[0] == 1 and action:
            action()
    else:
        pygame.draw.rect(screen, color, button_rect)

    # Render and draw button text
    button_text = small_font.render(text, True, WHITE)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

# Start screen function
def start_screen():
    """
    Display the main screen with 1 Player, 2 Player, and Exit buttons.
    """
    running = True
    snake_cards = initialize_snake_cards()  # Initialize cards for animation

    while running:
        screen.fill(BACKGROUND_COLOR)  # Set background color

        # Draw the title text
        title_text = font.render("Welcome to Notty Card Game!", True, GOLD)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))

        # Draw the 1 Player, 2 Player, and Exit buttons
        draw_text_button("Play 2 player ", 400, 300, 200, 50, GREEN, LIGHT_GREEN,
                         lambda: run_game("1 Player"))
        draw_text_button("Play 3 Player", 400, 375, 200, 50, GREEN, LIGHT_GREEN,
                         lambda: run_game("2 Player"))
        draw_text_button("Exit", 400, 450, 200, 50, RED, LIGHT_RED,
                         lambda: run_game("Exit"))

        # Update and draw the snake animation
        update_snake_animation(snake_cards)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update the screen
        pygame.display.update()
        pygame.time.delay(30)  # Control frame rate

# Function to run the game based on selection
def run_game(mode):
    """
    Run the game based on the selected mode.
    """
    if mode == "1 Player":
        print("Running 1 Player mode...")
        Main_code_2_player.main_game2_loop()  # Call the 1 Player game loop
    elif mode == "2 Player":
        print("Running 2 Player mode...")
        Main_code_3_player.main_game3_loop()
    elif mode == "Exit":
        print("Exiting game.")
        pygame.quit()
        exit()

# Main program logic
if __name__ == "__main__":
    start_screen()
    pygame.quit()
