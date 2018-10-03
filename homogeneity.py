import math
import pandas as pd
import pdb
import re
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import unicodedata as ucd

import product as pro

#------------------------------------------------------------------------------------------------------------------------------------------
# computePriceHomogeneity Method
#------------------------------------------------------------------------------------------------------------------------------------------       
def computePriceHomogeneity(varName: str, refProduct: pro.Product, products: dict):
    
    """
    Method:
        
        void computePriceHomogeneity
        (
            string varName,
            int refProduct,
            dict<int, Product> products
        )
        
    Description:
        Computes a price homogeneity score for each product in the product map.
    
    Arguments
        string varName:
            Name of the variable that will store the price homogeneity score.
        Product refProduct:
            Product that will serve as the reference.
        dict<int, Product> products:
            Map of candidate products.
    """
    
    if len(refProduct) == None:
        raise ValueError("Error: The reference product has not been instantiated.")
    if len(products) == 0:
        raise ValueError("Error: The product map is empty.")
    
    if len(refProduct.properties) > 0:
        periodIDs = list(refProduct.properties.keys())
        refPriceRelatives = {}
        
        for i in range(0, len(periodIDs) - 1):
            if periodIDs[i] + 1 in periodIDs:
                refPriceRelatives[periodIDs[i]] = refProduct.priceRelative(periodIDs[i] + 1, periodIDs[i])
                
    counter = 0
    for productID, product in products.items():
        
        distance = 0
        for periodID in periodIDs:
            if periodID in product.properties and periodID + 1 in product.properties:
                priceRelative = product.priceRelative(periodID + 1, periodID)
                distance += (refPriceRelatives[periodID] - priceRelative) ^ 2
                counter += 1
        
        if counter > 0:
            product.variables[varName] = distance / counter
        else:
            product.variables[varName] = math.inf

#------------------------------------------------------------------------------------------------------------------------------------------
# computeDistance Method
#------------------------------------------------------------------------------------------------------------------------------------------
def computeDistance(varKey: str, reference: pd.Series, products: dict, neighbourCount: int = 10):
    
    """
    Method:
        
        void computeDistance
        (
            string varName,
            Series reference,
            dict<int, Product> products,
            int neighbourCount
        )
        
    Description:
        Computes a distance score for each product in the product map with respect to a reference product. A set number of products, 
        given by the neighbourCount variablem, are assigned a real-number score. Beyond the closest neighbours, all other products in the
        product map are assigned a score of infinity.
    
    Arguments
        string varName:
            Name of the variable that will store the price homogeneity score.
        Series reference:
            Series of concatenated text features.
        dict<int, Product> products:
            Map of candidate products.
        int neighbourCount:
            Number of neighbours to return.
    """
    
    # If the neighbourCount exceeds the size of the product map, then it is readjusted.
    if neighbourCount > len(products):
        neighbourCount = len(products)
    
    # Initialize the transformer
    transformer = make_pipeline(TfidfVectorizer(encoding = "latin-1"))
    
    # Tranform the data
    candidates = list(map(lambda productID: [productID, products[productID]], products))
    candidateKeys = list(map(lambda candidate: candidate[0], candidates))
    candidateFeatures = list(map(lambda candidate: candidate[1].desc, candidates))
    transformedCandidates = transformer.fit_transform(candidateFeatures)
    
    transformedReference = transformer.transform(reference.tolist())
                
    #fit to entire set
    estimator = NearestNeighbors(n_neighbors = neighbourCount)
    estimator.fit(transformedCandidates)
        
    distances, indices = estimator.kneighbors(transformedReference, n_neighbors = neighbourCount)
    
    candidateKeys = pd.Series(candidateKeys)
    candidateKeys = candidateKeys[indices.flatten()].tolist() # 
    
    distances = list(distances.flatten())
    
    #pdb.set_trace()
    
     # Iterate through all products in the product map
    for productID, product in products.items():
        
        # Case 1: The product is among the nearest neighbours.
        if productID in candidateKeys:
            # Assign the actual distance.
            cIndex = candidateKeys.index(productID)
            products[productID].variables[varKey] = distances[cIndex]
            
        # Case 2: The product is not among the nearest neighbours.
        else:
            # Assign a distance of infinity.
            products[productID].variables[varKey] = math.inf
    
#------------------------------------------------------------------------------------------------------------------------------------------
# computeWordSimilarity Method
#------------------------------------------------------------------------------------------------------------------------------------------
def computeWordSimilarity(subSentence: str, sentence: str, delimiters: str = '\s') -> float:
    
    """
    Method:
        
        void computeWordSimilarity
        (
            string subSentence,
            string sentence,
            string delimiters
        )
        
    Description:
        Computes a word similarity score between a string and a substring. The presence of each word in the substring is checked in the main
        string. A score of 1 is given if all words are present. A score of 0 is given if none of the words are present.
    
    Arguments
        string subSentence:
            String of words separated by delimiters.
        string sentence:
            String of words.
        string delimiters:
            String of one or more delimiting characters. Separate each delimitor with a '|'.
    """
    
    # Normalize the sub-string and the main string
    subSentence = ucd.normalize("NFKD", subSentence.casefold())
    sentence = ucd.normalize("NFKD", sentence.casefold())
    
    # Split the sib-string into words
    words = re.split(delimiters, subSentence)
    
    # Check whether each word is present in the main string
    score = 0.0
    for word in words:
        if word in sentence:
            score += 1
    return score / len(words)