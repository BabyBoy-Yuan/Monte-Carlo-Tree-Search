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

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.state.is_terminal()

    def ucb1_score(self, exploration_constant=1.414):
        """计算 UCB1 分数"""
        if self.visits == 0:
            return float('inf')

        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration
class MCTS:
    def __init__(self, exploration_constant=1.414):
        self.C = exploration_constant

    def search(self, root_state, iterations=1000):
        root_node = MCTSNode(state=root_state)

        for _ in range(iterations):
            node = self._select(root_node)

            # 2. 扩展
            if not node.is_terminal():
                node = self._expand(node)

            # 3. 轮演
            reward = self._simulate(node.state)

            # 4. 回溯
            self._backpropagate(node, reward)

        return self._best_move(root_node)

    def _select(self, node):
        while node.is_fully_expanded() and not node.is_terminal():
            node = max(node.children, key=lambda c: c.ucb1_score(self.C))
        return node

    def _expand(self, node):
        move = node.untried_moves.pop()
        next_state = node.state.take_move(move)
        child_node = MCTSNode(state=next_state, parent=node, move=move)
        node.children.append(child_node)
        return child_node

    def _simulate(self, state):
        current_state = state
        while not current_state.is_terminal():
            possible_moves = current_state.get_legal_moves()
            move = random.choice(possible_moves)
            current_state = current_state.take_move(move)
        return current_state.get_reward()

    def _backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent
            reward = -reward

    def _best_move(self, root_node):
        return max(root_node.children, key=lambda c: c.visits).move