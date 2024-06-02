# burbankai


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

A pytorch software for simulating breeding programs. With GPU.

## Install

``` sh
pip install burbankai
```

## How to use

First, define the genome of your crop

``` python
ploidy = 2
number_chromosomes = 10
loci_per_chromosome = 100
n_founders = 50
```

We will create a generic genetic map where each loci is 1 cM apart from
the next loci.

``` python
genetic_map = create_uniform_genetic_map(number_chromosomes,loci_per_chromosome)
```

Now we can define the Genome for the simulation.

``` python
crop_genome = Genome(ploidy, number_chromosomes, loci_per_chromosome, genetic_map)
```

Next we will generate randomized founders.

``` python
founder_pop = create_random_founder_pop(crop_genome , n_founders)
print(founder_pop.shape)
```

    torch.Size([50, 2, 10, 100])
