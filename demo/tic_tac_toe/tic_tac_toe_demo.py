import pygame
import sys
import math
import random

class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_legal_moves()

    def ucb1_score(self, C=1.414):
        if self.visits == 0: return float('inf')
        return (self.wins / self.visits) + C * math.sqrt(math.log(self.parent.visits) / self.visits)


class MCTS:
    def search(self, root_state, iterations=1500):
        root_node = MCTSNode(state=root_state)
        for _ in range(iterations):
            node = root_node
            while not node.untried_moves and node.children:
                node = max(node.children, key=lambda c: c.ucb1_score())
            if node.untried_moves:
                move = node.untried_moves.pop()
                state = node.state.take_move(move)
                child = MCTSNode(state=state, parent=node, move=move)
                node.children.append(child)
                node = child
            curr_state = node.state
            while not curr_state.is_terminal():
                curr_state = curr_state.take_move(random.choice(curr_state.get_legal_moves()))
            reward = curr_state.get_reward()
            while node:
                node.visits += 1
                node.wins += reward
                node = node.parent
                reward = -reward
        return max(root_node.children, key=lambda c: c.visits).move


class TicTacToeState:
    def __init__(self, board=None, player=1):
        self.board = board if board else [0] * 9
        self.current_player = player

    def get_legal_moves(self):
        return [i for i, v in enumerate(self.board) if v == 0]

    def take_move(self, move):
        new_board = list(self.board)
        new_board[move] = self.current_player
        return TicTacToeState(new_board, -self.current_player)

    def is_terminal(self):
        return self._check_winner() is not None or 0 not in self.board

    def get_reward(self):
        winner = self._check_winner()
        if winner == 0: return 0
        return 1 if winner != self.current_player else -1

    def _check_winner(self):
        wins = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in wins:
            if self.board[a] != 0 and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return 0 if 0 not in self.board else None



WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
SQUARE_SIZE = WIDTH // 3
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
POPUP_BG = (255, 255, 255)
TEXT_COLOR = (30, 30, 30)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('MCTS 井字棋 - 挑战 AI')
font = pygame.font.SysFont('Arial', 60, bold=True)


def draw_lines():
    screen.fill(BG_COLOR)
    # 画井字线
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)


def draw_figures(board):
    for i in range(9):
        row, col = i // 3, i % 3
        center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
        if board[i] == 1:
            pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                             (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
            pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                             (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                             CROSS_WIDTH)
        elif board[i] == -1:
            pygame.draw.circle(screen, CIRCLE_COLOR, center, CIRCLE_RADIUS, CIRCLE_WIDTH)


def draw_game_over(winner):
    """ 绘制结果弹窗 """
    if winner == 1:
        text_content = "YOU WIN!"
        color = (0, 200, 0)
    elif winner == -1:
        text_content = "AI WINS!"
        color = (200, 0, 0)
    else:
        text_content = "DRAW GAME!"
        color = (100, 100, 100)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 180))
    screen.blit(overlay, (0, 0))

    text_surf = font.render(text_content, True, color)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    padding = 20
    bg_rect = text_rect.inflate(padding * 2, padding * 2)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=10)
    pygame.draw.rect(screen, color, bg_rect, width=5, border_radius=10)

    screen.blit(text_surf, text_rect)


def main():
    game = TicTacToeState()
    mcts = MCTS()
    draw_lines()

    game_over = False
    winner = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                game = TicTacToeState()
                game_over = False
                winner = None
                draw_lines()
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and game.current_player == 1:
                mouseX, mouseY = event.pos
                move = (mouseY // SQUARE_SIZE) * 3 + (mouseX // SQUARE_SIZE)

                if move in game.get_legal_moves():
                    game = game.take_move(move)
                    draw_figures(game.board)
                    pygame.display.update()

                    if game.is_terminal():
                        game_over = True
                        winner = game._check_winner()

        if not game_over and game.current_player == -1:
            pygame.time.wait(500)
            move = mcts.search(game, iterations=1500)
            game = game.take_move(move)
            draw_figures(game.board)
            pygame.display.update()

            if game.is_terminal():
                game_over = True
                winner = game._check_winner()

        if game_over:
            draw_game_over(winner)

        pygame.display.update()


if __name__ == "__main__":
    main()