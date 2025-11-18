from agent import Agent
from game import Game
import pygame

def main():
    agent = Agent(batch_size=100, lr=0.001)
    game = Game()

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
            # train long memory
            agent.train_long_memory()
            agent.epsilon = max(0.01, agent.epsilon - 0.001)

if __name__ == '__main__':
    main()