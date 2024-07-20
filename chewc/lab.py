# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_lab.ipynb.

# %% auto 0
__all__ = ['SelectionIntensityEnvironment']

# %% ../nbs/04_lab.ipynb 1
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import numpy as np
from .sim import *
import torch
class SelectionIntensityEnvironment(gym.Env):
    def __init__(self, SP, config):
        super(SelectionIntensityEnvironment, self).__init__()
        self.SP = SP
        self.config = config  # Store the config
        self.current_generation = 0
        self.max_generations = SP.max_generations
        # Get action space bounds from config, with defaults if not provided
        
        self.action_low = config.get('action_low', 0.01)
        self.action_high = config.get('action_high', 0.99)
        
        self.action_space = gym.spaces.Box(
            low=np.array([self.action_low]), 
            high=np.array([self.action_high]), 
            dtype=np.float32
        )
        
        # Update observation space based on config
#         obs_config = config['observation_config']['remaining_proportion']
        self.observation_config = config['observation_config']
        # Dynamically create observation space
        obs_low = []
        obs_high = []
        self.obs_keys = []
        for key, value in self.observation_config.items():
            self.obs_keys.append(key)
            obs_low.append(value['low'])
            obs_high.append(value['high'])
        
        self.observation_space = gym.spaces.Box(
            low=np.array(obs_low, dtype=np.float32),
            high=np.array(obs_high, dtype=np.float32)
        )

        self.action_values = []
        self.genetic_variance = []
        self.max_breeding_values = []
        self.final_generations = []
        self.episode_count = 0
        self.rewards = []
        self.episode_reward = 0
        
        #config
        self.config =config
        
    def _get_obs(self):
        obs = []
        for key in self.obs_keys:
            if key == 'remaining_proportion':
                obs.append(1 - (self.current_generation / self.max_generations))
            elif key == 'genetic_variance':
                obs.append(self.population.breeding_values.var().cpu().item())
            elif key == 'mean_phenotype':
                obs.append(self.population.phenotypes.mean().cpu().item())
            elif key == 'max_breeding_value':
                obs.append(self.population.breeding_values.max().cpu().item())
            # Add more elif statements for other possible inputs
        return np.array(obs, dtype=np.float32)


    def _get_info(self):
        return {
            "max_phenotype": self.population.breeding_values.max().cpu().item(),
            "genetic_variance": self.population.breeding_values.var().cpu().item(),
            "current_generation": self.current_generation
        }
    
    def update_max_generations(self, new_max_gen):
        self.SP.update_max_generations(new_max_gen)
        self.max_generations = self.SP.max_generations

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.population = self.SP.founder_pop
        self.phenotype = phenotype(self.population, self.SP.T, self.SP.h2)
        self.current_generation = 0
        self.episode_reward = 0
        self.max_generations = self.SP.max_generations
        observation = self._get_obs()
        info = self._get_info()
        
        return observation, info

    def step(self, action):
        
        # Map the action from [-1, 1] to [action_low, action_high]
#         print('raw', action)
#         action = scale_values(action, to_range=(self.action_low, self.action_high))
#         print('usu', action)
        total_selected = max((2,int(action * self.population.size)))
        selected = torch.topk(self.population.phenotypes, total_selected).indices
        self.population = create_pop(self.SP.G, random_crosses(self.population.haplotypes[selected], self.SP.pop_size))
        self.phenotype = phenotype(self.population, self.SP.T, self.SP.h2)
        self.current_generation += 1

        observation = self._get_obs()
        info = self._get_info()
        info['normalized_action'] = action
        
        terminated = self.current_generation > self.SP.max_generations
        #REWARD
        if self.config.get('sparse_reward', False):  # Use .get() with a default value
            reward = 0 if not terminated else float(self.population.breeding_values.max())
        else:
            reward = float(self.population.breeding_values.max())
        self.episode_reward += reward

        if terminated:
            info['final_generation'] = {
            "max_phenotype": self.population.breeding_values.max().cpu().item(),
            "genetic_variance": self.population.breeding_values.var().cpu().item(),
            "current_generation": self.current_generation
            }

        return observation, reward, bool(terminated), False, info
