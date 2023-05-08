import numpy as np
from invaders import *
from rl.agents import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import EpsGreedyQPolicy, LinearAnnealedPolicy
from tensorflow.keras.layers import Conv2D, Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam


class Agent:
    def __init__(self):
        self.env = SpaceInvaders(agent=True)

    def build_model(self):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=8, strides=4, activation='relu', input_shape=(1, WIDTH, HEIGHT, 3)))
        model.add(Conv2D(64, kernel_size=4, strides=2, activation='relu'))
        model.add(Conv2D(64, kernel_size=3, strides=1, activation='relu'))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dense(4, activation='linear'))
        return model
    
    def build_agent(self):
        policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.2, nb_steps=10000)
        memory = SequentialMemory(limit=1000, window_length=1)
        dqn = DQNAgent(model=self.build_model(), 
                       memory=memory, 
                       policy=policy, 
                       nb_actions=4, 
                       nb_steps_warmup=100, 
                       target_model_update=1e-2)
        return dqn
    
    def train(self):
        dqn = self.build_agent()
        dqn.compile(Adam(lr=1e-3))
        dqn.fit(self.env, nb_steps=10000, visualize=False, verbose=2)
        dqn.save_weights('dqn_weights.h5f', overwrite=True)
        return dqn

    def test(self):
        dqn = self.train()
        scores = dqn.test(self.env, nb_episodes=3, visualize=False)
        print(np.mean(scores.history['episode_reward']))

if __name__ == "__main__":
    agent = Agent()
    agent.test()
