from typing import Optional

import chess
import numpy as np
import math
import logging

from collections import defaultdict
from chess_env import ChessGame
from model_deep_nn import NeuralNet, ChessTrainingExample

"""
Implementation of a Monte Carlo Tree Search with different classes for Node, Edge and the MCTS itself
The Node corresponds to a state. The Edge corresponds to a possible next action from a state
"""


class ActionEdge(object):
    """
    Holds the stats of a specific action a  taken from a specific state s

    Attributes:
        :ivar int n: the number of times action a has been taken from state s
        :ivar float w: the total value of the next state = the accumulated value from every time algo
            visits a child of this action, each value is calculated by the value head of the NN
        :ivar float q: the mean value of the next state = w/n
        :ivar float p: the prior probability of selecting action a, given by the policy head of the NN
    """

    def __init__(self):
        self.n = 0
        # self.w = 0.0
        self.q = 0.0
        self.p = 0.0

    def ucb1(self, c_puct, N):
        """
        Calculate the upper confidence bound for taking the action a form state s
        :param N: #visits the parent node of the action
        :param c_puct: a hyperparameter that controls the degree of exploration
        :return: the upper confidence bound on the Q-values
        """
        return self.q + c_puct * self.p * math.sqrt(math.log(N) / (1 + self.n))

    def propagate(self, value):
        self.q = (self.q * self.n) + value / (self.n + 1)
        self.n += 1


class StateNode:
    """
    Define the node of a Monte Carlo Tree Search that is basically a state of the game env.
    Attributes:
        :ivar defaultdict actions: a dictionary represents the stats of all actions can be taken from this state
        :ivar int sum_n: sum of the n value for each of the actions in self.a = total visits over all actions
            in self.a
    """

    def __init__(self):
        self.a = defaultdict(ActionEdge)
        self.sum_n = 0

    def propagate(self, action, value):
        self.sum_n += 1
        self.a[action].propagate(value)

    def best_action(self, c_puct):
        """
        Choose the action that maximise the UCB1 score
        :return:
        """
        ucb1_a = {k: v.ucb1(self.sum_n, c_puct) for k, v in self.a.items()}
        return np.argmax(ucb1_a)

    def set_actions_proba(self, moves, policy):
        # moves = [mov.uci() for mov in board.legal_moves]
        for action, proba in zip(moves, policy):
            self.a[action].p = proba

    def select_move(self, deterministic=True, temp_parameter: Optional[float] = None) -> str:
        if deterministic:
            max_n = -1
            best_action = None
            for a, action in self.a.items():
                if action.n > max_n:
                    max_n = action.n
                    best_action = a
            return best_action
        else:
            assert temp_parameter is not None
            pass

    @property
    def policy(self, board):
        moves = [mov.uci() for mov in board.legal_moves]
        return [self.a[move].p for move in moves]


class ChessMCTS:
    """
    Define the MCTS of a game to choose moves based on policy and value network predictions

    Attributes:
        :ivar
    """

    def __init__(self, game: ChessGame, nnet: NeuralNet, c_puct: float, num_simulations):
        self.tree = defaultdict(StateNode)
        self.game = game
        self.nnet = nnet
        self.c_puct = c_puct
        self.num_sims = num_simulations

    @property
    def current_state(self):
        return self.tree[self.game.string_repr()]

    def reset(self):
        """
        reset the tree to begin a new exploration of states
        """
        self.tree = defaultdict(StateNode)

    def simulate_search(self):
        """Simulate one search of MCTS
            We keep the board order turn when doing the simulation but pass canonical board to the neural network
            to train and predict. Policy and value are reversed based on player turn"""
        canonical_board = self.game.get_canonical_board()
        s = self.game.string_repr()

        if self.game.is_ended:
            # terminal node
            return ChessGame.get_game_ended(self.game.board)

        if s not in self.tree:
            # leaf node, not yet explored
            policy, value = self.nnet.predict(canonical_board)
            moves = [move.uci() for move in canonical_board.legal_moves]
            moves = ChessGame.inverse_moves(moves) if not self.game.is_white_turn else moves
            self.tree[s].set_actions_proba(moves, policy)
            return value
        else:
            # Choose action maximizing ucb1
            chosen_action = self.tree[s].best_action(self.c_puct)
            self.game.move(chosen_action)  # make (simulate) a move
            value = self.simulate_search()  # do the MCTS on the new state after the move
            self.game.retreat_move()  # go back a move
            self.tree[s].propagate(chosen_action, value)
            return value

    def execute_episode(self):
        """
        Play a chess match (episode).
        FOr each state, simulate a number of monte carlo tree search then choose a best move according to baseline
        :return: a list of training examples for the neural network
        """
        examples = []
        while True:
            for _ in range(self.num_sims):
                self.simulate_search()
            examples.append(ChessTrainingExample(
                state=self.game.serialize(),
                policy=self.current_state.policy,
                reward=math.inf
            ))
            best_move = self.current_state.select_move()
            self.game.move(best_move)
            if self.game.is_ended:
                reward = self.game.result
                for ex in examples:
                    ex.reward = reward
                break
        return examples

    # def policy_iteration_self_play(self):
    #     """
    #     Train the neural network
    #     Play a number of episodes with itself to then update the neural network based on the examples generated
    #     during the plays.
    #     :return:
    #     """
    #     training_examples = []
    #     for