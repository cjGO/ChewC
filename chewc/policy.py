# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_Policy.ipynb.

# %% auto 0
__all__ = ['CustomFeatureExtractor', 'CustomNetwork', 'CustomActorCriticPolicy']

# %% ../nbs/03_Policy.ipynb 1
import torch
import torch.nn as nn
from gymnasium import spaces
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from typing import Tuple, Callable
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback

class CustomFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: spaces.Dict):
        super().__init__(observation_space, features_dim=64)
        
        pop_shape = observation_space.spaces["population"].shape
        self.pop_extractor = nn.Sequential(
            nn.Flatten(),
            nn.Linear(pop_shape[0] * pop_shape[1] * pop_shape[2] * pop_shape[3], 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        
        self.gen_extractor = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU()
        )
        
        self.combined = nn.Sequential(
            nn.Linear(80, 64),
            nn.ReLU()
        )

    def forward(self, observations) -> torch.Tensor:
        pop_features = self.pop_extractor(observations["population"])
        gen_features = self.gen_extractor(observations["generation"])
        combined = torch.cat([pop_features, gen_features], dim=1)
        return self.combined(combined)

class CustomNetwork(nn.Module):
    def __init__(self, feature_dim: int, last_layer_dim_pi: int = 64, last_layer_dim_vf: int = 64):
        super().__init__()
        self.latent_dim_pi = last_layer_dim_pi
        self.latent_dim_vf = last_layer_dim_vf
        
        self.policy_net = nn.Sequential(
            nn.Linear(feature_dim, last_layer_dim_pi),
            nn.ReLU()
        )
        
        self.value_net = nn.Sequential(
            nn.Linear(feature_dim, last_layer_dim_vf),
            nn.ReLU()
        )

    def forward(self, features: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.forward_actor(features), self.forward_critic(features)

    def forward_actor(self, features: torch.Tensor) -> torch.Tensor:
        return self.policy_net(features)

    def forward_critic(self, features: torch.Tensor) -> torch.Tensor:
        return self.value_net(features)

class CustomActorCriticPolicy(ActorCriticPolicy):
    def __init__(
        self,
        observation_space: spaces.Space,
        action_space: spaces.Space,
        lr_schedule: Callable[[float], float],
        *args,
        **kwargs,
    ):
        kwargs["features_extractor_class"] = CustomFeatureExtractor
        super().__init__(
            observation_space,
            action_space,
            lr_schedule,
            *args,
            **kwargs,
        )

    def _build_mlp_extractor(self) -> None:
        self.mlp_extractor = CustomNetwork(self.features_dim)