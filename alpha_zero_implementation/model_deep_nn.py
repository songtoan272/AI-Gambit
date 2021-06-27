from dataclasses import dataclass

import numpy as np

from tensorflow.keras.layers import Conv2D, BatchNormalization, ReLU, Add, Input, Flatten, Dense
from tensorflow.keras import Model
from tensorflow.keras.regularizers import l2

from alpha_zero_implementation.configs.config import Config

@dataclass
class ChessTrainingExample:
    state: np.ndarray
    policy: [float]
    reward: float


class NeuralNet:
    """
    This class specifies the base NeuralNet class described in AGZ paper.
    The neural network does not consider the current player, and instead only deals with
    the canonical form of the board.

    This model can be trained to take observations of the game and return value and policy
    for any specific state of board.
    """

    def __init__(self, config: Config):
        self.config = config
        self.mc = self.config.model
        self.model = None

    def build(self):
        """Build the model and store in self.model"""
        input_layer = Input(self.mc.input_shape)

        x = input_layer
        x = self._add_conv_block(x)
        for i in range(1, self.mc.res_layer_num + 1):
            x = self._add_residual_block(x, i)

        network_output = x  # cnn_filter_num * 8 * 8
        policy_output = self._add_policy_head(network_output)
        value_output = self._add_value_head(network_output)

        self.model = Model(input_layer, [policy_output, value_output], name='chess_model')

    def _add_conv_block(self, input, name='input'):
        x = Conv2D(
            filters=self.mc.cnn_filter_num,
            kernel_size=self.mc.cnn_filter_size,
            padding='same',
            data_format='channels_first',
            use_bias=False,
            kernel_regularizer=l2(self.mc.l2_reg),
            name=name + 'conv' + str(self.mc.cnn_filter_num) + str(self.mc.cnn_filter_size)
        )(input)
        x = BatchNormalization(axis=1, name=name + 'batchnorm')(x)
        x = ReLU(name=name + '_relu')(x)
        return x

    def _add_residual_block(self, input, index):
        x = input  # retain input
        name = 'resi' + str(index)

        x = self._add_conv_block(x, name=name + '_block1')(x)
        x = Conv2D(
            filters=self.mc.cnn_filter_num,
            kernel_size=self.mc.cnn_filter_size,
            padding='same',
            data_format='channels_first',
            use_bias=False,
            kernel_regularizer=l2(self.mc.l2_reg),
            name=name + '_block2_conv' + str(self.mc.cnn_filter_num) + str(self.mc.cnn_filter_size)
        )(x)
        x = BatchNormalization(axis=1, name=name + '_block2_batchnorm')(x)
        x = Add(name=name + '_add')([x, input])
        x = ReLU(name=name + '_block2_relu')(x)
        return x

    def _add_policy_head(self, input):
        x = Conv2D(
            filters=self.mc.policy_filter_num,
            kernel_size=self.mc.policy_filter_size,
            padding='same',
            data_format='channels_first',
            use_bias=False,
            kernel_regularizer=l2(self.mc.l2_reg),
            name='policy_conv'
        )(input)
        x = BatchNormalization(axis=1, name='policy_batchnorm')(x)
        x = ReLU(name='policy_relu')(x)
        x = Flatten(name='policy_flatten')(x)
        x = Dense(
            self.config.n_labels,
            kernel_regularizer=l2(self.mc.l2_reg),
            activation='softmax',
            name='policy_output'
        )(x)
        return x

    def _add_value_head(self, input):
        x = Conv2D(
            filters=self.mc.value_filter_num,
            kernel_size=self.mc.value_filter_size,
            padding='same',
            data_format='channels_first',
            use_bias=False,
            kernel_regularizer=l2(self.mc.l2_reg),
            name='value_conv'
        )(input)
        x = BatchNormalization(axis=1, name='value_batchnorm')(x)
        x = ReLU(name='value_relu')(x)
        x = Flatten(name='value_flatten')(x)
        x = Dense(
            self.mc.value_fc_size,
            kernel_regularizer=l2(self.mc.l2_reg),
            activation='tanh',
            name='value_output'
        )(x)
        return x

    def calculate_loss(self):
        self.target_policy = tf.placeholder()

    def train(self, examples):
        """
        This function trains the neural network with examples obtained from
        self-play.

        Input:
            examples: a list of training examples, where each example is of form
                      (board, pi, v). pi is the MCTS informed policy vector for
                      the given board, and v is its value. The examples has
                      board in its canonical form.
        """
        pass

    def predict(self, board):
        """
        Input:
            board: current board in its canonical form.

        Returns:
            pi: a policy vector for the current board- a numpy array of length
                game.getActionSize
            v: a float in [-1,1] that gives the value of the current board
        """
        self.model
        pass

    def save_checkpoint(self, config_path, weight_path):
        """
        Saves the current neural network (with its parameters) in
        folder/filename
        """
        pass

    def load_checkpoint(self, config_path, weight_path):
        """
        Loads parameters of the neural network
        :param str config_path: path to the file containing the entire configuration
        :param str weight_path: path to the file containing the model weights
        :return: true iff successful in loading
        """
        pass
