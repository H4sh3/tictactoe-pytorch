import random
import torch.nn as nn
import torch.optim as optim
import argparse
import sys
import torch
import gym
import tictactoe_env  # module init needs to run
from prop.algorithms.dqn import Agent
from prop.net.feed_forward import FeedForward

#!/usr/bin/env python
import signal
import sys


class FCNet(FeedForward):
    def __init__(self, obs_size, n_actions,_):
        # model is initiated in parent class, set params early.
        self.obs_size = obs_size
        self.n_actions = n_actions
        super(FCNet, self).__init__()

    def model(self):
        # observations -> hidden layer with relu activation -> actions
        return nn.Sequential(
            nn.Linear(self.obs_size, 12),
            nn.ReLU(),
            nn.Linear(12,12),
            nn.ReLU(),
            nn.Linear(12,12),
            #nn.ReLU(),
            #nn.Linear(64, 64),
            #nn.ReLU(),
            #nn.Linear(64, 64),
            #nn.ReLU(),
            nn.Linear(12, self.n_actions)
        )


class CNNNet(FeedForward):
    def __init__(self, obs_size, n_actions, device):
        # model is initiated in parent class, set params early.
        self.obs_size = obs_size
        self.n_actions = n_actions
        self.device = device
        super(CNNNet, self).__init__()

    def model(self):
        return nn.Sequential(
            # convolution 1
            # 3 channels -> `out_channels` different kernels/feature maps
            nn.Conv2d(in_channels=3, out_channels=512,
                      kernel_size=3, stride=1, padding=2),
            nn.ReLU(),  # negative numbers -> 0
            # deformation invariance; subtle changes are captured
            nn.MaxPool2d(kernel_size=5, stride=1),
            # flatten
            nn.Flatten(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, self.n_actions)
        )

    def forward(self, x, mask=[]):
        # transfrom from one tensor of shape (9) into 3 tensors of shape (3,3) each
        empty = torch.zeros(x.size(),device=self.device).masked_scatter_(
            (x == 0), torch.ones(x.size(),device=self.device)).view(-1, 3, 3)
        player1 = torch.zeros(x.size(),device=self.device).masked_scatter_(
            (x == 1), torch.ones(x.size(),device=self.device)).view(-1, 3, 3)
        player2 = torch.zeros(x.size(),device=self.device).masked_scatter_(
            (x == 2), torch.ones(x.size(),device=self.device)).view(-1, 3, 3)
        cnn_input = torch.stack((empty, player1, player2), dim=1)
        return super(CNNNet, self).forward(cnn_input, mask)


if __name__ == "__main__":
    # flags
    parser = argparse.ArgumentParser()
    parser.add_argument('-device', action="store", dest="device",
                        type=str, default="cpu", choices=["cpu", "cuda"])
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        print("cuda is not available")
        args.device = "cpu"

    device = torch.device(args.device)
    print(f"using device: {device}")

    tictactoe_env = gym.make('TicTacToeRandomPlayer-v0',
                             thresholds=dict(
                                 win_rate=0.92,
                                 draw_rate=0.08
                             ))
    tictactoe_env.spec.reward_threshold = tictactoe_env.performance_threshold
    print(f"performance threshold: {tictactoe_env.performance_threshold}")

    agent = Agent(
        logdir="logs",
        env=tictactoe_env,
        net=FCNet,
        name="dqn-cnn",
        learning_rate=1e-5,
        batch_size=128,
        optimizer=optim.Adam,
        loss_cutoff=0.03,
        max_std_dev=0.09,
        epsilon_decay=3000,
        double=True,
        target_net_update=500,
        eval_every=100,
        dev=device)

    # register sig handler to save model on abort
    def signal_handler(sig, frame):
        torch.save(agent.policy_net.state_dict(), f"policies/ff-v1")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)


    agent.train()


    print(f"#### stats ####")
    print(f"games played: {tictactoe_env.stats['games_played']}")
    signal.pause()

