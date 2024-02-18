import gymnasium as gym
import random

env = gym.make("LunarLander-v2", render_mode="human")
observation, info = env.reset()
print(observation, info)
for _ in range(10):
    act = [random.randint(0,3) for i in range(100)]
    for action in act:
        observation, reward, terminated, truncated, info = env.step(action)
        print(reward)

        if terminated or truncated:
            observation, info = env.reset()

env.close()