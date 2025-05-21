class Moves_rules:
    def __init__(self, board):
        self.__board = board

    def yellow_case_move(self, x_start, y_start, x_end, y_end):
        # Diagonal movement
        dx, dy = x_end - x_start, y_end - y_start
        if abs(dx) != abs(dy): 
            return False
        
        # Check obstacles
        sx = 1 if dx > 0 else -1
        sy = 1 if dy > 0 else -1
        
        for i in range(1, abs(dx)):
            x, y = x_start + i*sx, y_start + i*sy
            if self.__board[x][y] % 10 != 0:  
                return False
                
        # Check end case
        end_piece = self.__board[x_end][y_end] % 10
        current_player = self.__board[x_start][y_start] % 10
        
        # The end case must be empty or contain an opponent's piece
        return end_piece == 0 or (end_piece != current_player)

    def blue_case_move(self, x_start, y_start, x_end, y_end):
        dx, dy = abs(x_end - x_start), abs(y_end - y_start)
        if dx > 1 or dy > 1:
            return False
            
        
        end_piece = self.__board[x_end][y_end] % 10
        current_player = self.__board[x_start][y_start] % 10
        
        
        return end_piece == 0 or (end_piece != current_player)

    def green_case_move(self, x_start, y_start, x_end, y_end):
        # MOUVEMENT EN L
        dx, dy = abs(x_end - x_start), abs(y_end - y_start)
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            return False
            
        
        end_piece = self.__board[x_end][y_end] % 10
        current_player = self.__board[x_start][y_start] % 10
        
        
        return end_piece == 0 or (end_piece != current_player)

    def red_case_move(self, x_start, y_start, x_end, y_end):
        # HORIZONTAL OR VERTICAL MOVEMENT
        if x_start != x_end and y_start != y_end:
            return False
            
        
        dx = 0 if x_start == x_end else (1 if x_end > x_start else -1)
        dy = 0 if y_start == y_end else (1 if y_end > y_start else -1)
        
        # Check obstacles
        x, y = x_start + dx, y_start + dy
        while (x, y) != (x_end, y_end):
            if self.__board[x][y] % 10 != 0:  
                return False
            x, y = x + dx, y + dy
            
        
        end_piece = self.__board[x_end][y_end] % 10
        current_player = self.__board[x_start][y_start] % 10
        
        return end_piece == 0 or (end_piece != current_player)
    
    def verify_move(self, case_color, x_start, y_start, x_end, y_end):
        couleur = case_color // 10
        
        if couleur == 1:
            return self.blue_case_move(x_start, y_start, x_end, y_end)
        elif couleur == 2:
            return self.green_case_move(x_start, y_start, x_end, y_end)
        elif couleur == 3:
            return self.yellow_case_move(x_start, y_start, x_end, y_end)
        elif couleur == 4:
            return self.red_case_move(x_start, y_start, x_end, y_end)
        else:  
            return False