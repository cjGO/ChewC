# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_core.ipynb.

# %% auto 0
__all__ = ['Genome', 'Individual', 'Population', 'SimParam', 'create_uniform_genetic_map', 'create_random_genetic_map',
           'create_random_founder_pop']

# %% ../nbs/01_core.ipynb 4
import attr
import torch
from fastcore.test import *
from typing import List, Tuple, Union, Callable, Optional

# %% ../nbs/01_core.ipynb 6
@attr.s(auto_attribs=True)
class Genome:
    """
    Used for defining the genomic architecture for the simulation. 
    It will be used as an argument for breeding program operations.
    
    Args:
        ploidy (int): Ploidy level (assuming autopolyploid).
        number_chromosomes (int): Total number of chromosomes in the karyotype/genome.
        loci_per_chromosome (int): The number of loci which are genotyped on each chromosome (e.g., a SNP chip).
        genetic_map (torch.Tensor): A 2D tensor representing the genetic map. 
                                     Shape: (number_chromosomes, loci_per_chromosome). 
                                     Each row represents a chromosome, and each element in a row is the genetic 
                                     location (in cM) of a locus.
    """
    ploidy: int
    number_chromosomes: int
    loci_per_chromosome: int
    genetic_map: torch.Tensor
    shape: torch.Tensor
        
    def shape(self):
        return self.ploidy, self.number_chromosomes, self.loci_per_chromosome

    def __attrs_post_init__(self):
        """
        Validate the input parameters after initialization.
        """
        # Check if the genetic map dimensions are compatible
        if not self.genetic_map.shape == (self.number_chromosomes, self.loci_per_chromosome):
            raise ValueError(f"Genetic map shape {self.genetic_map.shape} is incompatible with the number of chromosomes and loci per chromosome.")

#         # Check if the genetic map is valid (starts at 0 and is increasing)
#         for chrom_map in self.genetic_map:
#             if not (chrom_map[0] == 0.0 and all(x < y for x, y in zip(chrom_map, chrom_map[1:]))):
#                 raise ValueError("The genetic map must start at 0 and be strictly increasing for each chromosome.")
                
#                         # Set the shape attribute
        self.shape = (self.ploidy, self.number_chromosomes, self.loci_per_chromosome)



# %% ../nbs/01_core.ipynb 7
@attr.s(auto_attribs=True)
class Individual:
    """
    Represents an individual in the breeding simulation.

    Args:
        genome (Genome): Reference to the shared Genome object.
        haplotypes (torch.Tensor): Tensor representing the individual's haplotypes. 
                                    Shape: (number_chromosomes, ploidy, number_loci).
        id (Optional[str]): Unique identifier. Defaults to None.
        mother_id (Optional[str]): Mother's identifier. Defaults to None.
        father_id (Optional[str]): Father's identifier. Defaults to None.
        genetic_value (Optional[torch.Tensor]): Genetic value for traits. Shape: (number_traits,). Defaults to None.
        phenotype (Optional[torch.Tensor]): Phenotype for traits. Shape: (number_traits,). Defaults to None.
    """
    genome: Genome
    haplotypes: torch.Tensor # haplotypes.shape == genome.genetic_map.shape
    id: Optional[str] = None
    mother_id: Optional[str] = None
    father_id: Optional[str] = None
    genetic_value: Optional[torch.Tensor] = None
    phenotype: Optional[torch.Tensor] = None

    def __attrs_post_init__(self):
        """
        Validate the input parameters after initialization.
        """
        # make sure the haplotype and given genetic map are compatible. 
        if not self.haplotypes.shape == self.genome.gentic_map.shape:
            raise ValueError(f"Haplotype shape {self.haplotypes.shape[1:]} is incompatible with the genome {self.genome.genetic_map.shape}.")
        

# %% ../nbs/01_core.ipynb 8
@attr.s(auto_attribs=True)
class Population:
    """
    Represents a population of individuals.

    Args:
        individuals (List[Individual]): List of Individual objects in the population.
        id (Optional[str]): Unique identifier for the population. Defaults to None.
    """
    individuals: List[Individual]
    id: Optional[str] = None

# %% ../nbs/01_core.ipynb 9
@attr.s(auto_attribs=True)
class SimParam:
    founder_pop = None
    genome = None
    traits = None
    device = 'cpu'

# %% ../nbs/01_core.ipynb 12
def create_uniform_genetic_map(number_chromosomes: int, loci_per_chromosome: int, chromosome_length: float = 100.0) -> torch.Tensor:
    """
    Creates a uniform genetic map with equally spaced loci on each chromosome.

    Args:
        number_chromosomes (int): Number of chromosomes.
        loci_per_chromosome (int): Number of loci per chromosome.
        chromosome_length (float): Genetic length of each chromosome in centimorgans (cM). Defaults to 100.0 cM.

    Returns:
        torch.Tensor: 2D tensor representing the genetic map (shape: (number_chromosomes, loci_per_chromosome)).
    """
    return torch.arange(0, chromosome_length, chromosome_length / loci_per_chromosome).repeat(number_chromosomes, 1)


def create_random_genetic_map(number_chromosomes: int, loci_per_chromosome: int, chromosome_length: float = 100.0, device: str = 'cpu') -> torch.Tensor:
    """
    Creates a random genetic map with loci positions that gradually increase randomly on each chromosome.

    Args:
        number_chromosomes (int): Number of chromosomes.
        loci_per_chromosome (int): Number of loci per chromosome.
        chromosome_length (float): Maximum genetic length of each chromosome in centimorgans (cM). Defaults to 100.0 cM.
        device (str): Device to create the tensor on ('cpu' or 'cuda'). Defaults to 'cpu'.

    Returns:
        torch.Tensor: 2D tensor representing the genetic map (shape: (number_chromosomes, loci_per_chromosome)).
    """
    genetic_map = torch.zeros((number_chromosomes, loci_per_chromosome), device=device)

    for chr_idx in range(number_chromosomes):
        random_positions = torch.sort(torch.rand(loci_per_chromosome-1, device=device) * chromosome_length).values
        genetic_map[chr_idx, 1:] = random_positions    
    return genetic_map


def create_random_founder_pop(genome: Genome, n_founders: int, device: str = 'cpu') -> torch.Tensor:
    """
    Creates a tensor of random haplotypes for multiple founder individuals based on the provided genome.

    Args:
        genome (Genome): The genome defining the structure of the haplotypes.
        n_founders (int): The number of founder individuals to create haplotypes for.
        device (str): Device to create the tensor on ('cpu' or 'cuda'). Defaults to 'cpu'.

    Returns:
        torch.Tensor: A tensor of random 0's and 1's representing haplotypes.
                         Shape: (n_founders, ploidy, number_chromosomes, loci_per_chromosome)
    """
    return torch.randint(0, 2, (n_founders, genome.ploidy, genome.number_chromosomes, genome.loci_per_chromosome), device=device)

