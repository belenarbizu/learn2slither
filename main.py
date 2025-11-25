from agent import Agent
from game import Game
import pygame

def main():
    agent = Agent(batch_size=32, lr=0.005)
    game = Game()
    n_games = 0

    while True:
        # get current state
        current_state = game.get_state()
        # get move
        move = agent.get_action(current_state)
        # perform move and get new state
        reward, done, score = game.play_step(move)
        new_state = game.get_state()

        # train short memory
        agent.train_short_memory(current_state, move, reward, new_state, done)

        # remember
        agent.remember(current_state, move, reward, new_state, done)

        if score > 20:
            agent.model.save('model.pth')
            break

        if done:
            game.reset()
            n_games += 1
            if score > 0:
                print('Game', n_games, 'Score:', score)
            # train long memory
            agent.train_long_memory()
            agent.epsilon *= 0.995
            agent.epsilon = max(0.01, agent.epsilon)

if __name__ == '__main__':
    main()