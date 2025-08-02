import time
import os
import random

ROWS, COLS = 9, 6
FILENAME = "gamestate.txt"

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
    """Get all valid moves for a player"""
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
                    return None  # Game continues
    
    # Only declare winner if we have enough orbs on board (both players have played)
    if total_orbs < 2:
        return None  # Too early to have a winner
    
    if red_exists and not blue_exists:
        return 'R'
    elif blue_exists and not red_exists:
        return 'B'
    return None

def process_game_over(winner, board):
    """Handle game over scenarios"""
    result = "Red Wins" if winner == 'R' else "Blue Wins"
    print(f"{'Random AI' if winner == 'R' else 'Smart AI'} ({winner}) wins!")
    write_gamestate(FILENAME, f"Game Over: {result}", board)

def main():
    """Main game loop for Random AI player without timeout logic"""
    print(" Random AI Player starting...")
    print(" Using maximum iteration limits (no timeouts)")
    
    # Wait a moment for everything to initialize
    time.sleep(1)
    
    # Initialize empty board for first move
    board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    first_move = True
    move_number = 0
    
    while True:
        if first_move:
            # Random AI goes first in AI vs AI mode
            print(" Random AI making first move...")
            time.sleep(0.5)  # Small delay to ensure viewer is ready
        else:
            # Read Smart AI move
            print(" Random AI waiting for Smart AI move...")
            board = read_gamestate(FILENAME, "Smart AI Move:")
            
            if board is None:
                time.sleep(0.1)
                continue
            
            print(" Smart AI move detected, processing...")
        
        # Calculate Random AI move
        move_number += 1
        print(f" Random AI thinking... (Move {move_number})")
        valid_moves = get_valid_moves(board, 'R')
        
        if not valid_moves:
            print(" No valid moves for Random AI!")
            write_gamestate(FILENAME, "Game Over: Blue Wins", board)
            break
        
        # Random move selection
        move = random.choice(valid_moves)
        r, c = move
        
        print(f" Random AI plays at ({r}, {c})")

        # Apply Random AI move
        apply_move(board, r, c, 'R')

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
            print(" Random AI first move completed")

        # Write game state
        if write_gamestate(FILENAME, "Random AI Move:", board):
            print(" Random AI move completed\n")
        else:
            print(" Warning: Failed to write game state\n")
        
        # Delay to make it easier to follow
        time.sleep(1.0)

if __name__ == "__main__":
    main()