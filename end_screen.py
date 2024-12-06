import pygame
import sys
import random
import math
import subprocess

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Card Game - Winning Screen")
surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
FIREWORK_COLORS = [
    (255, 69, 0),  # Red-Orange
    (255, 215, 0),  # Gold
    (0, 191, 255),  # Deep Sky Blue
    (127, 255, 0),  # Chartreuse
    (238, 130, 238),  # Violet
    (255, 255, 255),  # White
]

# Fonts
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Load Uno card images
notty_card_images = []
for i in range(1, 5): 
    image = pygame.image.load(f"game_images/notty_card_{i}.png").convert_alpha()
    notty_card_images.append(pygame.transform.scale(image, (100, 150)))

# Function to display text
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Firework particle class
class FireworkParticle:
    def __init__(self, x, y, angle, speed, color, lifetime):
        self.x = x
        self.y = y
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.color = color
        self.lifetime = lifetime
        self.alpha = 255

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        self.alpha = max(0, int((self.lifetime / 60) * 255))  

    def draw(self, surface):
        if self.lifetime > 0:
            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y)), 3)

# Create firework explosion
def create_firework_explosion(x, y):
    particles = []
    num_particles = random.randint(50, 100)
    speed = random.uniform(2, 4)
    color = random.choice(FIREWORK_COLORS)
    lifetime = random.randint(30, 60)
    for i in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        particles.append(FireworkParticle(x, y, angle, speed, color, lifetime))
    return particles

# Create and animate card fireworks
def create_card_firework_center():
    """
    Creates a single card firework starting from the center of the screen, moving vertically upward.
    """
    return {
        "image": random.choice(notty_card_images),
        "x": SCREEN_WIDTH // 2 - 50,  
        "y": SCREEN_HEIGHT - 100,    
        "dx": 0,                     
        "dy": -5,                   
        "stage": "launch",
        "timer": 0
    }

def animate_cards(cards, particles):
    for card in cards[:]:
        if card["stage"] == "launch":
            card["x"] += card["dx"]
            card["y"] += card["dy"]
            card["timer"] += 1

            # Transition to "explode" after a set timer
            if card["timer"] > 30:
                card["stage"] = "explode"
                particles.extend(create_firework_explosion(card["x"] + 50, card["y"] + 75))
                cards.remove(card)

        # Draw the card
        screen.blit(card["image"], (card["x"], card["y"]))

# Animate fireworks
def animate_fireworks(particles, surface):
    for particle in particles[:]:
        particle.move()
        particle.draw(surface)
        if particle.lifetime <= 0:
            particles.remove(particle)

# Load crying emoji image
crying_emoji = pygame.image.load("game_images/crying_emoji.png")  
crying_emoji = pygame.transform.scale(crying_emoji, (100, 100))  # Resize as needed

def draw_button(surface, text, x, y, width, height, font, button_color, text_color, hover_color, action=None):
  
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Check if mouse is over the button
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(surface, hover_color, (x, y, width, height))
        if click[0] == 1 and action:
            action()
    else:
        pygame.draw.rect(surface, button_color, (x, y, width, height))

    # Draw the button text
    button_text = font.render(text, True, text_color)
    text_rect = button_text.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(button_text, text_rect)

# Action functions for buttons
def play_again_action():
    """
    Action triggered when the Play Again button is clicked.
    Runs the start_screen.py script to restart the game.
    """
    print("Play Again button clicked!")
    pygame.quit()
    subprocess.run(["python", "start_screen.py"])  # Run start_screen.py
    sys.exit()

def exit_action():
    print("Exit button clicked!")  # Close the game
    pygame.quit()
    sys.exit()

# Modified winning screen function with buttons
def show_winning_screen(winner_name, user_name):
    """
    Display the winning screen.

    :param winner_name: Name of the player who won (from another file).
    :param user_name: Name of the user.
    """
    clock = pygame.time.Clock()
    running = True
    cards = []
    particles = []

    # Check if the user is the winner
    is_user_winner = winner_name == user_name

    # Button dimensions
    button_width = 200
    button_height = 50
    button_y = SCREEN_HEIGHT - 100

    # Game loop
    while running:
        clock.tick(60)
        screen.fill((15, 20, 45))  # Set background color to RGB (15, 20, 45)

        # Determine message based on whether the user won or lost
        if is_user_winner:
            draw_text("Congratulations, You Won!", font, GREEN, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)
        else:
            draw_text("Sorry, You Lost!", font, (255, 0, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)

       

        if is_user_winner:
            # Create a single card firework from one side
            if len(cards) == 0:  # Ensure only one card at a time
                side = "left"  # Set the side for card animation
                cards.append(create_card_firework_center())

            # Animate the single card
            animate_cards(cards, particles)
            animate_fireworks(particles, surface)

        else:
            # Display crying emoji when the user loses
            screen.blit(crying_emoji, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))  # Centered crying emoji

        # Draw buttons
        draw_button(screen, "Play Again", SCREEN_WIDTH // 4 - button_width // 2, button_y, button_width, button_height,
                    small_font, (0, 200, 0), WHITE, (0, 255, 0), play_again_action)
        draw_button(screen, "Exit", 3 * SCREEN_WIDTH // 4 - button_width // 2, button_y, button_width, button_height,
                    small_font, (200, 0, 0), WHITE, (255, 0, 0), exit_action)

        # Blit the surface
        screen.blit(surface, (0, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update display
        pygame.display.flip()

    pygame.quit()
    sys.exit()
# Example usage
if __name__ == "__main__":
    user_name = "Player 1"

    # Assuming the winner's name is fetched from another file
    winner_name = "Player 1"  

    # Show the winning screen
    show_winning_screen(winner_name, user_name)
