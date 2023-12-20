# # # ```python
import pygame

# Initialize Pygame
pygame.init()

# Define the size of the window and grid
width, height = 800, 600
rows, cols = 15, 15
cell_size = min(width, height) // max(rows, cols)

# Create the window
window = pygame.display.set_mode((width, height))

# Set the title of the window
pygame.display.set_caption("Gobang Game")

# Define colors and fonts
bg_color = (220, 220, 220)
lines_color = (0, 0, 0)
player1_color = (255, 0, 0)
player2_color = (0, 0, 255)
button_color = (100, 200, 100)
status_font = pygame.font.SysFont(None, 48)
button_font = pygame.font.SysFont(None, 36)

# Define the restart button properties
button_rect = pygame.Rect(width - 150, height - 50, 140, 40)
button_label = button_font.render('Restart', True, (255, 255, 255))

# Status area position
status_x = width // 2
status_y = height - 40

# Initialize the game board
board = [[None for _ in range(cols)] for _ in range(rows)]
current_player = 1
winner = None

# Function definitions
def draw_board(surface):
    surface.fill(bg_color)
    for i in range(rows):
        pygame.draw.line(surface, lines_color, (0, i * cell_size), (cols * cell_size, i * cell_size))
    for j in range(cols):
        pygame.draw.line(surface, lines_color, (j * cell_size, 0), (j * cell_size, rows * cell_size))

def draw_stones(surface):
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 1:
                pygame.draw.circle(surface, player1_color,
                                   (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2),
                                   cell_size // 2 - 5)
            elif board[row][col] == 2:
                pygame.draw.circle(surface, player2_color,
                                   (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2),
                                   cell_size // 2 - 5)

def draw_restart_button(surface):
    pygame.draw.rect(surface, button_color, button_rect)
    surface.blit(button_label, button_label.get_rect(center=button_rect.center))

def draw_status(surface, message):
    status_message = status_font.render(message, True, (0, 0, 0))
    surface.blit(status_message, status_message.get_rect(center=(status_x, status_y)))

def reset_game():
    global board, current_player, winner
    board = [[None for _ in range(cols)] for _ in range(rows)]
    current_player = 1
    winner = None

def check_win(row, col, player):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 0
        for i in range(-4, 5):
            r = row + dr * i
            c = col + dc * i
            if 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
                count += 1
                if count == 5:
                    return player
            else:
                count = 0
    return None

def handle_player_input(pos):
    global current_player, winner
    x, y = pos
    col = x // cell_size
    row = y // cell_size
    if board[row][col] is None:
        board[row][col] = current_player
        if check_win(row, col, current_player):
            winner = current_player
            draw_status(window, f"Player {winner} wins!")
        current_player = 1 if current_player == 2 else 2

# Main loop to keep the window open
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                reset_game()
            elif winner is None:
                handle_player_input(event.pos)

    # Draw the game board, stones, restart button, and status message
    draw_board(window)
    draw_stones(window)
    draw_restart_button(window)
    if winner:
        draw_status(window, f"Player {winner} wins!")
    else:
        draw_status(window, f"Player {current_player}'s turn")

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
# # # ```
# # #
# # # The above code is a complete implementation of the specified features for the Pygame-based Gobang game. It includes the creation of the game window, drawing the board and stones, handling player input, checking win conditions, providing a restart button, and displaying status messages. The main loop handles game events and updates the display accordingly. When the player wants to quit the game, Pygame is properly shut down.
