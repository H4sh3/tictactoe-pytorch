from gym.envs.registration import registry, register, make, spec

# register all environments here so gym.make() can get them.

register(
    id='TicTacToeBase-v0',
    entry_point='environment.base:TicTacToeEnv',
    reward_threshold=0.7,
)

register(
    id='TicTacToeHumanPlayer-v0',
    entry_point='environment.human_player:TicTacToeEnv',
    reward_threshold=0.7,
)

register(
    id='TicTacToeRandomPlayer-v0',
    entry_point='environment.random_player:TicTacToeEnv',
    reward_threshold=0.7,
)

register(
    id='TicTacToePunishIllegalMoves-v0',
    entry_point='environment.punish_illegal_moves:TicTacToeEnv',
    reward_threshold=0.7,
)
