import time
import os
import copy
import json
import random

ROWS, COLS = 9, 6
FILENAME = "gamestate.txt"
CONFIG_FILE = "game_config.json"

# Level configurations - optimized for speed
LEVEL_CONFIG = {
    1: {"name": "Beginner", "depth": 1, "heuristics": ["orb_count"]},
    2: {"name": "Easy", "depth": 2, "heuristics": ["orb_count", "critical_mass"]},
    3: {"name": "Medium", "depth": 2, "heuristics": ["orb_count", "critical_mass", "strategic_position"]},
    4: {"name": "Hard", "depth": 2, "heuristics": ["orb_count", "critical_mass", "strategic_position", "conversion_potential"]},
    5: {"name": "Expert", "depth": 3, "heuristics": ["orb_count", "critical_mass", "strategic_position", "conversion_potential", "mobility"]}
}

# Pre-calculate critical masses and neighbors for efficiency
CRITICAL_MASS = {}
NEIGHBORS = {}
POSITION_WEIGHTS = {}

for r in range(ROWS):
    for c in range(COLS):
        # Critical mass
        if (r in [0, ROWS-1]) and (c in [0, COLS-1]):
            CRITICAL_MASS[(r, c)] = 2  # Corner
            POSITION_WEIGHTS[(r, c)] = 3
        elif r in [0, ROWS-1] or c in [0, COLS-1]:
            CRITICAL_MASS[(r, c)] = 3  # Edge
            POSITION_WEIGHTS[(r, c)] = 2
        else:
            CRITICAL_MASS[(r, c)] = 4  # Interior
            POSITION_WEIGHTS[(r, c)] = 1
        
        # Neighbors
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                neighbors.append((nr, nc))
        NEIGHBORS[(r, c)] = neighbors

def load_game_config():
    """Load game configuration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"level": 1}

def save_game_config(config):
    """Save game configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except:
        pass

def parse_board(lines):
    """Parse board from text lines"""
    board = []
    for line in lines:
        row = []
        for p in line.strip().split():
            if p == '0':
                row.append(None)
            else:
                row.append((int(p[:-1]), p[-1]))
        board.append(row)
    return board

def board_to_lines(board):
    """Convert board to text lines"""
    lines = []
    for row in board:
        line = []
        for cell in row:
            line.append('0' if cell is None else f"{cell[0]}{cell[1]}")
        lines.append(' '.join(line))
    return lines

def write_gamestate(filename, header, board):
    """Write game state to file"""
    try:
        lines = [header] + board_to_lines(board)
        with open(filename, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

def read_gamestate(filename, expected_header):
    """Read game state from file"""
    try:
        if not os.path.exists(filename):
            return None
            
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        if len(lines) < ROWS + 1 or lines[0].strip() != expected_header:
            return None
            
        return parse_board(lines[1:1+ROWS])
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def explode(board, max_iterations=1000):
    """Handle chain reactions with maximum iteration limit only"""
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

def get_valid_moves(board, player_color):
    """Get all valid moves for a player - optimized"""
    moves = []
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if cell is None or cell[1] == player_color:
                moves.append((r, c))
    return moves

def apply_move(board, r, c, color):
    """Apply a move to the board"""
    current = board[r][c]
    board[r][c] = (1, color) if current is None else (current[0] + 1, color)

def quick_evaluate(board):
    """Fast evaluation function for quick decisions"""
    blue_score = red_score = 0
    
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if cell:
                count, color = cell
                position_bonus = POSITION_WEIGHTS[(r, c)] * 0.3
                critical_bonus = (count / CRITICAL_MASS[(r, c)]) * 0.5
                
                total_value = count + position_bonus + critical_bonus
                
                if color == 'B':
                    blue_score += total_value
                else:
                    red_score += total_value
    
    return blue_score - red_score

def evaluate_board(board, level):
    """Evaluate board position based on difficulty level - optimized"""
    if level <= 2:
        return quick_evaluate(board)
    
    config = LEVEL_CONFIG[level]
    heuristics = config["heuristics"]
    
    # Pre-calculate color counts and positions
    blue_data = {"orbs": 0, "cells": []}
    red_data = {"orbs": 0, "cells": []}
    
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if cell:
                count, color = cell
                data = blue_data if color == 'B' else red_data
                data["orbs"] += count
                data["cells"].append((r, c, count))
    
    score = 0
    
    # Simple orb count (always included)
    score += (blue_data["orbs"] - red_data["orbs"]) * 1.0
    
    # Only compute expensive heuristics for higher levels
    if level >= 3:
        # Critical mass proximity
        if "critical_mass" in heuristics:
            for r, c, count in blue_data["cells"]:
                score += (count / CRITICAL_MASS[(r, c)]) * 1.5
            for r, c, count in red_data["cells"]:
                score -= (count / CRITICAL_MASS[(r, c)]) * 1.5
        
        # Strategic positions (use pre-calculated weights)
        if "strategic_position" in heuristics:
            for r, c, count in blue_data["cells"]:
                score += count * POSITION_WEIGHTS[(r, c)] * 0.4
            for r, c, count in red_data["cells"]:
                score -= count * POSITION_WEIGHTS[(r, c)] * 0.4
    
    # Only for highest levels
    if level >= 4:
        if "conversion_potential" in heuristics:
            for r, c, count in blue_data["cells"]:
                if count >= CRITICAL_MASS[(r, c)] - 1:
                    conversion = sum(board[nr][nc][0] if board[nr][nc] and board[nr][nc][1] != 'B' else 0
                                   for nr, nc in NEIGHBORS[(r, c)])
                    score += conversion * 1.0
            
            for r, c, count in red_data["cells"]:
                if count >= CRITICAL_MASS[(r, c)] - 1:
                    conversion = sum(board[nr][nc][0] if board[nr][nc] and board[nr][nc][1] != 'R' else 0
                                   for nr, nc in NEIGHBORS[(r, c)])
                    score -= conversion * 1.0
    
    return score

def check_winner(board):
    """Check if there's a winner - optimized"""
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

def is_winning_move(board, r, c, color, max_iterations=100):
    """Quick check if a move wins the game"""
    test_board = [row[:] for row in board]  # Shallow copy
    apply_move(test_board, r, c, color)
    explode(test_board, max_iterations=max_iterations)
    winner = check_winner(test_board)
    return winner == color

def minimax_no_timeout(board, depth, alpha, beta, maximizing_player, level):
    """Minimax algorithm without timeout - pure iteration-based"""
    if depth == 0:
        return evaluate_board(board, level), None
    
    player_color = 'B' if maximizing_player else 'R'
    valid_moves = get_valid_moves(board, player_color)
    
    if not valid_moves:
        return (-1000 - depth) if maximizing_player else (1000 + depth), None
    
    # Quick win check for maximizing player (AI)
    if maximizing_player:
        for r, c in valid_moves:
            if is_winning_move(board, r, c, player_color, max_iterations=100):
                return 1000 + depth, (r, c)
    
    # Move ordering: prioritize moves that affect more cells
    def move_priority(move):
        r, c = move
        cell = board[r][c]
        priority = 0
        
        # Prefer moves on cells with more orbs
        if cell:
            priority += cell[0] * 2
        
        # Prefer corner and edge positions
        priority += POSITION_WEIGHTS[(r, c)]
        
        # Prefer moves close to critical mass
        if cell and cell[1] == player_color:
            priority += (cell[0] / CRITICAL_MASS[(r, c)]) * 5
        
        return -priority  # Negative for descending sort
    
    valid_moves.sort(key=move_priority)
    
    best_move = None
    best_eval = float('-inf') if maximizing_player else float('inf')
    
    for r, c in valid_moves:
        new_board = copy.deepcopy(board)
        apply_move(new_board, r, c, player_color)
        explode(new_board, max_iterations=500)  # Max iterations for game simulation
        
        eval_score, _ = minimax_no_timeout(new_board, depth - 1, alpha, beta, not maximizing_player, level)
        
        if maximizing_player:
            if eval_score > best_eval:
                best_eval = eval_score
                best_move = (r, c)
            alpha = max(alpha, eval_score)
        else:
            if eval_score < best_eval:
                best_eval = eval_score
                best_move = (r, c)
            beta = min(beta, eval_score)
            
        if beta <= alpha:
            break
    
    return best_eval, best_move

def get_smart_random_move(valid_moves):
    """Get a smart random move (prefer corners/edges)"""
    corner_moves = []
    edge_moves = []
    center_moves = []
    
    for r, c in valid_moves:
        if (r in [0, ROWS-1]) and (c in [0, COLS-1]):
            corner_moves.append((r, c))
        elif r in [0, ROWS-1] or c in [0, COLS-1]:
            edge_moves.append((r, c))
        else:
            center_moves.append((r, c))
    
    # Choose from corner first, then edge, then center
    if corner_moves:
        return random.choice(corner_moves)
    elif edge_moves:
        return random.choice(edge_moves)
    else:
        return random.choice(center_moves)

def process_game_over(winner, board):
    """Handle game over scenarios"""
    result = "Red Wins" if winner == 'R' else "Blue Wins"
    print(f"{'Human' if winner == 'R' else 'AI'} ({winner}) wins!")
    write_gamestate(FILENAME, f"Game Over: {result}", board)

def main():
    """Main game loop for AI player without timeout logic"""
    config = load_game_config()
    level = config.get("level", 1)
    level_config = LEVEL_CONFIG[level]
    
    print(f" AI Player starting at Level {level} ({level_config['name']})...")
    print(f" Using heuristics: {', '.join(level_config['heuristics'])}")
    print(f" Search depth: {level_config['depth']}")
   # print(f" Using maximum iteration limits (no timeouts)")
    
    first_move = True
    
    while True:
        # Read human move with shorter polling interval
        board = read_gamestate(FILENAME, "Human Move:")
        
        if board is None:
            time.sleep(0.1)
            continue
        
        print("Human move detected, processing...")
        
        # Calculate AI move
        print(" AI thinking...")
        valid_moves = get_valid_moves(board, 'B')
        
        if not valid_moves:
            print(" No valid moves for AI!")
            write_gamestate(FILENAME, "Game Over: Red Wins", board)
            break
        
        # Quick win check first
        winning_move = None
        for r, c in valid_moves:
            if is_winning_move(board, r, c, 'B', max_iterations=100):
                winning_move = (r, c)
                break
        
        if winning_move:
            move = winning_move
            score = 1000
            think_time = 0
            strategy = "winning"
            print(f" AI found winning move immediately!")
        else:
            # Use minimax without timeout - pure iteration-based
            start_time = time.time()
            search_depth = level_config["depth"]
            
            score, move = minimax_no_timeout(board, search_depth, float('-inf'), float('inf'), True, level)
            think_time = time.time() - start_time
            
            if move is None:  # No valid move found (shouldn't happen normally)
                print(f" Minimax returned no move, using smart random move...")
                move = get_smart_random_move(valid_moves)
                score = 0
                strategy = "random"
            else:
                strategy = "minimax"
        
        r, c = move
        print(f" AI (Level {level}) plays at ({r}, {c}) - Strategy: {strategy}, Score: {score:.2f}, Time: {think_time:.3f}s")

        # Apply AI move
        apply_move(board, r, c, 'B')

        # Process explosions with max iterations
        explosion_levels = explode(board, max_iterations=1000)
        if explosion_levels > 1:
            print(f" Explosion: {explosion_levels} iterations")
        
        # Check winner ONLY if not first move
        if not first_move:
            winner = check_winner(board)
            if winner:
                process_game_over(winner, board)
                break
        else:
            first_move = False
            print(" First move completed")
            
        # Write game state
        if write_gamestate(FILENAME, "AI Move:", board):
            print(" AI move completed\n")
        else:
            print(" Failed to write game state\n")

if __name__ == "__main__":
    main()