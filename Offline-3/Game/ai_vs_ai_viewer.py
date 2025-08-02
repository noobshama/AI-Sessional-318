import pygame
import os
import time
import sys
import json

ROWS, COLS = 9, 6
FILENAME = "gamestate.txt"
CONFIG_FILE = "game_config.json"
CELL_SIZE = 70  # Adjusted for better fit
WIDTH, HEIGHT = COLS * CELL_SIZE + 100, ROWS * CELL_SIZE + 250  # More space for enhanced UI

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

# Level configurations
LEVEL_CONFIG = {
    1: {"name": "Beginner", "color": SUCCESS_COLOR, "description": "Simple orb counting"},
    2: {"name": "Easy", "color": ACCENT_PRIMARY, "description": "Considers critical mass"},
    3: {"name": "Medium", "color": WARNING_COLOR, "description": "Strategic positioning"},
    4: {"name": "Hard", "color": DANGER_COLOR, "description": "Conversion potential"},
    5: {"name": "Expert", "color": ACCENT_SECONDARY, "description": "Full AI capabilities"}
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chain Reaction - AI Battle")

# Enhanced font setup
try:
    title_font = pygame.font.SysFont('Segoe UI', 32, bold=True)
    font = pygame.font.SysFont('Segoe UI', 18, bold=True)
    large_font = pygame.font.SysFont('Segoe UI', 28, bold=True)
    small_font = pygame.font.SysFont('Segoe UI', 14)
    tiny_font = pygame.font.SysFont('Segoe UI', 12)
except:
    title_font = pygame.font.SysFont('Arial', 32, bold=True)
    font = pygame.font.SysFont('Arial', 18, bold=True)
    large_font = pygame.font.SysFont('Arial', 28, bold=True)
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
    """Load game configuration"""
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

def read_game_state():
    """Read current game state from file"""
    try:
        if not os.path.exists(FILENAME):
            return None, None
        
        with open(FILENAME, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < ROWS + 1:
            return None, None
        
        header = lines[0].strip()
        board = parse_board(lines[1:1+ROWS])
        return header, board
    except:
        return None, None

def get_critical_mass(r, c):
    """Calculate critical mass based on position"""
    if (r == 0 or r == ROWS-1) and (c == 0 or c == COLS-1):
        return 2  # Corner
    elif r == 0 or r == ROWS-1 or c == 0 or c == COLS-1:
        return 3  # Edge
    else:
        return 4  # Interior

def draw_orbs_in_cell(surface, center_x, center_y, count, color, cell_size):
    """Draw enhanced individual orbs based on count"""
    orb_color = RED if color == 'R' else BLUE
    orb_light_color = RED_GRADIENT_START if color == 'R' else BLUE_GRADIENT_START
    orb_radius = min(10, cell_size // 9)
    
    if count == 1:
        # Single orb with gradient effect
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
            # Modern number display
            text = small_font.render(str(count), True, TEXT_PRIMARY)
            text_rect = text.get_rect(center=(center_x, center_y))
            
            # Background circle
            bg_radius = max(text_rect.width, text_rect.height) // 2 + 6
            pygame.draw.circle(surface, WHITE, (center_x, center_y), bg_radius + 2)
            pygame.draw.circle(surface, orb_color, (center_x, center_y), bg_radius + 1, 2)
            pygame.draw.circle(surface, WHITE, (center_x, center_y), bg_radius)
            
            surface.blit(text, text_rect)

def draw_board(board, level, current_player="", move_count=0, paused=False):
    # Background
    screen.fill(BACKGROUND)
    
    # Header section
    header_height = 130
    header_rect = pygame.Rect(0, 0, WIDTH, header_height)
    draw_gradient_rect(screen, header_rect, DARK_GRAY, (70, 90, 110))
    
    # Title
    title_text = title_font.render("AI Battle", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH//2, 20))
    screen.blit(title_text, title_rect)
    
    # Player cards with better spacing
    card_width = 140
    card_height = 50
    card_y = 50
    
    # Random AI card (left)
    red_card = pygame.Rect(15, card_y, card_width, card_height)
    red_active = "Random" in current_player
    red_color = RED if red_active else CARD_BACKGROUND
    red_text_color = WHITE if red_active else RED
    draw_card(screen, red_card, red_color, RED, 2 if red_active else 1, shadow=True)
    
    # AI info
    red_title = small_font.render(" Random AI", True, red_text_color)
    red_title_rect = red_title.get_rect(center=(red_card.centerx, red_card.centery - 8))
    screen.blit(red_title, red_title_rect)
    
    if board:
        red_orbs = sum(cell[0] for row in board for cell in row if cell and cell[1] == 'R')
        red_count = tiny_font.render(f"{red_orbs} orbs", True, red_text_color)
        red_count_rect = red_count.get_rect(center=(red_card.centerx, red_card.centery + 12))
        screen.blit(red_count, red_count_rect)
    
    # Smart AI card (right)
    blue_card = pygame.Rect(WIDTH - card_width - 15, card_y, card_width, card_height)
    blue_active = "Smart" in current_player
    blue_color = BLUE if blue_active else CARD_BACKGROUND
    blue_text_color = WHITE if blue_active else BLUE
    draw_card(screen, blue_card, blue_color, BLUE, 2 if blue_active else 1, shadow=True)
    
    level_info = LEVEL_CONFIG[level]
    blue_title = small_font.render(" Smart AI", True, blue_text_color)
    blue_title_rect = blue_title.get_rect(center=(blue_card.centerx, blue_card.centery - 8))
    screen.blit(blue_title, blue_title_rect)
    
    if board:
        blue_orbs = sum(cell[0] for row in board for cell in row if cell and cell[1] == 'B')
        blue_count = tiny_font.render(f"{blue_orbs} orbs", True, blue_text_color)
        blue_count_rect = blue_count.get_rect(center=(blue_card.centerx, blue_card.centery + 12))
        screen.blit(blue_count, blue_count_rect)
    
    # Center info card with better positioning
    center_width = WIDTH - (card_width * 2) - 60  # Space between left and right cards
    center_x = red_card.right + 15
    center_card = pygame.Rect(center_x, card_y, center_width, card_height)
    draw_card(screen, center_card, CARD_BACKGROUND, GRAY, 1, shadow=True)
    
    # Game status
    if paused:
        status_text = small_font.render(" PAUSED", True, WARNING_COLOR)
    else:
        status_text = small_font.render(f"Move {move_count}", True, TEXT_PRIMARY)
    status_rect = status_text.get_rect(center=(center_card.centerx, center_card.centery - 10))
    screen.blit(status_text, status_rect)
    
    # AI level info
    level_text = small_font.render(f"Level {level}: {level_info['name']}", True, level_info['color'])
    level_rect = level_text.get_rect(center=(center_card.centerx, center_card.centery + 12))
    screen.blit(level_text, level_rect)
    
    # Game board
    board_start_y = header_height + 20
    board_rect = pygame.Rect(50, board_start_y, COLS * CELL_SIZE, ROWS * CELL_SIZE)
    draw_card(screen, board_rect, WHITE, GRAY, 2, shadow=True, border_radius=12)
    
    if board:
        for r in range(ROWS):
            for c in range(COLS):
                x = 50 + c * CELL_SIZE
                y = board_start_y + r * CELL_SIZE
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                # Cell background with subtle gradient
                if (r + c) % 2 == 0:
                    cell_color = (250, 250, 250)
                else:
                    cell_color = (245, 245, 245)
                
                pygame.draw.rect(screen, cell_color, cell_rect)
                pygame.draw.rect(screen, (220, 220, 220), cell_rect, 1)
                
                # Critical mass indicators
                critical_mass = get_critical_mass(r, c)
                dot_color = (200, 200, 200)
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
                    
                    # Glow effect for critical cells
                    if count >= critical_mass:
                        glow_color = GOLD
                        for i in range(3):
                            pygame.draw.circle(screen, glow_color, (center_x, center_y), 
                                             CELL_SIZE // 2 - 8 + i, 1)
                    
                    draw_orbs_in_cell(screen, center_x, center_y, count, color, CELL_SIZE)
    
    # Control panel
    control_panel_y = board_start_y + ROWS * CELL_SIZE + 30
    control_rect = pygame.Rect(20, control_panel_y, WIDTH - 40, 60)
    draw_card(screen, control_rect, CARD_BACKGROUND, GRAY, 1, shadow=True)
    
    # Controls
    controls = [
        ("SPACE", "Pause/Resume", WARNING_COLOR),
        ("ESC", "Exit to Menu", DANGER_COLOR)
    ]
    
    control_x = 40
    for key, action, color in controls:
        # Key button
        key_rect = pygame.Rect(control_x, control_panel_y + 15, 60, 30)
        draw_card(screen, key_rect, color, None, 0, shadow=False, border_radius=6)
        
        key_text = small_font.render(key, True, WHITE)
        key_text_rect = key_text.get_rect(center=key_rect.center)
        screen.blit(key_text, key_text_rect)
        
        # Action text
        action_text = small_font.render(action, True, TEXT_SECONDARY)
        action_rect = action_text.get_rect(midleft=(key_rect.right + 10, key_rect.centery))
        screen.blit(action_text, action_rect)
        
        control_x += 150
    
    pygame.display.flip()

def show_game_over_message(message, level):
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Main message
    if "Red Wins" in message:
        text_color = RED
        winner_text = "Random AI Wins!"
        if win_sound:
            win_sound.play()
    elif "Blue Wins" in message:
        text_color = BLUE
        winner_text = "Smart AI Wins!"
        if win_sound:
            win_sound.play()
    else:
        text_color = WHITE
        winner_text = message
    
    text = large_font.render(winner_text, True, text_color)
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    
    # Add background for text
    bg_rect = rect.inflate(40, 20)
    pygame.draw.rect(screen, WHITE, bg_rect)
    pygame.draw.rect(screen, BLACK, bg_rect, 3)
    
    screen.blit(text, rect)
    
    # Show level info
    level_info = LEVEL_CONFIG[level]
    level_text = font.render(f"Smart AI was Level {level} ({level_info['name']})", True, WHITE)
    level_rect = level_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 10))
    screen.blit(level_text, level_rect)
    
    # Add instruction
    instruction = font.render("Press ESC to exit to main menu", True, WHITE)
    inst_rect = instruction.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
    screen.blit(instruction, inst_rect)
    
    pygame.display.flip()

def main():
    config = load_game_config()
    level = config.get("level", 1)
    
    board = None
    last_header = ""
    running = True
    game_over = False
    paused = False
    move_count = 0
    current_player = "Random AI"
    
    print(f"AI vs AI - Smart AI Level {level} vs Random AI")
    
    draw_board(board, level, current_player, move_count)
    
    clock = pygame.time.Clock()
    last_check_time = time.time()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print("Game paused" if paused else "Game resumed")
        
        # Check for game state updates more frequently
        current_time = time.time()
        if not paused and not game_over and (current_time - last_check_time > 0.1):  # Check every 100ms
            last_check_time = current_time
            
            # Read game state
            header, new_board = read_game_state()
            
            if header and header != last_header:
                last_header = header
                print(f"Game state update: {header}")
                
                if header.startswith("Game Over:"):
                    game_over = True
                    board = new_board
                    show_game_over_message(header, level)
                elif new_board:
                    board = new_board
                    move_count += 1
                    
                    # Determine current player based on header
                    if "Random AI Move:" in header:
                        current_player = "Smart AI's Turn"
                        if move_sound:
                            move_sound.play()
                    elif "Smart AI Move:" in header:
                        current_player = "Random AI's Turn"
                        if explosion_sound:
                            explosion_sound.play()
                    
                    draw_board(board, level, current_player, move_count)
        
        clock.tick(60)  # 60 FPS for smooth display
    
    print("AI vs AI  closing")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()