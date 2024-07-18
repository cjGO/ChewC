# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_config.ipynb.

# %% auto 0
__all__ = ['get_default_config', 'create_simulation', 'set_seed']

# %% ../nbs/00_config.ipynb 1
from .lab import *
from .sim import *
from .policy import *
import numpy as np
import torch
# from stable_baselines3.common.vec_env import DummyVecEnv

def get_default_config():
    config = {
        # Environment parameters
        'action_low': 0.05,
        'action_high': 0.95,
        'sparse_reward': False,

        # Simulation parameters
        'n_parents':10,
        'n_chr': 1,
        'n_loci': 100,
        'pop_size': 200,
        'max_generations': 10,
        'h2': 0.5,
        'target_mean': 0,
        'target_variance': 1,
        'reps':1,

        # Training parameters
        'total_timesteps': 100000,
        'learning_rate': 3e-4,
        'gae_lambda': 0.95,

        # Callback parameters
        'log_freq': 100,

        # Progressive parameters
        'start_gen': 10,
        'end_gen': 100,
        'start_gae_lambda': 0.9,
        'end_gae_lambda': 0.95,

        # Seed
        'seed': None
    }
    return config



def create_simulation(config=None):
    if config is None:
        config = get_default_config()
    
    seed = config['seed']
    if seed is not None:
        set_seed(seed)

    G = Genome(config['n_chr'], config['n_loci'], seed=seed)
    founder_haplotypes = np.load('../nbs/data/g2f_ch10.npy')
    
    # n_parents determines diversity approximately
    random_parent_indices = np.random.choice(founder_haplotypes.shape[0], config['n_parents'], replace=False)
    random_loci_indices = np.random.choice(founder_haplotypes.shape[2], config['n_loci'], replace=False)
    founder_haplotypes = founder_haplotypes[random_parent_indices,:,:]
    founder_haplotypes = founder_haplotypes[:,:,random_loci_indices]
    founder_haplotypes = torch.tensor(founder_haplotypes).unsqueeze(2)

    # one round of random crossing with said parents to generate appropriate pop size which must be fixed in this env
    founder_pop = create_pop(G, founder_haplotypes)
    founder_pop = random_crosses(founder_pop.haplotypes, config['pop_size'])
    founder_pop = create_pop(G, founder_pop)

    T = Trait(G, founder_pop, target_mean=config['target_mean'], target_variance=config['target_variance'], seed=seed)
    SP = SimParams(founder_pop,config)


    env_config = {'sparse_reward': config['sparse_reward']}
    env = SelectionIntensityEnvironment(SP, env_config)
#     env = DummyVecEnv([lambda: env])

    return env

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

