import math
import pdb
import scipy.stats as stat

import dataset as ds
import product as pro

#==========================================================================================================================================
# Cluster Class
#==========================================================================================================================================
class Cluster:
    
    """
    Class:     Cluster
    
    Description:
        Wraps around a map of related products and provides various utility functions that facilitate filtering.
        
    Instance Variables:
        
        Commodity commodity:
            Commodity object that contains the commodity information of the Cluster.
        
        Geography geography:
            Geography object that contains the geographic information of the Cluster.
        
        list<int> tpoIDs:
            List of integer identifiers that uniquely identify TargetProductOffer objects stored in the Substituter object.
        
        dict<int, Product> products:
            Collection of Product objects that are within the cluster.
        
        dict<string, set<int>> filterSets:
            A collection of sets of product IDs. Each set is a subset of the products property.
            Key: name of the filter set
            Value: set object containing product IDs.
            
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, commodity, geography):
        self.commodity = commodity
        self.geography = geography
        self.tpoIDs = []
        self.products = {}
        self.filterSets = {}
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # hasDuplicates Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def hasDuplicates(self) -> bool:
        """
        Method:     bool hasDuplicates()
        
        Description: 
            This method checks whether the cluster has any duplicate products.
        
        Output:
            bool
        """
        
        productIDs = list(self.products.keys())
        for i in range(0, len(productIDs)):
            for j in range(i + 1, len(productIDs)):
                if productIDs[i] == productIDs[j]:
                    return True
        return False
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # addUniqueProduct Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def addUniqueProduct(self, productID, unitSize: float, UOM: str, brandType: str, desc: str, periodID: int, outletID: int, unitCount: float, sales: float):
        """
        Method:     void addUniqueProduct
                    (
                        T productID,
                        float unitSize,
                        string UOM,
                        string desc,
                        int periodID,
                        int outletID,
                        float unitCount,
                        float sales
                    )
        
        Description: 
            This method checks whether a Product object with the given product ID already exists. If not, it creates a new Product object.
            Otherwise, it aggregates the given properties with those of the existing object.
        
        Arguments:
            T productID: Unique identifier of the product to be added.
            float unitSize: Volume or mass of a single unit of product.
            string UOM: Unit of measure.
            string desc: Concatenated text features of the product.
            int periodID: Unique identifier of the reference period during which the product was sold.
            int outletID: Unique identifier of the outlet at which the product was sold.
            float unitCount: Number of units sold. 
        """
        
        if productID not in self.products:
            self.products[productID] = pro.Product(productID, UOM, brandType, desc)
        self.products[productID].addProperties(periodID, outletID, unitSize, unitCount, sales)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # removeProduct Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def removeProduct(self, productID):
        """
        Method:     void removeProduct
                    (
                        T productID
                    )
        
        Description: 
            This method removes the product associated with the given product ID from all sets.
            
        Arguments:
            T productID: Unique identifier of the product to be removed.
        """
        
        self.products.pop(productID)
        for setName, filterSet in self.filterSets.items():
            try:
                filterSet.remove(productID)
            except KeyError:
                pass
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # find Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def find(self, comparer = lambda refProd, prod: True, retriever = lambda prod: prod.productID, setName: str = None):
        """
        Method:     T find
                    (
                        bool comparer(Product refProd, Product prod),
                        T retriever<T>(Product prod),
                        string setName
                    )
        
        Description: 
            This method compares all products within the designated set by way of the comparer. It then applies the retriever onto the
            remaining product and returns an object of type T.
            If setName is None, then the method uses the full product set.
            
        Arguments:
            bool comparer(Product refProd, Product prod):
                A callable object that evaluates a boolean expression on two Product objects.
                If it returns True, then prod is assigned to refProd. Otherwise, refProd remains unchanged.
            T retriever<T>(Product prod):
                A callable object that retrieves a property of a Product object.
                The retriever gets the desired property of refProd once the comparer has been applied to every Product object in the
                set. This property is then returned as the output of the method.
            string setName:
                Name of the filter set that the method will consider. If set to None, the method will consider all the products in the
                Cluster.
            
        Output:
            Property of refProd of type T.
        """
        
        if setName == None:
            productIDList = list(self.products.keys())
        else:
            productIDList = list(self.filterSets[setName])
        
        ref = self.products[productIDList[0]]
        for i in range(1, len(productIDList)):
            if comparer(ref, self.products[productIDList[i]]):
                ref = self.products[productIDList[i]]
        
        return retriever(ref)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # addFilterSet Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def addFilterSet(self, name: str):
        """
        Method:     void addFilterSet
                    (
                        string name
                    )
        
        Description: 
            This method adds a filter set with the given name.
            
        Arguments:
            string name: Name of the filter set to be added.
        """
        
        self.filterSets[name] = set(self.products.keys())
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # copyFilterSet Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def copyFilterSet(self, sourceSetName: str, copySetName: str):
        """
        Method:     void copyFilterSet
                    (
                        string sourceSetName,
                        string copySetName
                    )
        
        Description: 
            This method copies the set with the name given by sourceSetName and creates a new set with the name given by copySetName.
            
        Arguments:
            string sourceSetName: Name of the filter set to be copied.
            string copySetName: Name of the filter set to be created.
        """
        
        self.filterSets[copySetName] = set(self.filterSets[sourceSetName])
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # removeFilterSet Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def removeFilterSet(self, name: str):
        """
        Method:     void removeFilterSet
                    (
                        string name
                    )
        
        Description: 
            This method removes the filter set with the given name.
            
        Arguments:
            string name: Name of the filter set to be removed.
        """
        
        self.filterSets.remove(name)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # clearFilterSets Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def clearFilterSets(self):
        """
        Method:     void clearFilterSets()
        
        Description: 
            This method removes all filter sets.
        """
        
        self.filterSets = {}
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # intersectFilterSets Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def intersectFilterSets(self, innerSetName: str, setNames = []):
        """
        Method:     void intersectFilterSets
                    (
                        string interSetName,
                        list<string> setNames
                    )
        
        Description: 
            This method creates a new filter set (name given by innerSetName) that is the intersection of all filter sets given by 
            the names stored in setNames.
            
        Arguments:
            string innerSetName: Name of the intersection filter set to be created.
            list<string> setNames: List of names of the filter sets that will be intersected.
        """
        
        if len(setNames) == 0:
            raise ValueError("Set list is empty.")
        
        firstSetName = setNames.pop(0)
        
        filterSets = []
        for name in setNames:
            filterSets.append(self.filterSets[name])
        
        self.filterSets[innerSetName] = self.filterSets[firstSetName].intersection(*filterSets)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # applyFilterMask Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def applyFilterMask(self, setName: str, productIDSet: set, filterMode: str = 'drop'):
        """
        Method:     void applyFilterMask
                    (
                        string setName,
                        set<T> productIDSet,
                        string filterMode
                    )
        
        Description: 
            This method filters the product IDs stored in the filter set given by setName. If filterMode is set to 'drop', the product IDs 
            in productIDSet are dropped from the set. If filterMode is set to 'keep', then only the product IDs in productIDSet are retained 
            in the set.
            
        Arguments:
            string setName: Name of the set to which the filter mask will be applied.
            set<int> productIDSet: Set of product IDs that will serve as the mask.
            string filterMode: = 'drop' or 'keep'
                Designates the type of mask. If set to 'drop', then all product IDs in productIDSet will be dropped from setName. If
                set to 'keep', then all productIDs not in productIDSet will be dropped from setName.
        """
        
        if filterMode == 'drop':
            self.filterSets[setName] = self.filterSets[setName].difference(productIDSet)
        elif filterMode == 'keep':
            self.filterSets[setName] = set(productIDSet)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # applyFilterFunction Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def applyFilterFunction(self, setName: str, filterer = lambda product: product.properties[0].sales > 0):
        """
        Method:     void applyFilterMask
                    (
                        string setName,
                        bool filterer(Product product)
                    )
        
        Description: 
            This method applies the filterer function to determine whether each product in the set given by setName should be kept 
            or dropped.
            
        Arguments:
            string setName: Name of the filter set on which the filter function will be applied.
            bool filterer(Product product):
                A callable object that applies a boolean expression on product.
                Arguments:
                    Product product: The Product object that is evaluated by the filterer.
        """
        
        keepProductIDs = set()
        for productID in self.filterSets[setName]:
            if filterer(self.products[productID]) == True:
                keepProductIDs.add(productID)
        self.applyFilterMask(setName, keepProductIDs, filterMode = 'keep')
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # applyCutoffFilter Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def applyCutoffFilter(self, 
                          setName: str, 
                          retriever = lambda product: product.properties[0].sales,
                          lowerCutoff: float = 0.5,
                          upperCutoff: float = 1):
        """
        Method:     void applyCutoffFilter
                    (
                        string setName,
                        float retriever(Product product),
                        float lowerCutoff,
                        float upperCutoff
                    )
        
        Description: 
            This method filters out all products with a specific property that is above the given upperCutoff and/or below the given
            lowerCutoff. The getVariable function is applied to retrieve a property of a product.
            
        Arguments:
            string setName: Name of the set on which the cut-off filter will be applied.
            float retriever(Product product):
                A callable object that returns a numeric property of the given Product object.
            float lowerCutoff: Lowest acceptable value for the property being evaluated.
            float upperCutoff: Highest acceptable value for the property being evaluated.
        """
        
        if lowerCutoff != None and upperCutoff != None:
            if upperCutoff < lowerCutoff:
                raise ValueError("The upper cutoff cannot be smaller than the lower cutoff.")
            filterer = lambda product: retriever(product) >= lowerCutoff and retriever(product) <= upperCutoff
        elif lowerCutoff != None:
            filterer = lambda product: retriever(product) >= lowerCutoff
        elif upperCutoff != None:
            filterer = lambda product: retriever(product) <= upperCutoff
        else:
            filterer = lambda product: True
            
        keepProductIDs = set()
        for productID in self.filterSets[setName]:
            try:
                if filterer(self.products[productID]):
                    keepProductIDs.add(productID)
            except Exception:
                pass
                    
        self.applyFilterMask(setName, keepProductIDs, filterMode = 'keep')
     
    #--------------------------------------------------------------------------------------------------------------------------------------
    # addNormalizedVariable Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def addNormalizedVariable(self, 
                              varKey: str,
                              retriever = lambda product: product.properties[0].sales,
                              setName: str = None,
                              normMode: str = 'rank', 
                              invert: bool = False):
        """
        Method:     void addNormalizedvariable
                    (
                        string varKey,
                        float retriever(Product product),
                        string setName,
                        string normMode,
                        bool invert
                    )
        
        Description: 
            This method creates a new normalized variable (called varKey) for each product in the set given by setName. This new variable
            is derived from a product property retrieved by getVariable. It is stored in the variables property of each Product object.
            
            If normMode is set to 'rank', then the normalized variable will be derived from the sorted rank of each product variable.
            If normMode is set to 'magnitude', then the normalized variable will be proportional to the product variable itself.
            If normMode is set to 'weight', then the normalized variable will be proportional to the product variable as well as summing 
            up to 1 across all products in the set.
            
        Arguments:
            string varKey: Name of the normalized variable to be created.
            float retriever(Product product):
                A callable object that retrieves a numeric property of the given Product object.
            string setName: Name of the filter set to be consider. If set to None, then all products in the Cluster will be considered.
            string normMode: = 'rank' or 'magnitude' or 'weight'
                Determines how the variable will be normalized.
            bool invert: If True, then the variable is also inverted.
        """
        
        if setName == None:
            productIDs = list(self.products.keys())
        else:
            productIDs = list(self.filterSets[setName])
        
        count = len(productIDs)
        
        values = []
        
        try:
            
            for i in range(0, count):
                self.products[productIDs[i]].variables[varKey] = 0
                values.append(retriever(self.products[productIDs[i]]))
            
            # Normalize the variable by rank.
            if normMode == 'rank':
                
                ranks = stat.rankdata(values)
                
                for i in range(0, count):
                    
                    if not invert:
                        self.products[productIDs[i]].variables[varKey] = float(ranks[i] / count)
                    
                    if invert:
                        self.products[productIDs[i]].variables[varKey] = float(1 - (ranks[i] - 1) / count)
            
            # Normalize the variable by magnitude.
            elif normMode == 'magnitude':
                
                minValue = min(values)
                maxValue = max(values)
                
                for i in range(0, count):
                    
                    if not invert:
                        self.products[productIDs[i]].variables[varKey] = (values[i] - minValue) / (maxValue - minValue)
                        
                    if invert:
                        self.products[productIDs[i]].variables[varKey] = 1 - ((values[i] - minValue) / (maxValue - minValue))
            
            # Normalize the variable by weight.
            elif normMode == 'weight':
                
                summedValue = sum(values)
                
                for i in range(0, count):
                    
                    if not invert:
                        self.products[productIDs[i]].variables[varKey] = values[i] / summedValue
                        
                    if invert:
                        self.products[productIDs[i]].variables[varKey] = 1 - values[i] / summedValue
                
        except KeyError as e:
            for productID in productIDs:
                self.products[productID].variables[varKey] = 0
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # toFile Method
    #--------------------------------------------------------------------------------------------------------------------------------------  
    def toDataFrame(self, periodID: int, tpoID: int, varLabels: list, setName: str = None):
        
        """
        Method:     DataFrame toDataFrame
                    (
                        int periodID,
                        int tpoID,
                        list<string> varLabels,
                        string setName
                    )
        
        Description: 
            This method generates a DataFrame containing the properties of each product in the cluster during the period 
            given by periodID. A column is created for each label contained in varLabels.
            
        Arguments:
            int periodID: Unique identifier of the reference period to consider when retrieving the properties of the Cluster.
            int tpoID: Unique identifier of the TPO that this cluster is associated with.
            list<string> varLabels: Additional columns to be added to the output. Each varLabel corresponds to a variable in the 
                variables property of each Product object.
        """
        
        if setName == None:
            productIDList = list(self.products.keys())
        else:
            productIDList = list(self.filterSets[setName])
        
        filterLabels = []
        for filterLabel in self.filterSets:
            filterLabels.append(filterLabel)
        
        colLabels = ['TPO_ID', 'ProductID', 'UOM', 'Description', 'Unit Size', 'Quantity Units', 'Sales'] + varLabels + filterLabels
        df = ds.fromDict(colLabels)
        
        for productID in productIDList:
            
            product = self.products[productID]
            
            if periodID in product.properties:
                props = product.properties[periodID]
                
                variables = []
                for varLabel in varLabels:
                    if varLabel in product.variables:
                        variables.append(product.variables[varLabel])
                    else:
                        variables.append(-1)
                        
                filters = []
                for filterLabel in filterLabels:
                    if productID in self.filterSets[filterLabel]:
                        filters.append(1)
                    else:
                        filters.append(0)
                
                ds.addRow(df, [tpoID, productID, product.UOM, product.desc, props.unitSize, props.unitCount, props.sales] + variables + filters)
        
        return df
                
    #--------------------------------------------------------------------------------------------------------------------------------------
    # toString Method
    #--------------------------------------------------------------------------------------------------------------------------------------      
    def toString(self, escChars: str = "\n", limit: bool = True) -> str:
        response =  escChars + "------------------------------"
        response += escChars + "Data type: Product Cluster"
        
        response += escChars + "Geography: " + self.geography.toString(escChars + "\t")
        
        response += escChars + "TPOs in this cluster: " + str(len(self.tpoIDs))
        for i, tpoID in enumerate(self.tpoIDs):
            response += escChars + str(i + 1) + ". " + str(tpoID)
        
        response += escChars + "Products in this cluster: " + str(len(self.products))
        for i, productID in enumerate(self.products):
            response += escChars + "Product " + str(i + 1) + ". " + str(self.products[productID].toString(escChars + "\t", limit))
            if i == 9 and limit:
                response += escChars + "..." 
                break
            
        response += escChars + "Filter sets: " + str(len(self.filterSets))
        for i, setName in enumerate(self.filterSets):
            
            response += escChars + str(i + 1) + ". '" + setName + "' filter set: " + str(len(self.filterSets[setName])) + " product IDs"
            
            for i, productID in enumerate(self.filterSets[setName]):
                response += escChars + "\t" + str(i + 1) + ". " + str(productID)
                if i == 9 and limit:
                    response += escChars + "\t" + "..." 
                    break
        
        response += escChars + "------------------------------"
        return response
        