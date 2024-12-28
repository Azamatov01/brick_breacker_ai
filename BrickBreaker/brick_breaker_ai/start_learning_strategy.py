import numpy as np

def get_next_action(EPSILON, game, model):
    if np.random.random() < EPSILON:
        if game.ball_x < game.paddle_x:
            action = 0
        elif game.ball_x > (game.paddle_x + game.PADDLE_WIDTH):
            action = 2
        else:
            action = 1
    else:
        action = model.predict(state)

    return action