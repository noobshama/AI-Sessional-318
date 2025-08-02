# Updated human_player.py without timeout logic
import pygame
import os
import time
import sys
import math
import json

ROWS, COLS = 9, 6
FILENAME = "gamestate.txt"
CONFIG_FILE = "game_config.json"
CELL_SIZE = 75
WIDTH, HEIGHT = COLS * CELL_SIZE + 100, ROWS * CELL_SIZE + 200

# Enhanced Modern Colors
WHITE = (255, 255, 255)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
BLACK = (0, 0, 0)
GRAY = (189, 195, 199)
DARK_GRAY = (52, 73, 94)
LIGHT_GRAY = (236, 240, 241)
GREEN = (46, 204, 113)
GOLD = (241, 196, 15)
PURPLE = (155, 89, 182)
ORANGE = (230, 126, 34)

# UI Colors
BACKGROUND = (248, 249, 250)
CARD_BACKGROUND = (255, 255, 255)
ACCENT_PRIMARY = (52, 152, 219)
ACCENT_SECONDARY = (155, 89, 182)
TEXT_PRIMARY = (44, 62, 80)
TEXT_SECONDARY = (127, 140, 141)
SUCCESS_COLOR = (46, 204, 113)
WARNING_COLOR = (230, 126, 34)
DANGER_COLOR = (231, 76, 60)

# Gradient colors for better UI
RED_GRADIENT_START = (255, 120, 120)
RED_GRADIENT_END = (231, 76, 60)
BLUE_GRADIENT_START = (120, 180, 255)
BLUE_GRADIENT_END = (52, 152, 219)
HOVER_HIGHLIGHT = (255, 235, 59)

# Level configurations
LEVEL_CONFIG = {
    1: {"name": "Beginner", "color": SUCCESS_COLOR, "description": "Simple orb counting"},
    2: {"name": "Easy", "color": ACCENT_PRIMARY, "description": "Considers critical mass"},
    3: {"name": "Medium", "color": WARNING_COLOR, "description": "Strategic positioning"},
    4: {"name": "Hard", "color": DANGER_COLOR, "description": "Conversion potential"},
    5: {"name": "Expert", "color": ACCENT_SECONDARY, "description": "Full AI capabilities"}
}

# Pre-calculate critical masses and neighbors for efficiency
CRITICAL_MASS = {}
NEIGHBORS = {}

for r in range(ROWS):
    for c in range(COLS):
        # Critical mass
        if (r in [0, ROWS-1]) and (c in [0, COLS-1]):
            CRITICAL_MASS[(r, c)] = 2  # Corner
        elif r in [0, ROWS-1] or c in [0, COLS-1]:
            CRITICAL_MASS[(r, c)] = 3  # Edge
        else:
            CRITICAL_MASS[(r, c)] = 4  # Interior
        
        # Neighbors
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                neighbors.append((nr, nc))
        NEIGHBORS[(r, c)] = neighbors

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chain Reaction - Human vs AI")

# Enhanced font setup
try:
    title_font = pygame.font.SysFont('Segoe UI', 28, bold=True)
    font = pygame.font.SysFont('Segoe UI', 18, bold=True)
    large_font = pygame.font.SysFont('Segoe UI', 32, bold=True)
    small_font = pygame.font.SysFont('Segoe UI', 14)
    tiny_font = pygame.font.SysFont('Segoe UI', 12)
except:
    title_font = pygame.font.SysFont('Arial', 28, bold=True)
    font = pygame.font.SysFont('Arial', 18, bold=True)
    large_font = pygame.font.SysFont('Arial', 32, bold=True)
    small_font = pygame.font.SysFont('Arial', 14)
    tiny_font = pygame.font.SysFont('Arial', 12)

# Initialize mixer for sound
pygame.mixer.init()

def draw_card(surface, rect, color=CARD_BACKGROUND, border_color=None, border_width=0, shadow=True, border_radius=8):
    """Draw a modern card with shadow effect"""
    if shadow:
        shadow_rect = rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height))
        shadow_surface.set_alpha(40)
        shadow_surface.fill(BLACK)
        surface.blit(shadow_surface, shadow_rect)
    
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=border_radius)

def draw_gradient_rect(surface, rect, color1, color2, vertical=True):
    """Draw a gradient rectangle"""
    if vertical:
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))
    else:
        for x in range(rect.width):
            ratio = x / rect.width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x + x, rect.y), (rect.x + x, rect.y + rect.height))

def create_sound_wave(frequency, duration, sample_rate=22050):
    """Create a simple sine wave sound"""
    try:
        import numpy as np
        frames = int(duration * sample_rate)
        time_array = np.linspace(0, duration, frames)
        wave = np.sin(2 * np.pi * frequency * time_array)
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        stereo_wave = np.ascontiguousarray(stereo_wave)
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound
    except ImportError:
        print("NumPy not available, sounds disabled")
        return None
    except Exception as e:
        print(f"Sound creation failed: {e}")
        return None

# Create sound effects
move_sound = create_sound_wave(440, 0.2)
win_sound = create_sound_wave(523, 0.5)
explosion_sound = create_sound_wave(200, 0.3)

def load_game_config():
    """Load game configuration including difficulty level"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"level": 1}

def parse_board(lines):
    board = []
    for line in lines:
        row = []
        parts = line.strip().split()
        for p in parts:
            if p == '0':
                row.append(None)
            else:
                count = int(p[:-1])
                color = p[-1]
                row.append((count, color))
        board.append(row)
    return board

def board_to_lines(board):
    lines = []
    for row in board:
        line = []
        for cell in row:
            if cell is None:
                line.append('0')
            else:
                count, color = cell
                line.append(f"{count}{color}")
        lines.append(' '.join(line))
    return lines

def explode(board, max_iterations=1000):
    """Handle chain reactions after a move with max iterations"""
    explosion_count = 0
    
    while explosion_count < max_iterations:
        explosion_count += 1
        
        to_explode = []
        
        for r in range(ROWS):
            for c in range(COLS):
                cell = board[r][c]
                if cell and cell[0] >= CRITICAL_MASS[(r, c)]:
                    to_explode.append((r, c, cell[0], cell[1]))
        
        if not to_explode:
            break
        
        for r, c, count, color in to_explode:
            critical = CRITICAL_MASS[(r, c)]
            remaining = count - critical
            
            board[r][c] = (remaining, color) if remaining > 0 else None

            for nr, nc in NEIGHBORS[(r, c)]:
                neighbor = board[nr][nc]
                if neighbor is None:
                    board[nr][nc] = (1, color)
                else:
                    board[nr][nc] = (neighbor[0] + 1, color)
    
    if explosion_count >= max_iterations:
        print(f" Explosion stopped after maximum {max_iterations} iterations")
    
    return explosion_count

def check_winner(board):
    """Check if there's a winner"""
    red_exists = blue_exists = False
    total_orbs = 0
    
    for row in board:
        for cell in row:
            if cell:
                total_orbs += cell[0]
                if cell[1] == 'R':
                    red_exists = True
                elif cell[1] == 'B':
                    blue_exists = True
                    
                if red_exists and blue_exists:
                    return None
    
    # Only declare winner if we have enough orbs on board (both players have played)
    if total_orbs < 2:
        return None
    
    if red_exists and not blue_exists:
        return 'R'
    elif blue_exists and not red_exists:
        return 'B'
    return None

def write_human_move(filename, board):
    lines = ["Human Move:"] + board_to_lines(board)
    with open(filename, 'w') as f:
        f.write('\n'.join(lines) + '\n')

def read_ai_move_or_gameover(filename):
    while True:
        if not os.path.exists(filename):
            time.sleep(0.2)
            continue
        with open(filename, 'r') as f:
            lines = f.readlines()
        if len(lines) < ROWS + 1:
            time.sleep(0.2)
            continue
        header = lines[0].strip()
        if header.startswith("Game Over:"):
            return header, None
        if header != "AI Move:":
            time.sleep(0.2)
            continue
        return None, parse_board(lines[1:1+ROWS])

def get_critical_mass(r, c):
    """Calculate critical mass based on position"""
    if (r == 0 or r == ROWS-1) and (c == 0 or c == COLS-1):
        return 2
    elif r == 0 or r == ROWS-1 or c == 0 or c == COLS-1:
        return 3
    else:
        return 4

def draw_orbs_in_cell(surface, center_x, center_y, count, color, cell_size):
    """Draw enhanced individual orbs based on count"""
    orb_color = RED if color == 'R' else BLUE
    orb_light_color = RED_GRADIENT_START if color == 'R' else BLUE_GRADIENT_START
    orb_radius = min(10, cell_size // 9)
    
    if count == 1:
        pygame.draw.circle(surface, orb_light_color, (center_x, center_y), orb_radius + 3)
        pygame.draw.circle(surface, orb_color, (center_x, center_y), orb_radius)
        pygame.draw.circle(surface, WHITE, (center_x - 3, center_y - 3), orb_radius // 3)
        
    elif count == 2:
        offset = cell_size // 7
        positions = [(center_x - offset, center_y), (center_x + offset, center_y)]
        for pos in positions:
            pygame.draw.circle(surface, orb_light_color, pos, orb_radius + 2)
            pygame.draw.circle(surface, orb_color, pos, orb_radius)
            pygame.draw.circle(surface, WHITE, (pos[0] - 2, pos[1] - 2), orb_radius // 3)
            
    elif count == 3:
        offset = cell_size // 8
        positions = [
            (center_x, center_y - offset),
            (center_x - offset, center_y + offset // 2),
            (center_x + offset, center_y + offset // 2)
        ]
        for pos in positions:
            pygame.draw.circle(surface, orb_light_color, pos, orb_radius + 2)
            pygame.draw.circle(surface, orb_color, pos, orb_radius)
            pygame.draw.circle(surface, WHITE, (pos[0] - 2, pos[1] - 2), orb_radius // 3)
            
    elif count >= 4:
        offset = cell_size // 8
        positions = [
            (center_x - offset, center_y - offset),
            (center_x + offset, center_y - offset),
            (center_x - offset, center_y + offset),
            (center_x + offset, center_y + offset)
        ]
        for pos in positions:
            pygame.draw.circle(surface, orb_light_color, pos, orb_radius + 2)
            pygame.draw.circle(surface, orb_color, pos, orb_radius)
            pygame.draw.circle(surface, WHITE, (pos[0] - 2, pos[1] - 2), orb_radius // 3)
        
        if count > 4:
            text = small_font.render(str(count), True, TEXT_PRIMARY)
            text_rect = text.get_rect(center=(center_x, center_y))
            
            bg_radius = max(text_rect.width, text_rect.height) // 2 + 6
            pygame.draw.circle(surface, WHITE, (center_x, center_y), bg_radius + 2)
            pygame.draw.circle(surface, orb_color, (center_x, center_y), bg_radius + 1, 2)
            pygame.draw.circle(surface, WHITE, (center_x, center_y), bg_radius)
            
            surface.blit(text, text_rect)

def draw_board(board, level, selected_cell=None, waiting_for_ai=False):
    # Background
    screen.fill(BACKGROUND)
    
    # Header section
    header_height = 100
    header_rect = pygame.Rect(0, 0, WIDTH, header_height)
    draw_gradient_rect(screen, header_rect, DARK_GRAY, (70, 90, 110))
    
    # Title
    title_text = title_font.render("Human vs AI", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH//2, 25))
    screen.blit(title_text, title_rect)
    
    # Player cards
    card_width = 150
    card_height = 50
    card_y = 45
    
    # Human player card
    human_card = pygame.Rect(20, card_y, card_width, card_height)
    human_active = not waiting_for_ai
    human_color = RED if human_active else CARD_BACKGROUND
    human_text_color = WHITE if human_active else RED
    draw_card(screen, human_card, human_color, RED, 2 if human_active else 1, shadow=True)
    
    human_title = font.render("You", True, human_text_color)
    human_title_rect = human_title.get_rect(center=(human_card.centerx, human_card.centery - 8))
    screen.blit(human_title, human_title_rect)
    
    # Count orbs for each player
    red_orbs = blue_orbs = 0
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if cell:
                count, color = cell
                if color == 'R':
                    red_orbs += count
                else:
                    blue_orbs += count
    
    human_count = small_font.render(f"{red_orbs} orbs", True, human_text_color)
    human_count_rect = human_count.get_rect(center=(human_card.centerx, human_card.centery + 10))
    screen.blit(human_count, human_count_rect)
    
    # AI player card
    ai_card = pygame.Rect(WIDTH - card_width - 20, card_y, card_width, card_height)
    ai_active = waiting_for_ai
    ai_color = BLUE if ai_active else CARD_BACKGROUND
    ai_text_color = WHITE if ai_active else BLUE
    draw_card(screen, ai_card, ai_color, BLUE, 2 if ai_active else 1, shadow=True)
    
    level_info = LEVEL_CONFIG[level]
    ai_title = font.render(f"AI L{level}", True, ai_text_color)
    ai_title_rect = ai_title.get_rect(center=(ai_card.centerx, ai_card.centery - 8))
    screen.blit(ai_title, ai_title_rect)
    
    ai_count = small_font.render(f"{blue_orbs} orbs", True, ai_text_color)
    ai_count_rect = ai_count.get_rect(center=(ai_card.centerx, ai_card.centery + 10))
    screen.blit(ai_count, ai_count_rect)
    
    # Center info card
    center_card = pygame.Rect(WIDTH//2 - 100, card_y, 200, card_height)
    draw_card(screen, center_card, CARD_BACKGROUND, GRAY, 1, shadow=True)
    
    # Game status
    if waiting_for_ai:
        status_text = font.render("AI Thinking...", True, BLUE)
    else:
        status_text = font.render("Your Turn", True, RED)
    status_rect = status_text.get_rect(center=(center_card.centerx, center_card.centery - 8))
    screen.blit(status_text, status_rect)
    
    # AI level info
    level_text = small_font.render(f"Level {level}: {level_info['name']}", True, level_info['color'])
    level_rect = level_text.get_rect(center=(center_card.centerx, center_card.centery + 10))
    screen.blit(level_text, level_rect)
    
    # Game board
    board_start_y = header_height + 20
    board_rect = pygame.Rect(50, board_start_y, COLS * CELL_SIZE, ROWS * CELL_SIZE)
    draw_card(screen, board_rect, WHITE, GRAY, 2, shadow=True, border_radius=12)
    
    for r in range(ROWS):
        for c in range(COLS):
            x = 50 + c * CELL_SIZE
            y = board_start_y + r * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            
            if (r + c) % 2 == 0:
                cell_color = (250, 250, 250)
            else:
                cell_color = (245, 245, 245)
            
            # Highlight selected cell
            if selected_cell == (r, c):
                cell_color = HOVER_HIGHLIGHT
                pygame.draw.rect(screen, cell_color, cell_rect, border_radius=4)
                pygame.draw.rect(screen, GOLD, cell_rect, 3, border_radius=4)
            else:
                pygame.draw.rect(screen, cell_color, cell_rect)
            
            pygame.draw.rect(screen, (220, 220, 220), cell_rect, 1)
            
            # Critical mass indicators
            critical_mass = get_critical_mass(r, c)
            dot_color = (200, 200, 200) if selected_cell != (r, c) else (180, 180, 180)
            for i in range(critical_mass):
                dot_x = x + 6 + (i % 2) * 8
                dot_y = y + 6 + (i // 2) * 8
                pygame.draw.circle(screen, dot_color, (dot_x, dot_y), 2)
            
            # Draw orbs
            cell = board[r][c]
            if cell:
                count, color = cell
                center_x = x + CELL_SIZE // 2
                center_y = y + CELL_SIZE // 2
                
                if count >= critical_mass:
                    glow_color = GOLD
                    for i in range(3):
                        pygame.draw.circle(screen, glow_color, (center_x, center_y), 
                                         CELL_SIZE // 2 - 8 + i, 1)
                
                draw_orbs_in_cell(screen, center_x, center_y, count, color, CELL_SIZE)
    
    # Instructions panel
    instruction_panel_y = board_start_y + ROWS * CELL_SIZE + 20
    instruction_rect = pygame.Rect(20, instruction_panel_y, WIDTH - 40, 60)
    draw_card(screen, instruction_rect, CARD_BACKGROUND, GRAY, 1, shadow=True)
    
    # Instructions
    if waiting_for_ai:
        instruction_lines = [
            "Please wait for AI to make its move...",
            "The AI is analyzing the board position"
        ]
        text_color = BLUE
    else:
        instruction_lines = [
            "Click on any empty cell or your own orbs to place",
            "Reach critical mass to trigger chain reactions!"
        ]
        text_color = TEXT_SECONDARY
    
    for i, line in enumerate(instruction_lines):
        instruction_text = small_font.render(line, True, text_color)
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, instruction_panel_y + 20 + i * 20))
        screen.blit(instruction_text, instruction_rect)
    
    pygame.display.flip()

def is_valid_human_move(board, r, c):
    cell = board[r][c]
    return (cell is None) or (cell[1] == 'R')

def apply_human_move(board, r, c):
    count = board[r][c][0] if board[r][c] else 0
    board[r][c] = (count + 1, 'R')

def show_game_over_message(message):
    # Create overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Game over card
    card_width, card_height = 350, 250
    card_rect = pygame.Rect(WIDTH//2 - card_width//2, HEIGHT//2 - card_height//2, card_width, card_height)
    draw_card(screen, card_rect, CARD_BACKGROUND, None, 0, shadow=True, border_radius=16)
    
    # Winner info
    if "Red Wins" in message:
        winner_color = RED
        winner_text = "You Win!"
        sub_text = "Congratulations! You defeated the AI!"
        if win_sound:
            win_sound.play()
    elif "Blue Wins" in message:
        winner_color = BLUE
        winner_text = "AI Wins!"
        sub_text = "Better luck next time!"
        if win_sound:
            win_sound.play()
    else:
        winner_color = TEXT_PRIMARY
        winner_text = message
        sub_text = "Game Over"
    
    # Winner text
    winner_surface = title_font.render(winner_text, True, winner_color)
    winner_rect = winner_surface.get_rect(center=(card_rect.centerx, card_rect.y + 80))
    screen.blit(winner_surface, winner_rect)
    
    # Sub text
    sub_surface = font.render(sub_text, True, TEXT_SECONDARY)
    sub_rect = sub_surface.get_rect(center=(card_rect.centerx, card_rect.y + 120))
    screen.blit(sub_surface, sub_rect)
    
    # Exit button
    button_rect = pygame.Rect(card_rect.centerx - 80, card_rect.y + 160, 160, 40)
    draw_card(screen, button_rect, DANGER_COLOR, None, 0, shadow=False, border_radius=8)
    
    button_text = font.render("Exit to Menu", True, WHITE)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)
    
    # Instructions
    instruction = small_font.render("Press ESC to exit to main menu", True, TEXT_SECONDARY)
    inst_rect = instruction.get_rect(center=(card_rect.centerx, card_rect.y + 220))
    screen.blit(instruction, inst_rect)
    
    pygame.display.flip()

def main():
    config = load_game_config()
    level = config.get("level", 1)
    
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    running = True
    waiting_for_ai = False
    selected_cell = None
    game_over = False
    first_move = True
    
    draw_board(board, level, selected_cell, waiting_for_ai)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEMOTION and not waiting_for_ai and not game_over:
                x, y = event.pos
                board_start_y = 120
                if y >= board_start_y:
                    c = (x - 50) // CELL_SIZE
                    r = (y - board_start_y) // CELL_SIZE
                    if 0 <= r < ROWS and 0 <= c < COLS and 50 <= x <= 50 + COLS * CELL_SIZE:
                        if is_valid_human_move(board, r, c):
                            selected_cell = (r, c)
                            draw_board(board, level, selected_cell, waiting_for_ai)
                        else:
                            if selected_cell:
                                selected_cell = None
                                draw_board(board, level, selected_cell, waiting_for_ai)

            if not waiting_for_ai and not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                board_start_y = 120
                if y >= board_start_y:
                    c = (x - 50) // CELL_SIZE
                    r = (y - board_start_y) // CELL_SIZE
                    if 0 <= r < ROWS and 0 <= c < COLS and 50 <= x <= 50 + COLS * CELL_SIZE:
                        if is_valid_human_move(board, r, c):
                            # Apply human move
                            apply_human_move(board, r, c)
                            if move_sound:
                                move_sound.play()
                            
                            # Process explosions after human move
                            explode(board, max_iterations=1000)
                            
                            # Check winner ONLY if not first move
                            if not first_move:
                                winner = check_winner(board)
                                if winner:
                                    if winner == 'R':
                                        show_game_over_message("Game Over: Red Wins")
                                    else:
                                        show_game_over_message("Game Over: Blue Wins")
                                    game_over = True
                                    return
                            else:
                                first_move = False
                            
                            selected_cell = None
                            waiting_for_ai = True
                            draw_board(board, level, selected_cell, waiting_for_ai)
                            write_human_move(FILENAME, board)

        if waiting_for_ai and not game_over:
            header, board_or_none = read_ai_move_or_gameover(FILENAME)
            if header is not None:
                show_game_over_message(header)
                game_over = True
                waiting_for_ai = False
            else:
                board = board_or_none
                if explosion_sound:
                    explosion_sound.play()
                waiting_for_ai = False
                draw_board(board, level, selected_cell, waiting_for_ai)

        pygame.time.delay(50)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()