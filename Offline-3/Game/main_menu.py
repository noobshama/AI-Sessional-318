import pygame
import sys
import subprocess
import os
import json
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 800
CELL_SIZE = 80

# Enhanced Modern Colors (removed icons)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (245, 245, 245)
GREEN = (46, 204, 113)
GOLD = (255, 215, 0)
PURPLE = (155, 89, 182)
ORANGE = (230, 126, 34)

# Gradient and modern colors
BACKGROUND_GRADIENT_TOP = (41, 128, 185)
BACKGROUND_GRADIENT_BOTTOM = (109, 213, 250)
CARD_BACKGROUND = (255, 255, 255)
ACCENT_PRIMARY = (52, 152, 219)
ACCENT_SECONDARY = (155, 89, 182)
TEXT_PRIMARY = (44, 62, 80)
TEXT_SECONDARY = (127, 140, 141)
SUCCESS_COLOR = (46, 204, 113)
WARNING_COLOR = (230, 126, 34)
DANGER_COLOR = (231, 76, 60)

# Level configurations (removed icons)
LEVEL_CONFIG = {
    1: {"name": "Beginner", "color": SUCCESS_COLOR, "description": "Simple orb counting"},
    2: {"name": "Easy", "color": ACCENT_PRIMARY, "description": "Considers critical mass"},
    3: {"name": "Medium", "color": WARNING_COLOR, "description": "Strategic positioning"},
    4: {"name": "Hard", "color": DANGER_COLOR, "description": "Conversion potential"},
    5: {"name": "Expert", "color": ACCENT_SECONDARY, "description": "Full AI capabilities"}
}

# Initialize display and fonts
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chain Reaction")

# Modern font setup
try:
    title_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
    subtitle_font = pygame.font.SysFont('Segoe UI', 24, bold=True)
    font = pygame.font.SysFont('Segoe UI', 20, bold=True)
    small_font = pygame.font.SysFont('Segoe UI', 16)
    tiny_font = pygame.font.SysFont('Segoe UI', 14)
except:
    title_font = pygame.font.SysFont('Arial', 48, bold=True)
    subtitle_font = pygame.font.SysFont('Arial', 24, bold=True)
    font = pygame.font.SysFont('Arial', 20, bold=True)
    small_font = pygame.font.SysFont('Arial', 16)
    tiny_font = pygame.font.SysFont('Arial', 14)

CONFIG_FILE = "game_config.json"

def draw_gradient_background(surface, color1, color2):
    """Draw a gradient background"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_card(surface, rect, color=CARD_BACKGROUND, border_color=None, border_width=0, shadow=True):
    """Draw a modern card with shadow effect"""
    if shadow:
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height))
        shadow_surface.set_alpha(30)
        shadow_surface.fill(BLACK)
        surface.blit(shadow_surface, shadow_rect)
    
    pygame.draw.rect(surface, color, rect, border_radius=12)
    
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=12)

def load_game_config():
    """Load game configuration"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"level": 1, "mode": "human_vs_ai"}

def save_game_config(config):
    """Save game configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return True
    except:
        return False

def show_mode_selection():
    """Show enhanced game mode selection screen"""
    config = load_game_config()
    selected_mode = 0  # 0 = Human vs AI, 1 = AI vs AI
    mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        draw_gradient_background(screen, BACKGROUND_GRADIENT_TOP, BACKGROUND_GRADIENT_BOTTOM)
        
        # Main title card
        title_card = pygame.Rect(WIDTH//2 - 350, 50, 700, 120)
        draw_card(screen, title_card, CARD_BACKGROUND, shadow=True)
        
        title_text = title_font.render("Chain Reaction", True, TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(WIDTH//2, 90))
        screen.blit(title_text, title_rect)
        
        subtitle_text = subtitle_font.render("AI Game Suite", True, ACCENT_PRIMARY)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, 125))
        screen.blit(subtitle_text, subtitle_rect)
        
        desc_text = small_font.render("Choose your game mode", True, TEXT_SECONDARY)
        desc_rect = desc_text.get_rect(center=(WIDTH//2, 150))
        screen.blit(desc_text, desc_rect)
        
        # Mode selection cards
        card_width, card_height = 320, 200
        spacing = 40
        start_x = WIDTH//2 - card_width - spacing//2
        start_y = 220
        
        modes = [
            {
                "name": "Human vs AI", 
                "desc": "", 
                "details": "",
                "color": ACCENT_PRIMARY
            },
            {
                "name": "AI vs AI", 
                "desc": "", 
                "details": "",
                "color": ACCENT_SECONDARY
            }
        ]
        
        mode_rects = []
        
        for i, mode in enumerate(modes):
            x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(x, start_y, card_width, card_height)
            mode_rects.append(card_rect)
            
            is_hovering = card_rect.collidepoint(mouse_pos)
            is_selected = i == selected_mode
            
            if is_selected:
                bg_color = mode["color"]
                text_color = WHITE
                border_color = mode["color"]
            elif is_hovering:
                bg_color = CARD_BACKGROUND
                text_color = mode["color"]
                border_color = mode["color"]
            else:
                bg_color = CARD_BACKGROUND
                text_color = TEXT_PRIMARY
                border_color = GRAY
            
            draw_card(screen, card_rect, bg_color, border_color, 3, shadow=True)
            
            # Mode name
            name_text = subtitle_font.render(mode["name"], True, text_color)
            name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.y + 80))
            screen.blit(name_text, name_rect)
            
            # Description
            desc_text = font.render(mode["desc"], True, text_color)
            desc_rect = desc_text.get_rect(center=(card_rect.centerx, card_rect.y + 120))
            screen.blit(desc_text, desc_rect)
            
            # Details
            details_text = small_font.render(mode["details"], True, text_color)
            details_rect = details_text.get_rect(center=(card_rect.centerx, card_rect.y + 150))
            screen.blit(details_text, details_rect)
        
        # Instructions card
        instruction_card = pygame.Rect(WIDTH//2 - 300, HEIGHT - 120, 600, 80)
        draw_card(screen, instruction_card, CARD_BACKGROUND, shadow=True)
        
        instruction_lines = [
            "Click to select mode • ENTER to confirm • ESC to exit",
            "Use arrow keys for keyboard navigation"
        ]
        
        for i, line in enumerate(instruction_lines):
            instruction_text = small_font.render(line, True, TEXT_SECONDARY)
            instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 95 + i * 20))
            screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    selected_mode = (selected_mode - 1) % 2
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                    selected_mode = (selected_mode + 1) % 2
                elif event.key == pygame.K_RETURN:
                    return selected_mode
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(mode_rects):
                    if rect.collidepoint(mouse_pos):
                        return i
        
        clock.tick(60)

def show_ai_battle_selection():
    """Show AI vs AI battle type selection"""
    selected_battle = 0  # 0 = Random vs Heuristic, 1 = Heuristic vs Heuristic
    mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        draw_gradient_background(screen, BACKGROUND_GRADIENT_TOP, BACKGROUND_GRADIENT_BOTTOM)
        
        # Title card
        title_card = pygame.Rect(WIDTH//2 - 350, 30, 700, 100)
        draw_card(screen, title_card, CARD_BACKGROUND, shadow=True)
        
        title_text = subtitle_font.render("AI vs AI Battle Mode", True, TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(WIDTH//2, 60))
        screen.blit(title_text, title_rect)
        
        subtitle_text = small_font.render("Choose battle type", True, TEXT_SECONDARY)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, 90))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Battle type cards
        card_width, card_height = 380, 240
        spacing = 40
        start_x = WIDTH//2 - card_width - spacing//2
        start_y = 180
        
        battles = [
            {
                "name": "Random vs Heuristic", 
                "desc": "Random AI vs Smart AI", 
                "details": "",
                "extra": "",
                "color": ACCENT_PRIMARY
            },
            {
                "name": "Heuristic vs Heuristic", 
                "desc": "Smart AI vs Smart AI", 
                "details": "",
                "extra": "",
                "color": ACCENT_SECONDARY
            }
        ]
        
        battle_rects = []
        
        for i, battle in enumerate(battles):
            x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(x, start_y, card_width, card_height)
            battle_rects.append(card_rect)
            
            is_hovering = card_rect.collidepoint(mouse_pos)
            is_selected = i == selected_battle
            
            if is_selected:
                bg_color = battle["color"]
                text_color = WHITE
                border_color = battle["color"]
            elif is_hovering:
                bg_color = CARD_BACKGROUND
                text_color = battle["color"]
                border_color = battle["color"]
            else:
                bg_color = CARD_BACKGROUND
                text_color = TEXT_PRIMARY
                border_color = GRAY
            
            draw_card(screen, card_rect, bg_color, border_color, 3, shadow=True)
            
            # Battle name
            name_text = font.render(battle["name"], True, text_color)
            name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.y + 60))
            screen.blit(name_text, name_rect)
            
            # Description
            desc_text = small_font.render(battle["desc"], True, text_color)
            desc_rect = desc_text.get_rect(center=(card_rect.centerx, card_rect.y + 100))
            screen.blit(desc_text, desc_rect)
            
            # Details
            details_text = small_font.render(battle["details"], True, text_color)
            details_rect = details_text.get_rect(center=(card_rect.centerx, card_rect.y + 130))
            screen.blit(details_text, details_rect)
            
            # Extra info
            extra_text = tiny_font.render(battle["extra"], True, text_color)
            extra_rect = extra_text.get_rect(center=(card_rect.centerx, card_rect.y + 160))
            screen.blit(extra_text, extra_rect)
        
        # Instructions
        instruction_card = pygame.Rect(WIDTH//2 - 300, HEIGHT - 120, 600, 80)
        draw_card(screen, instruction_card, CARD_BACKGROUND, shadow=True)
        
        instruction_lines = [
            "Click to select battle type • ENTER to confirm • ESC to go back",
            "Arrow keys for navigation"
        ]
        
        for i, line in enumerate(instruction_lines):
            instruction_text = small_font.render(line, True, TEXT_SECONDARY)
            instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 95 + i * 20))
            screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Go back
                elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    selected_battle = (selected_battle - 1) % 2
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                    selected_battle = (selected_battle + 1) % 2
                elif event.key == pygame.K_RETURN:
                    return selected_battle
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(battle_rects):
                    if rect.collidepoint(mouse_pos):
                        return i
        
        clock.tick(60)

def show_dual_level_selection():
    """Show level selection for both AIs in heuristic vs heuristic mode"""
    config = load_game_config()
    ai1_level = config.get("ai1_level", 3)
    ai2_level = config.get("ai2_level", 5)
    selected_ai = 0  # 0 = AI1, 1 = AI2
    mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        draw_gradient_background(screen, BACKGROUND_GRADIENT_TOP, BACKGROUND_GRADIENT_BOTTOM)
        
        # Title
        title_card = pygame.Rect(WIDTH//2 - 400, 20, 800, 80)
        draw_card(screen, title_card, CARD_BACKGROUND, shadow=True)
        
        title_text = subtitle_font.render("Heuristic vs Heuristic Configuration", True, TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(WIDTH//2, 60))
        screen.blit(title_text, title_rect)
        
        # AI configuration panels
        panel_width = 380
        panel_height = 420
        spacing = 40
        start_x = WIDTH//2 - panel_width - spacing//2
        start_y = 130
        
        ai_configs = [
            {"name": "AI Player 1 (Red)", "level": ai1_level, "color": RED},
            {"name": "AI Player 2 (Blue)", "level": ai2_level, "color": BLUE}
        ]
        
        # Store button rects for click detection
        if not hasattr(show_dual_level_selection, 'button_rects'):
            show_dual_level_selection.button_rects = {}
        
        for ai_idx, ai_config in enumerate(ai_configs):
            x = start_x + ai_idx * (panel_width + spacing)
            panel_rect = pygame.Rect(x, start_y, panel_width, panel_height)
            
            is_selected = ai_idx == selected_ai
            border_color = ai_config["color"] if is_selected else GRAY
            border_width = 3 if is_selected else 1
            
            draw_card(screen, panel_rect, CARD_BACKGROUND, border_color, border_width, shadow=True)
            
            # AI name
            name_text = font.render(ai_config["name"], True, ai_config["color"])
            name_rect = name_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 30))
            screen.blit(name_text, name_rect)
            
            # Current level display
            current_level_info = LEVEL_CONFIG[ai_config["level"]]
            current_text = small_font.render(f"Current: Level {ai_config['level']} - {current_level_info['name']}", True, current_level_info["color"])
            current_rect = current_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 60))
            screen.blit(current_text, current_rect)
            
            # Level buttons
            button_width = 60
            button_height = 50
            button_spacing = 8
            buttons_start_x = panel_rect.centerx - (5 * button_width + 4 * button_spacing) // 2
            buttons_y = panel_rect.y + 100
            
            for level in range(1, 6):
                button_x = buttons_start_x + (level - 1) * (button_width + button_spacing)
                button_rect = pygame.Rect(button_x, buttons_y, button_width, button_height)
                
                level_info = LEVEL_CONFIG[level]
                is_current = level == ai_config["level"]
                is_hovering = button_rect.collidepoint(mouse_pos) and is_selected
                
                if is_current:
                    button_color = level_info["color"]
                    text_color = WHITE
                elif is_hovering:
                    button_color = LIGHT_GRAY
                    text_color = level_info["color"]
                else:
                    button_color = WHITE
                    text_color = TEXT_PRIMARY
                
                draw_card(screen, button_rect, button_color, level_info["color"], 2 if is_current else 1, shadow=False)
                
                level_text = small_font.render(str(level), True, text_color)
                level_text_rect = level_text.get_rect(center=(button_rect.centerx, button_rect.centery - 8))
                screen.blit(level_text, level_text_rect)
                
                name_text = tiny_font.render(level_info["name"][:4], True, text_color)
                name_text_rect = name_text.get_rect(center=(button_rect.centerx, button_rect.centery + 8))
                screen.blit(name_text, name_text_rect)
                
                # Store button rect for click detection
                show_dual_level_selection.button_rects[(ai_idx, level)] = button_rect
            
            # Level description
            desc_y = buttons_y + 80
            desc_text = tiny_font.render(current_level_info["description"], True, TEXT_SECONDARY)
            desc_rect = desc_text.get_rect(center=(panel_rect.centerx, desc_y))
            screen.blit(desc_text, desc_rect)
            
            # AI strategy info
            strategy_y = desc_y + 40
            strategy_lines = [
                f"Search Depth: {ai_config['level']}",
                f"Heuristics: {len(LEVEL_CONFIG[ai_config['level']].get('heuristics', []))}",
                f"Strength: {['Very Easy', 'Easy', 'Medium', 'Hard', 'Expert'][ai_config['level']-1]}"
            ]
            
            for i, line in enumerate(strategy_lines):
                strategy_text = tiny_font.render(line, True, TEXT_SECONDARY)
                strategy_rect = strategy_text.get_rect(center=(panel_rect.centerx, strategy_y + i * 20))
                screen.blit(strategy_text, strategy_rect)
        
        # Start battle button
        start_button = pygame.Rect(WIDTH//2 - 100, start_y + panel_height + 40, 200, 50)
        start_hovering = start_button.collidepoint(mouse_pos)
        start_color = SUCCESS_COLOR if start_hovering else CARD_BACKGROUND
        start_text_color = WHITE if start_hovering else SUCCESS_COLOR
        
        draw_card(screen, start_button, start_color, SUCCESS_COLOR, 2, shadow=True)
        start_text = font.render("Start Battle", True, start_text_color)
        start_text_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_text_rect)
        
        # Instructions
        instruction_card = pygame.Rect(WIDTH//2 - 350, HEIGHT - 100, 700, 70)
        draw_card(screen, instruction_card, CARD_BACKGROUND, shadow=True)
        
        instruction_lines = [
            "TAB to switch AI • Click level buttons to change • ENTER to start • ESC to go back",
            f"Battle: Level {ai1_level} vs Level {ai2_level}"
        ]
        
        for i, line in enumerate(instruction_lines):
            color = TEXT_SECONDARY if i == 0 else TEXT_PRIMARY
            instruction_text = small_font.render(line, True, color)
            instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 75 + i * 20))
            screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None  # Go back
                elif event.key == pygame.K_TAB:
                    selected_ai = (selected_ai + 1) % 2
                elif event.key == pygame.K_RETURN:
                    return ai1_level, ai2_level
                elif event.key >= pygame.K_1 and event.key <= pygame.K_5:
                    level = event.key - pygame.K_0
                    if selected_ai == 0:
                        ai1_level = level
                    else:
                        ai2_level = level
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check start button
                if start_button.collidepoint(mouse_pos):
                    return ai1_level, ai2_level
                
                # Check level buttons
                for (ai_idx, level), button_rect in show_dual_level_selection.button_rects.items():
                    if button_rect.collidepoint(mouse_pos):
                        if ai_idx == 0:
                            ai1_level = level
                        else:
                            ai2_level = level
                        break
        
        clock.tick(60)

def show_level_selection(title_text="Select AI Difficulty Level"):
    """Show enhanced level selection screen (existing function, icons removed)"""
    config = load_game_config()
    current_level = config.get("level", 1)
    selected_level = current_level
    mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        draw_gradient_background(screen, BACKGROUND_GRADIENT_TOP, BACKGROUND_GRADIENT_BOTTOM)
        
        # Title card
        title_card = pygame.Rect(WIDTH//2 - 350, 30, 700, 80)
        draw_card(screen, title_card, CARD_BACKGROUND, shadow=True)
        
        title = subtitle_font.render(title_text, True, TEXT_PRIMARY)
        title_rect = title.get_rect(center=(WIDTH//2, 70))
        screen.blit(title, title_rect)
        
        # Level cards
        card_width, card_height = 140, 160
        spacing = 15
        total_width = 5 * card_width + 4 * spacing
        start_x = WIDTH//2 - total_width//2
        start_y = 150
        
        level_rects = []
        
        for level in range(1, 6):
            level_info = LEVEL_CONFIG[level]
            x = start_x + (level - 1) * (card_width + spacing)
            card_rect = pygame.Rect(x, start_y, card_width, card_height)
            level_rects.append(card_rect)
            
            is_hovering = card_rect.collidepoint(mouse_pos)
            is_selected = level == selected_level
            is_current = level == current_level
            
            if is_selected:
                bg_color = level_info["color"]
                text_color = WHITE
                border_color = level_info["color"]
                border_width = 4
            elif is_hovering:
                bg_color = CARD_BACKGROUND
                text_color = level_info["color"]
                border_color = level_info["color"]
                border_width = 3
            else:
                bg_color = CARD_BACKGROUND
                text_color = TEXT_PRIMARY
                border_color = GRAY if not is_current else level_info["color"]
                border_width = 1 if not is_current else 2
            
            draw_card(screen, card_rect, bg_color, border_color, border_width, shadow=True)
            
            # Current level indicator
            if is_current and not is_selected:
                current_indicator = pygame.Rect(card_rect.right - 25, card_rect.top + 5, 20, 20)
                pygame.draw.circle(screen, SUCCESS_COLOR, current_indicator.center, 8)
                check_text = tiny_font.render("✓", True, WHITE)
                check_rect = check_text.get_rect(center=current_indicator.center)
                screen.blit(check_text, check_rect)
            
            # Level number
            level_text = font.render(f"Level {level}", True, text_color)
            level_rect = level_text.get_rect(center=(card_rect.centerx, card_rect.y + 40))
            screen.blit(level_text, level_rect)
            
            # Level name
            name_text = small_font.render(level_info["name"], True, text_color)
            name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.y + 70))
            screen.blit(name_text, name_rect)
            
            # Description (wrapped)
            desc_words = level_info["description"].split()
            lines = []
            current_line = []
            for word in desc_words:
                test_line = " ".join(current_line + [word])
                if tiny_font.size(test_line)[0] < card_width - 10:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
            
            for i, line in enumerate(lines[:2]):
                desc_text = tiny_font.render(line, True, text_color)
                desc_rect = desc_text.get_rect(center=(card_rect.centerx, card_rect.y + 100 + i * 15))
                screen.blit(desc_text, desc_rect)
        
        # Current selection info
        if selected_level:
            info_card = pygame.Rect(WIDTH//2 - 200, 340, 400, 80)
            draw_card(screen, info_card, CARD_BACKGROUND, LEVEL_CONFIG[selected_level]["color"], 2, shadow=True)
            
            selected_info = LEVEL_CONFIG[selected_level]
            info_title = font.render(f'{selected_info["name"]}', True, selected_info["color"])
            info_title_rect = info_title.get_rect(center=(WIDTH//2, 360))
            screen.blit(info_title, info_title_rect)
            
            info_desc = small_font.render(selected_info["description"], True, TEXT_SECONDARY)
            info_desc_rect = info_desc.get_rect(center=(WIDTH//2, 385))
            screen.blit(info_desc, info_desc_rect)
            
            difficulty_labels = ["Very Easy", "Easy", "Medium", "Hard", "Very Hard"]
            difficulty_text = small_font.render(f"Difficulty: {difficulty_labels[selected_level-1]}", True, TEXT_SECONDARY)
            difficulty_rect = difficulty_text.get_rect(center=(WIDTH//2, 405))
            screen.blit(difficulty_text, difficulty_rect)
        
        # Instructions card
        instruction_card = pygame.Rect(WIDTH//2 - 300, HEIGHT - 120, 600, 80)
        draw_card(screen, instruction_card, CARD_BACKGROUND, shadow=True)
        
        instruction_lines = [
            "Click to select level • SPACE to confirm • ESC to go back",
            f"Current level: {current_level} ({LEVEL_CONFIG[current_level]['name']})"
        ]
        
        for i, line in enumerate(instruction_lines):
            color = TEXT_SECONDARY if i == 0 else LEVEL_CONFIG[current_level]["color"]
            instruction_text = small_font.render(line, True, color)
            instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 95 + i * 20))
            screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_SPACE:
                    return selected_level
                elif event.key == pygame.K_LEFT:
                    selected_level = max(1, selected_level - 1)
                elif event.key == pygame.K_RIGHT:
                    selected_level = min(5, selected_level + 1)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for level, rect in enumerate(level_rects, 1):
                    if rect.collidepoint(mouse_pos):
                        selected_level = level
                        break
        
        clock.tick(60)

def main():
    """Main function to handle mode selection and launch appropriate game"""
    while True:
        # Show mode selection
        selected_mode = show_mode_selection()
        
        if selected_mode == 0:  # Human vs AI
            # Show level selection for AI
            level = show_level_selection("Select AI Difficulty Level")
            if level is None:
                continue
            
            # Save config and launch human vs AI game
            config = {"level": level, "mode": "human_vs_ai"}
            save_game_config(config)
            
            # Clear any existing game state
            if os.path.exists("gamestate.txt"):
                os.remove("gamestate.txt")
            
            # Launch both AI and human interfaces
            try:
                ai_process = subprocess.Popen([sys.executable, "ai_player.py"])
                human_process = subprocess.Popen([sys.executable, "human_player.py"])
                human_process.wait()
                ai_process.terminate()
            except Exception as e:
                print(f"Error launching game: {e}")
                
        elif selected_mode == 1:  # AI vs AI
            # Show AI battle type selection
            battle_type = show_ai_battle_selection()
            if battle_type is None:
                continue
            
            if battle_type == 0:  # Random vs Heuristic
                # Show level selection for smart AI
                level = show_level_selection("Select Smart AI Difficulty Level")
                if level is None:
                    continue
                
                # Save config and launch Random vs Heuristic
                config = {"level": level, "mode": "ai_vs_ai", "battle_type": "random_vs_heuristic"}
                save_game_config(config)
                
                # Clear any existing game state
                if os.path.exists("gamestate.txt"):
                    os.remove("gamestate.txt")
                
                print(f"Starting Random vs Heuristic - Smart AI Level {level} vs Random AI")
                
                try:
                    # Start Random AI process first
                    print("Starting Random AI...")
                    random_ai_process = subprocess.Popen([sys.executable, "random_ai_player.py"])
                    time.sleep(0.5)
                    
                    # Start Smart AI process
                    print("Starting Smart AI...")
                    smart_ai_process = subprocess.Popen([sys.executable, "smart_ai_player.py"])
                    time.sleep(0.5)
                    
                    # Start AI viewer interface
                    print("Starting AI vs AI viewer...")
                    viewer_process = subprocess.Popen([sys.executable, "ai_vs_ai_viewer.py"])
                    
                    viewer_process.wait()
                    
                    # Clean up
                    try:
                        smart_ai_process.terminate()
                        random_ai_process.terminate()
                    except:
                        pass
                    
                    print("Random vs Heuristic match ended")
                    
                except Exception as e:
                    print(f"Error launching Random vs Heuristic: {e}")
                    try:
                        if 'smart_ai_process' in locals():
                            smart_ai_process.terminate()
                        if 'random_ai_process' in locals():
                            random_ai_process.terminate()
                        if 'viewer_process' in locals():
                            viewer_process.terminate()
                    except:
                        pass
            
            elif battle_type == 1:  # Heuristic vs Heuristic
                # Show dual level selection
                ai1_level, ai2_level = show_dual_level_selection()
                if ai1_level is None or ai2_level is None:
                    continue
                
                # Save config and launch Heuristic vs Heuristic
                config = {
                    "ai1_level": ai1_level, 
                    "ai2_level": ai2_level, 
                    "mode": "ai_vs_ai", 
                    "battle_type": "heuristic_vs_heuristic"
                }
                save_game_config(config)
                
                # Clear any existing game state
                if os.path.exists("gamestate.txt"):
                    os.remove("gamestate.txt")
                
                print(f"Starting Heuristic vs Heuristic - AI Level {ai1_level} vs AI Level {ai2_level}")
                
                try:
                    # Start AI1 process first (Red player)
                    print(f"Starting AI1 (Level {ai1_level})...")
                    ai1_process = subprocess.Popen([sys.executable, "heuristic_ai1_player.py"])
                    time.sleep(0.5)
                    
                    # Start AI2 process (Blue player)
                    print(f"Starting AI2 (Level {ai2_level})...")
                    ai2_process = subprocess.Popen([sys.executable, "heuristic_ai2_player.py"])
                    time.sleep(0.5)
                    
                    # Start enhanced AI viewer interface
                    print("Starting Heuristic vs Heuristic viewer...")
                    viewer_process = subprocess.Popen([sys.executable, "heuristic_vs_heuristic_viewer.py"])
                    
                    viewer_process.wait()
                    
                    # Clean up
                    try:
                        ai1_process.terminate()
                        ai2_process.terminate()
                    except:
                        pass
                    
                    print("Heuristic vs Heuristic match ended")
                    
                except Exception as e:
                    print(f"Error launching Heuristic vs Heuristic: {e}")
                    try:
                        if 'ai1_process' in locals():
                            ai1_process.terminate()
                        if 'ai2_process' in locals():
                            ai2_process.terminate()
                        if 'viewer_process' in locals():
                            viewer_process.terminate()
                    except:
                        pass

if __name__ == "__main__":
    main()