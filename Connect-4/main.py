from random import choice
from math import floor
from copy import deepcopy
import pygame

moves_in_future = 7

 
class Window:
    WIDTH = 490
    HEIGHT = 520
    COLUMNS = 7
    ROWS = 6
 
    def __init__(self):
        pygame.init()

        self.win = pygame.display.set_mode((Window.WIDTH, Window.HEIGHT))
        pygame.display.set_caption("Connect 4")

        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font("freesansbold.ttf", 32)
        self.font_small = pygame.font.Font("freesansbold.ttf", 20)
        self.title = self.font_big.render("Connect 4", True, (255, 255, 255))
 
        self.board_img = pygame.image.load("board.png").convert_alpha()
        self.board_img_height = self.board_img.get_height()
        self.board_top = Window.HEIGHT - self.board_img_height
 
        self.board = [[0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0]]
 
        self.column_width = 67.5
        self.row_height = 67.4
 
        self.turn = 1
        self.AI = choice([1, -1])
 
        self.P1 = (255, 0, 0)
        self.P2 = (255, 255, 0)
 
        self.run = True
        while self.run:
            self.main_loop()
 
    def main_loop(self):
        if self.turn == self.AI:
            MiniMax.moves = {}
            ai_move = MiniMax.best_move(self.board, moves_in_future, self.AI, True, -float("inf"), float("inf"))

            self.add_token(self.board, ai_move[0], animate=True)
 
            winner = MiniMax.winning_board(self.board)
            if winner:
                self.winner(winner)
            self.turn *= -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.turn == self.AI:
                    continue

                column = int(abs((pygame.mouse.get_pos()[0] - 7.5)/self.column_width))
                column = Window.COLUMNS-1 if column > Window.COLUMNS-1 else column
                token = self.add_token(self.board, column, animate=True)  # todo fix brocken if click far right

                if token != "invalid":
                    winner = MiniMax.winning_board(self.board)
                    if winner:
                        self.winner(winner)
                    self.turn *= -1

        self.win.fill((33, 33, 33))
        self.render_screen()
 
        self.clock.tick(60)

    def winner(self, winning_tokens):
        token = "Bot" if winning_tokens[0] == self.AI else "You"
        start_pt = winning_tokens[1]
        end_pt = winning_tokens[2]
 
        self.win.fill((33, 33, 33))
        self.render_screen()

        text = self.font_big.render(f"{token} won", True, (255, 255, 255), (33, 33, 33))
        self.win.blit(text, (5, self.board_top - text.get_height() - 5))
        pygame.draw.line(self.win, (255, 255, 255), (43 + start_pt[0]*self.column_width,
                                                     43 + self.board_top + start_pt[1]*self.row_height),
                         (43 + end_pt[0] * self.column_width,
                          43 + self.board_top + end_pt[1] * self.row_height), 5)
        pygame.display.update()
 
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    return

            self.clock.tick(60)

    def add_token(self, board, column, animate=False):      
        for i in range(Window.ROWS):
            if not board[Window.ROWS-i-1][column]:
                if animate:
                    self.drop_token_animation(Window.ROWS-i-1, column, self.turn)
                board[Window.ROWS-i-1][column] = self.turn
                return board
        return "invalid"

    def drop_token_animation(self, row, column, token_type):
        colour = self.P1 if token_type == 1 else self.P2

        x, y = 43 + column * self.column_width, 43 + row * self.row_height + self.board_top
        current_y = self.board_top
        y_vel = 0
        bounce_factor = 0.5

        while current_y <= y:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    return

            self.win.fill((33, 33, 33))
            pygame.draw.circle(self.win, colour, (x, current_y), 30)
            self.render_screen()

            current_y += y_vel
            y_vel += 0.8

            if current_y > y and y_vel > 7:
                y_vel *= -bounce_factor
                current_y = y

            pygame.display.update()
            self.clock.tick(60)

    def render_screen(self):
        self.render_board()

        self.win.blit(self.title, (Window.WIDTH // 2 - self.title.get_width() // 2, 20))

        turn = "Bot's" if self.AI == self.turn else "Your"
        text = self.font_small.render(f"{turn} turn", True, (255, 255, 255))
        self.win.blit(text, (5, self.board_top - text.get_height() - 5))

        pygame.display.update()

    def render_board(self):
        for y in range(Window.ROWS):
            for x in range(Window.COLUMNS):
                if not self.board[y][x]:
                    continue
                colour = self.P1 if self.board[y][x] == 1 else self.P2
                pygame.draw.circle(self.win, colour, 
                    (43 + x*self.column_width, 43 + y*self.row_height + self.board_top), 30)
        self.win.blit(self.board_img, (0, self.board_top))


class MiniMax:
    @staticmethod
    def best_move(board, depth, bot, maximise, alpha, beta):
        terminal = MiniMax.terminal_position(board)

        if terminal or depth == 0:
            if terminal:
                if terminal == bot:
                    return (None, 9999999999999)
                elif terminal == bot * -1:
                    return (None, -9999999999999)
                else:
                    return (None, 0)
            else:
                return (None, MiniMax.evaluate_board(board, bot))

        if maximise:
            boards = MiniMax.all_moves(board, bot)
            column = choice(boards)[1]
            value = -float("inf")
            for b, col in boards:
                new_score = MiniMax.best_move(b, depth - 1, bot, False, alpha, beta)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            return column, value
        else:
            boards = MiniMax.all_moves(board, bot*-1)
            column = choice(boards)[1]
            value = float("inf")
            for b, col in boards:
                new_score = MiniMax.best_move(b, depth - 1, bot, True, alpha, beta)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break

            return column, value

    @staticmethod
    def terminal_position(board):
        win = MiniMax.winning_board(board)
        if win:
            return win[0]
        if True not in [0 in row for row in board]:
            return "tie"
        return False

    @staticmethod
    def evaluate_section(section, bot):
        blanks = section.count(0)
        if blanks == 4:
            return 0
 
        bot = section.count(bot)
        if bot:
            if bot == 1 and blanks == 3:
                return 1  # -----------------------
            elif bot == 2 and blanks == 2:
                return 10  # -----------------------
            elif bot == 3 and blanks == 1:
                return 25  # -----------------------
            elif bot == 4:
                return 99999999999  # -----------------------
        else:
            player = section.count(bot*-1)
            if player == 1:
                return -0  # ----------------------- -2
            elif player == 2:
                return -0  # ----------------------- -20
            else:
                return -20  # ----------------------- -99999
        return 0

    @staticmethod
    def evaluate_board(board, bot):
        score = 0
        centre = [board[i][3] for i in range(Window.ROWS)]
        score += centre.count(bot) * 3

        for row in range(Window.ROWS):
            for i in range(Window.COLUMNS - 3):
                score += MiniMax.evaluate_section(board[row][i:i+4], bot)
 
        for col in range(Window.COLUMNS):
            for i in range(Window.ROWS - 3):
                score += MiniMax.evaluate_section([board[i][col], board[i+1][col],
                                                board[i+2][col], board[i+3][col]], bot)
 
        for x in range(4):
            for y in range(3):
                score += MiniMax.evaluate_section([board[y][x], board[y+1][x+1], board[y+2][x+2], board[y+3][x+3]], 
                    bot)
 
        for x in range(4):
            for y in range(3):
                score += MiniMax.evaluate_section([board[5-y][x], board[4-y][x+1], board[3-y][x+2], board[2-y][x+3]], 
                    bot)
 
        return score

    @staticmethod
    def all_moves(board, player):
        boards = []
        for column in range(Window.COLUMNS):

            token = MiniMax.add_token(deepcopy(board), column, player)
            if token != "Invalid":
                boards.append((token, column))
        return boards

    @staticmethod
    def add_token(board, column, player):
        for i in range(Window.ROWS):
            if not board[Window.ROWS-i-1][column]:
                board[Window.ROWS-i-1][column] = player
                return board
        return "Invalid"

    @staticmethod
    def winning_board(board):
        for row in range(Window.ROWS):
            for i in range(Window.COLUMNS - 3):
                if board[row][i] == board[row][i+1] == board[row][i+2] == board[row][i+3] != 0:
                    return board[row][i], (i, row), (i + 3, row)
 
        for col in range(Window.COLUMNS):
            for i in range(Window.ROWS - 3):
                if board[i][col] == board[i+1][col] == board[i+2][col] == board[i+3][col] != 0:
                    return board[i][col], (col, i), (col, i + 3)
 
        for x in range(4):
            for y in range(3):
                if board[y][x] == board[y+1][x+1] == board[y+2][x+2] == board[y+3][x+3] != 0:
                    return board[y][x], (x, y), (x + 3, y + 3)
 
        for x in range(4):
            for y in range(3):
                if board[5-y][x] == board[4-y][x+1] == board[3-y][x+2] == board[2-y][x+3] != 0:
                    return board[5-y][x], (x, 5 - y), (x + 3, 2 - y)

        return False

if __name__ == '__main__':
    window = Window()