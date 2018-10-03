import math
import numpy as np
import pdb

#==========================================================================================================================================
# SamplingError Class
#==========================================================================================================================================
class SamplingError(Exception):
    def __init__(self, message: str, samplingMode: str, innerSetCount: int, outerSetCount: int):
        
        prompt = "\nSampling Error: " + message
        prompt += "\n\tSampling Strategy: " + samplingMode
        prompt += "\n\tInner Set: " +  str(innerSetCount)
        prompt += "\n\tOuter Set: " + str(outerSetCount)
        
        super(SamplingError, self).__init__(prompt)
        
#------------------------------------------------------------------------------------------------------------------------------------------
# sample Method
#------------------------------------------------------------------------------------------------------------------------------------------
def sample(population: dict, innerSet: set, outerSet: set, getProbability, samplingStrategy: str = '', sampleSize: int = 1) -> list:
    """  
    Method:   
        
        list<T> sample
        (
            dict<T, S> population,
            set<T> innerSet,
            set<T> outerSet
            Function:   float getProbability(S item),
            string samplingMode,
            int sampleSize
        )
    
    Description: 
        This method generates a random sample of items of type S from a population. The inner and outer sets are subsets of the population, 
        and can be used to narrow the pool of candididate items. A list of keys of type T is returned.
        Five sampling strategies can be selected from:
            (1) Cut-off: 
                    All items in the inner set of the population are assigned an inclusion probability of 1. All items outside of 
                    the inner set but inside the outer set are assigned an inclusion probability of 0.
            (2) Proportional:
                    All items are assigned an inclusion probability via the getProbability function.
            (3) Top Proportional:
                    All items in the inner set of the population are assigned an inclusion probability via the getProbability function. 
                    All items outside of the inner set but inside the outer set are assigned an inclusion probability of 0.
            (4) Random: 
                    All items in the population are assigned an inclusion probability of 1. Default strategy.
             
    Arguments:
        dict<T, S> population:
            A dictionary mapping generic items of type S to unique keys of type T.
        set<T> innerSet:
            Set of item IDs belonging to the population. The inner set is a subset of the outer set.
        set<T> outerSet:
            Set of item IDs belonging to the population.
        Function:   float getProbability(S item):
            A function that accepts a generic item of type S and returns a floating point inclusion probability.
        string samplingStrategy:
            A string flag that describes what sampling strategy is to be applied.
            Values:
                := 'cutoff' : applies the cut-off sampling strategy
                := 'proportional' : applies the proportional sampling strategy
                := 'top_proportional' : applies the top proportional strategy
        int sampleSize:
           Size of the sample. 
        
    Output:
        list<T>
    """
      
    # If the population size is empty, raise a Sampling Error
    if len(population) == 0:
        pdb.set_trace()
        raise SamplingError("The population dict is empty.", samplingStrategy, len(innerSet), len(outerSet))
    
    # Apply the chosen sampling strategy to construct a subpopulation and a probability vector
    
    # Case 1: Cut-off sampling.
    if samplingStrategy == 'cutoff':
        subPopulation = list(innerSet)
        probabilities = None
        
    # Case 2: Proportional sampling.
    elif samplingStrategy == 'proportional':
        # innerSet|outerSet returns the union of the inner set and the outer set
        subPopulation, probabilities = proportionalSampling(population, innerSet|outerSet, getProbability)
    
    # Case 3: Top proportional sampling.
    elif samplingStrategy == 'top_proportional':
        subPopulation, probabilities = proportionalSampling(population, innerSet, getProbability)
    
    # Case 4: Random sampling.
    else:
        subPopulation = list(outerSet)
        probabilities = None
        
    # If the subpopulation size is empty, raise a Sampling Error
    if len(subPopulation) == 0:
        raise SamplingError("The sub-population is empty.", samplingStrategy, len(innerSet), len(outerSet))
    
    # Case 1: The probability vector is empty.
    if probabilities == None:
        # All items are given an equal inclusion probability.
        sampleArray = np.random.choice(subPopulation, sampleSize)
    
    # Case 2: The probability vector is not empty.
    else:
        try:
            
            # Normalize the probability vector such that the sum of the vector's elements is 1
            pSum = sum(probabilities)
            
            # Case 2.1: The sum of all elements is 0 or is infinity.
            if pSum == 0 or pSum == math.inf:
                 # All items are given an equal inclusion probability.
                weight = 1 / len(subPopulation)
                probabilities = [weight for a in range(len(subPopulation))]
            
            # Case 2.2: The sum of all elements is a non-zero real number.
            else:
                probabilities = list(map(lambda x: x / pSum, probabilities))
            
            # Construct a random sample of items
            sampleArray = np.random.choice(subPopulation, sampleSize, p=probabilities)
            
        except ZeroDivisionError as e:
            pdb.set_trace()
        
    return list(sampleArray)
       
#------------------------------------------------------------------------------------------------------------------------------------------
# proportionalSampling Method
#------------------------------------------------------------------------------------------------------------------------------------------ 
def proportionalSampling(population: dict, itemSet: set, getProbability) -> tuple:
    
    """
    Method:
        
        tuple<list<T>, list<float>> cutoffSampling
        (
            dict<T, S> population,
            set<T> innerSet,
            Function:   float getProbability(S item) 
        )
        
    Description:
        Assigns an inclusion probability to all items in the set via the getProbability function.
    
    Arguments
        dict<T, S> population:
            A dictionary of generic items of type S mapped to keys of type T.
        set<T> itemSet:
            A set of item keys of type T.
        Function:   float getProbability(S item)
        
    Output:
        tuple<list<T>, list<float>> { subPopulation, probabilities }
            subPopulation: A list of item keys of type T
            probabilities: A list of floating point probabilities
    """
    
    subPopulation = []
    probabilities = []
    
    for ID in itemSet:
        subPopulation.append(ID)
        probabilities.append(getProbability(population[ID]))
    
    return subPopulation, probabilities