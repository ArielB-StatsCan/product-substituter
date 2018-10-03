### Import external libraries ###
import numpy as np
import pandas as pd
import pdb

### Import project files ###
import dataset as ds
import cluster as clu
import commodity as com
import geography as geo
import homogeneity as hom
import sampling as sam
import targetproductoffer as tpro
import timer as tim

#==========================================================================================================================================
# Substituter Class
#==========================================================================================================================================
class Substituter():
    
    """
    Class:     Substituter
    
    Description:
        Assigns product IDs to unmatched TPOs.
        
    Instance Variables:
        DataFrame productData:
            Lists all of the sales of the past n months.
        DataFrame productDescData:
            Contains the constant properties of every product since period 0. Includes the commodity class ID, the product description, 
            the retailer hierarchy and the unit of measure.
        DataFrame outletData:
            Describes all outlets within the sample at each period.
        DataFrame tpoMatchedData:
            Contains a dataframe where each row corresponds to a previously-unassigned TPO that was assigned a substitute product. This 
            dataframe serves as the output of the algorithm and is converted into a .csv file at the end.
        DataFrame suggestionsData:
            Contains all possible candidates for each substituted TPO.
        DataFrame summary:
            Contains various summary statistics.
        dict<int, Commodity> comMap:
            A map of Commodity objects.
                Key := commodity class ID
                Value := Commodity object
        dict<int, Commodity> tpoMap:
            A map of TargetProductOffer objects.
                Key := TPO ID
                Value := TargetProductOffer object
        int unclassifiedCount:
            Number of TPOs with previous product IDs that are unclassified.
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, productDescData: pd.DataFrame, productSalesDataSets: dict = None, outletDataSets: dict = None):
        
        """
        Constructor:
            
            Substituter
            ( 
                DataFrame prodDescData
            )
        
        Description:
            Constructs a Substituter object.
        
        Arguments:
            DataFrame productDescData: 
                 A pandas DataFrame describing each unique product. The following columns are obligatory:
                     'ProductID': Unique integer identifier of a product.
                     'CommodityID': Unique integer identifier of a commodity class; i.e. the EA column in UATfalk.Loblaws_fct_UniqueProdDesc. 
        """
        
        print('\n\nInitializing substituter ...')
        
        # Constants
        self.productIDKey = 'ProductID'
        self.tpoIDKey = 'TPO_ID'
        self.rpNameKey = 'RPName'
        self.statusIDKey = 'StatusID'
        self.periodIDKey = 'PeriodID'
        self.commodityIDKey = 'CommodityID'
        self.provinceKey = 'Province'
        self.cityKey = 'City'
        self.outletIDKey = 'OutletID'
        self.retailerSiteIDKey = 'SiteID'
        self.uomKey = 'StdUOM'
        self.brandTypeKey = 'BrandType'
        self.salesKey = 'Sales'
        self.unitCountKey = 'QtyUnits'
        
        # Instance Variables
        
        self.unclassifiedCount = 0
        
        self.comMap = {}
        self.tpoMap = {}        
        
        self.productData = None
        self.productDescData = productDescData
        self.outletData = None
        self.tpoMatchedData = None
        self.suggestionsData = None
        self.summary = ds.fromDict([self.periodIDKey, 'Commodity Count', 'Cluster Count', 'Outlet Count', 'TPO Count', 'Assigned Count', 'Unclassified Count', 'Fraction Assigned', 'Average Similarity', 'Brand Matching'])
        
        self.productDescData = ds.convertAllColumns(self.productDescData, str, exclude=[self.productIDKey, self.commodityIDKey])
        
        if productSalesDataSets is not None and outletDataSets is not None:
            self.assignSample(productSalesDataSets, outletDataSets)
        
    #--------------------------------------------------------------------------------------------------------------------------------------
    # assignSalesDataSet Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def assignSample(self, salesDataSets: dict, outletDataSets: dict):
        
        """
        Method:
            
            void assignSalesDataSet
            ( 
                dict<int, DataFrame> salesDataSets, 
                dict<int, DataFrame> outletDaatSets
            )
        
        Description:
            Assigns one or more DataFrame objects to the product DataFrame of the Substituter. If multiple DataFrames are given, they 
            are appended together.
            Assigns one or more DataFrame objects to the outlets DataFrame of the Substituter. If multiple DataFrames are given, they 
            are merged together.
        
        Arguments:
            dict<int, DataFrame> salesDataSets
                 A dictionary of DataFrame objects describing the monthly sales of all outlets within the sample over a given 
                 time frame. The following columns are obligatory:
                     'ProductID': Unique integer identifier of a product.
                     'SiteID': Unique integer identifier of an outlet; i.e. Retailer Oulet ID.
                     'PeriodID': Unique integer identifier that denotes the period (i.e. month) of the sales.
                     'QtyUnits': Floating point value describing the number of units sold over the course of the period.
                     'Sales': Floating point value describing the amount of revenue that was collected over the course of the period.
            dict<int, DataFrame> outletsDataSets
                 A dictionary of DataFrame objects describing the outlets within the sample over a given time frame. The following columns 
                 are obligatory:
                     'OutletID': Unique integer identifier of an outlet; i.e. Phoenix Outlet ID.
                     'SiteID': Unique integer identifier of an outlet; i.e. Retailer Outlet ID.
        """
        
        periodIDs = list(outletDataSets.keys())
        b = periodIDs[0]
        
        self.outletData = outletDataSets[b]
        self.outletData = self.outletData.rename(columns={self.retailerSiteIDKey:self.retailerSiteIDKey + '_' + str(b)})
        
        for i in outletDataSets:
            if i != b:                
                union = self.outletData.merge(outletDataSets[i][[self.outletIDKey, self.retailerSiteIDKey]], how='outer', on=self.outletIDKey)
                self.outletData = union.rename(columns={self.retailerSiteIDKey:self.retailerSiteIDKey + '_' + str(i)})
        
        for i, periodID in enumerate(salesDataSets):
            
            salesDF = salesDataSets[periodID].merge(outletDataSets[periodID][[self.outletIDKey, self.retailerSiteIDKey]], how='left', on=self.retailerSiteIDKey)
            
            if i == 0:
                self.productData = salesDF
            else:
                self.productData = self.productData.append(salesDF)  
        
        descriptions = self.productDescData[[self.productIDKey, self.commodityIDKey, self.uomKey, self.brandTypeKey]]
        features = self.productDescData.drop(columns = [self.productIDKey, self.commodityIDKey])
        features = features.fillna('')
        descriptions['Desc'] = features.iloc[:,:].apply(lambda x: ' '.join(x), axis=1)
        self.productData = self.productData.merge(descriptions, how='left', on=self.productIDKey)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # assignSalesDataSet Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def initOutput(self):
        
        """
        Method:
            
            void initOutput()
        
        Description:
            Initializes the tpoMatchedData dataframe.
        """
        
        self.tpoMatchedData = ds.fromDict([self.commodityIDKey,
                                           self.tpoIDKey, self.rpNameKey, self.outletIDKey,
                                           'Prev' + self.productIDKey, 'PrevDesc', 'Prev' + self.brandTypeKey,
                                           self.productIDKey, 'Desc', self.brandTypeKey,
                                           'ClusterTotal', 'CurrentTotal', 'OutletTotal',
                                           'SoldAtSite', 'InCommodity', 'NormQuantity', 'PriceHomoScore', 'Distance', 'WordSimilarity',
                                           self.statusIDKey, 'Status'])
        
        self.suggestionsData = None
        
    #--------------------------------------------------------------------------------------------------------------------------------------
    # substitute Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def substitute(self,
                   tpoData: pd.DataFrame,
                   currentPeriodID: int,
                   geoAggKey: str = 'City',
                   lowerQuantityCutoff: float = 0.5,
                   upperQuantityCutoff: float = 1,
                   neighbourCount: int = None,
                   relaunchDistanceCutoff: float = 0,
                   lowerDistanceCutoff: float = 0.5,
                   upperDistanceCutoff: float = 1,
                   samplingStrategy: str = 'cutoff',
                   tpoMatchedFilePath: str = 'C:\\tposMatched.csv',
                   details: bool = False,
                   suggestionsFilePath: str = 'C:\\suggestions.csv',
                   suggest: bool = True,
                   summaryFilePath: str = 'C:\\summary.csv'):
        
        """  
        Method:     void substitute
                    (
                        DataFrame tpoData,
                        int currentPeriodID,
                        string geoAggKey,
                        float lowerQuantityCutoff,
                        float upperQuantityCutoff,
                        int neighbourCount,
                        float relaunchDistanceCutoff,
                        float lowerDistanceCutoff,
                        float upperDistanceCutoff,
                        string samplingStrategy,
                        string tpoMatchedFilePath,
                        bool details,
                        string suggestionsFilePath,
                        bool suggest,
                        string summaryFilePath
                    )
        
        Description: 
            Attempts to assign substitute product IDs to all unmatched TPOs. 
             
        Arguments:
            DataFrame tpoData:
                 A DataFrame object with the following obligatory columns:
                     'TPO_ID': Unique integer identifier of the TPO; i.e. Phoenix TPO ID.
                     'RPName': String object that contains the name of the corresponding RPs.
                     'OutletID': Unique integer identifier of the outlet desscribed by the TPO; i.e. Phoenix Outlet ID.
                     'PeriodID': Unique integer identifier of the reference period.
                     'StatusID': Integer flag; see targetproductoffer.py for more information.
                     'ProductID': Unique integer identifier of the product assigned to the TPO.
            int currentPeriodID:
                Unique identifier of the reference period to be considered.
            string geoAggKey: = 'Province' or 'City' or 'OutletID'
                Determines at what level the geographic aggregation will occur.
            float lowerQuantityCutoff:
                Lowest acceptable quantity of a candidate product.
            float upperQuantityCutoff:
                Highest accetable quantity of a candidate product.
            int neighbourCount:
                Number of closest candidate products that will flagged for each missing product. Serves as an upper limit on the number
                of candidates to be considered.
            float relaunchDistanceCutoff:
                Highest acceptable distance for a potential relaunched product.
            float lowerDistanceCutoff:
                Lowest acceptable normalized and inverted distance score for a candidate product
            float uppperDistanceCutoff:
                Highest acceptable normalized and inverted distance score for a candidate product
            string samplingStrategy:
                Key of the sampling strategy to be used to select the final substitute from among a pool of suitable candidates.
                Keys:
                    'random' (default)
                    'cutoff'
                    'proportional'
                    'top_proportional'
            string tpoMatchedFilePath:
                Location at which the matched TPO file is created.
            bool details:
                True if additional columns are to be populated in the tpoMatchedData file. False if only the TPO ID, the status ID,
                and the newly-assigned product ID are to be displayed in the tpoMatchedData file.
            string suggestionsFilePath:
                Location at which the suggestions file is created.
            bool suggest:
                True if a list of suggestions is to be generated for each substitution.
            string summaryFilePath:
                Location at which the summary file is created.
        """
        
        # Setup the tpoMatchedData dataframe
        self.initOutput()
        
        # Build commodity and TPO maps
        #----------------------------------------------------------------------------------------------------------------------------------
        self.buildMaps(tpoData, currentPeriodID)
        
        # Iterate over commodity classes
        #----------------------------------------------------------------------------------------------------------------------------------
        comCounter = 0
        cluCounter = 0
        tpoCounter = 0
        outletSet = set()
        assignedCounter = 0
        for comID, commodity in self.comMap.items():
            
            if commodity.containsUnassignedTPOs(self.tpoMap, currentPeriodID):
                
                comCounter += 1
                print("\n\nCommodity " + str(comCounter) + ": " + str(comID))
                
                # Aggregate by geography
                #--------------------------------------------------------------------------------------------------------------------------
                clusters = self.buildClusterList(commodity, currentPeriodID, geoAggKey)
                for cluster in clusters:
                    # Populate the cluster with all products within the commodity class and the geographic class
                    self.populateCluster(cluster)
                
                # Remove absent products
                #--------------------------------------------------------------------------------------------------------------------------
                for cluster in clusters:
                    removeProductIDs = []
                    for productID, product in cluster.products.items():
                        # Check whether product was sold during the current period
                        if not product.isPresent(currentPeriodID):
                            removeProductIDs.append(productID)
                    # Remove all products not sold during the current period
                    for productID in removeProductIDs:
                        cluster.removeProduct(productID)
                
                # Iterate over clusters
                #--------------------------------------------------------------------------------------------------------------------------
                for cluster in clusters:
                    
                    cluCounter += 1
                    
                    # Iterate over all TPOs
                    for i, tpoID in enumerate(cluster.tpoIDs):
                        
                        tpo = self.tpoMap[tpoID]
                        if not tpo.isAssigned(currentPeriodID):
                            
                            tpoCounter += 1
                            outletSet.add(tpo.outletID)
                            
                            # Try to assign a new productID to the TPO
                            status = self.assignTPO(cluster, 
                                                    tpo,
                                                    currentPeriodID,
                                                    geoAggKey,
                                                    lowerQuantityCutoff,
                                                    upperQuantityCutoff,
                                                    neighbourCount,
                                                    relaunchDistanceCutoff,
                                                    lowerDistanceCutoff,
                                                    upperDistanceCutoff,
                                                    samplingStrategy)
                            
                            if suggest and tpo.properties[currentPeriodID].statusID == 2:
                                
                                cluster.products[tpo.properties[currentPeriodID].productID].variables['selected'] = 1
                                suggestions = cluster.toDataFrame(currentPeriodID, 
                                                                  tpo.ID,
                                                                  ['distance', self.salesKey, 'similarity', 'normDistance', 'selected'],
                                                                  'OUTLET')
                            
                                if self.suggestionsData is None:
                                    self.suggestionsData = suggestions
                                else:
                                    self.suggestionsData = ds.appendDataSet(self.suggestionsData, suggestions)
                            
                            print("\nTPO " + str(tpoCounter) + ": " + str(tpo.ID) + " - " + status)
                            
                            if status == 'ASSIGNED' or status == 'RELAUNCH':
                                assignedCounter += 1
                            
                            # Append a new row to the tpoMatchedData dataframe
                            self.appendResult(tpo, currentPeriodID, status, cluster)
        
        # Compute Brand Matching Score
        #----------------------------------------------------------------------------------------------------------------------------------
        tpoPeriodData = tpoData.loc[tpoData[self.periodIDKey] == currentPeriodID]
        dupRPData = tpoPeriodData.loc[(tpoPeriodData[self.rpNameKey].str.contains("1")) | (tpoPeriodData[self.rpNameKey].str.contains("2"))]
        dupRPData = dupRPData.merge(self.tpoMatchedData[[self.tpoIDKey, self.statusIDKey, self.productIDKey]], how='left', on=self.tpoIDKey, suffixes=('', '_s'))
        dupRPData = dupRPData.dropna(subset=[self.productIDKey + '_s'])
        dupRPData = dupRPData.loc[dupRPData['StatusID_s'] == 2]
        dupRPData = dupRPData.merge(self.productDescData[[self.productIDKey, self.brandTypeKey]], how='left', on=self.productIDKey)
        dupRPData = dupRPData.merge(self.productDescData[[self.productIDKey, self.brandTypeKey]], how='left', left_on=self.productIDKey+'_s', right_on=self.productIDKey, suffixes=('', '_s'))
        dupRPData['Match'] = np.where(dupRPData[self.brandTypeKey] == dupRPData[self.brandTypeKey+'_s'], 1, 0)
        
        brandMatching = sum(dupRPData['Match']) / len(dupRPData)
        
        # Generate Matched TPO File
        #----------------------------------------------------------------------------------------------------------------------------------
        if details == True:
            ds.generateFile(self.tpoMatchedData, tpoMatchedFilePath)
        else:
            ds.generateFile(self.tpoMatchedData[[self.tpoIDKey, self.productIDKey, self.statusIDKey]], tpoMatchedFilePath)
        
        # Generate Suggestions File
        #----------------------------------------------------------------------------------------------------------------------------------
        if self.suggestionsData is not None:
            ds.generateFile(self.suggestionsData, suggestionsFilePath)
        
        # Generate Summary File
        #----------------------------------------------------------------------------------------------------------------------------------
        print("\nSummary: Period " + str(currentPeriodID))
        print("------------------------------")
        print("Number of Commodities: " + str(comCounter))
        print("Number of Clusters: " + str(cluCounter))
        print("Number of Sites: " + str(len(outletSet)))
        print("Number of TPOs: " + str(tpoCounter))
        print("Number of Assigned TPOs: " + str(assignedCounter))
        print("Brand Matching Score: " + str(brandMatching))
        
        assignedDF = self.tpoMatchedData.loc[self.tpoMatchedData[self.statusIDKey] != 3]
        
        if len(assignedDF) > 0:
            similScore = sum(assignedDF['WordSimilarity']) / len(assignedDF['WordSimilarity'])
        else:
            similScore = 0
        
        assignedFraction = 0
        if tpoCounter != 0:
            assignedFraction = assignedCounter / tpoCounter
        
        summaryVars = [currentPeriodID, 
                       comCounter, 
                       cluCounter, 
                       len(outletSet), 
                       tpoCounter, 
                       assignedCounter, 
                       self.unclassifiedCount,
                       assignedFraction,
                       similScore,
                       brandMatching]
        ds.addRow(self.summary, summaryVars)
        ds.generateFile(self.summary, summaryFilePath)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # buildMaps Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def buildMaps(self, tpoData: pd.DataFrame, periodID: int) -> dict:
        
        """  
        Method:     void buildMaps
                    (
                        DataFrame tpoData
                    )
        
        Description: 
            Constructs a dictionary of Commodity objects and a dictionary of TargetProductOffer objects. A Commodity object is only 
            constructed under the following conditions:
                (1) The commodity class contains at least one unassigned TPO (i.e. statusID = 0);
                (2) A Commodity object has yet to be constructed for the commodity class.
            For each unassigned TPO, a TargetProductOffer object is created and mapped to the corresponding Commodity object.
            TargetProductOffer objects are also created for all assigned TPOs belonging to a commodity class with at least one unassigned TPO.
            
        Arguments:
            DataFrame tpoData:
                 A DataFrame containing the following obligatory columns:
                     'TPO_ID': Unique integer identifier of the TPO; i.e. Phoenix TPO ID.
                     'OutletID': Unique integer identifier of the outlet desscribed by the TPO; i.e. Phoenix Outlet ID.
                     'StatusID': Integer flag; see targetproductoffer.py for more information.
                     'ProductID': Unique integer identifier of the product assigned to the TPO; see targetproductoffer.py for more information.
            int periodID: Unique integer identifier denoting the current referenc period.
        """
        
        # Clean Up the TPO DataFrame
        #----------------------------------------------------------------------------------------------------------------------------------
        print('\n\nCleaning up raw TPO data ...')
        
        # Map a commodity class to each TPO
        if self.commodityIDKey not in tpoData.columns:
            tpoData = tpoData.merge(self.productDescData[[self.productIDKey, self.commodityIDKey]], how='left', on=self.productIDKey)
            
        # Map a city and a province to each TPO
        if self.cityKey not in tpoData.columns:
            tpoData = tpoData.merge(self.outletData[[self.outletIDKey, self.cityKey, self.provinceKey]], how='left', on=self.outletIDKey)
        
        # Identify any TPOs without a commodity mapping, and then attempt to complete the mapping through its associated RP
        # If the product description data set is complete, this step should not be necessary.
        recipientComDF = tpoData.loc[tpoData[self.commodityIDKey].isnull()]
        for row in recipientComDF.itertuples():
            rpName = str(getattr(row, self.rpNameKey))
            donorComDF = tpoData.loc[(tpoData[self.rpNameKey] == rpName) & (tpoData[self.commodityIDKey].notnull())]
            if len(donorComDF) > 0:
                comID = donorComDF[self.commodityIDKey].iloc[0]
                index = row.Index
                tpoData.at[index, self.commodityIDKey] = comID
        
        # Initialize the commodity map
        #----------------------------------------------------------------------------------------------------------------------------------
        print('\n\nConstructing commodity classes ...')
        
        # Filter by period ID
        tpoPeriodData = tpoData.loc[tpoData[self.periodIDKey] == periodID]
        
        # Filter out all assigned TPOs
        unassignedTPOData = tpoPeriodData.loc[tpoPeriodData[self.statusIDKey] == 0]
        
        # Build a map of commodity classes such that each unassigned TPO is represented.
        # Iterate over each unassigned TPO.
        for row in unassignedTPOData.itertuples():
            
            try:
                # Retrieve the Commodity Class ID
                comID = int(getattr(row, self.commodityIDKey))
                    
                # If the commodity class ID does not already exist as a dictionary key, create a new Commodity object.
                if comID not in self.comMap:
                    self.comMap[comID] = com.Commodity(comID)
                    
            except:
                pass
        
        # Map TPOs to each commodity
        #----------------------------------------------------------------------------------------------------------------------------------
        print('\n\nMapping TPOs to each commodity class ...')
        
        # Map all TPOs, both assigned and unassigned, to the existing Commodity objects.
        
        # Iterate over all TPOs.
        print("Total of " + str(len(tpoPeriodData)) + " TPOs.")
        for i in range(0, len(tpoPeriodData)):
            
            # Retrieve the properties of the TPO.
            productID = tpoPeriodData.iloc[i][self.productIDKey] # Product ID
            tpoID = int(tpoPeriodData.iloc[i]['TPO_ID']) # TPO ID
            rpName = str(tpoPeriodData.iloc[i][self.rpNameKey]) # RP name
            outletID = int(tpoPeriodData.iloc[i][self.outletIDKey]) # Outlet ID (Phoenix)
            city = str(tpoPeriodData.iloc[i][self.cityKey]) # City
            province = str(tpoPeriodData.iloc[i][self.provinceKey]) # Province
            statusID = int(tpoPeriodData.iloc[i][self.statusIDKey]) # Status ID of the TPO
            
            # Convert 'Out of Stock' statuses to 'Unassigned'
            if statusID == 3:
                statusID = 0
            
            # Case 1: TPO is initialized
            if productID != "":
            
                # Search for the product description of the TPO's product.
                descDS = self.productDescData.loc[self.productDescData[self.productIDKey] == productID]
                
                # Case 1.1: The assigned product of the TPO has a commodity classification.
                if len(descDS) > 0:
                    
                    # Retrieve the ID of the commodity class to which this product belongs.
                    
                    comID = descDS.iloc[0][self.commodityIDKey]
                    UOM = descDS.iloc[0][self.uomKey]
                    
                    # Create a TargetProductOffer object, but only if a Commodity object exists for the retrieved commodity ID.
                    if comID in self.comMap:
                        
                        # Assign the TPO to the Commodity object
                        if tpoID not in self.comMap[comID].tpoIDs:
                            self.comMap[comID].tpoIDs.add(tpoID)
                    
                        # Create a new TargetProductOffer object if the ID does not exist.
                        if tpoID not in self.tpoMap:
                            self.tpoMap[tpoID] = tpro.TargetProductOffer(tpoID, rpName, outletID, city, province, UOM)
                            
                        tpo = self.tpoMap[tpoID]
                        
                        # Case 1.1.1: Unassigned or Out of Stock
                        if statusID == 0:
                            if (periodID - 1) not in tpo.properties:
                                tpo.addPeriod(periodID - 1, 1, productID)
                            tpo.addPeriod(periodID, 0, productID)
                            
                        # Case 1.1.2: Continuity
                        elif statusID == 1:
                            if (periodID - 1) not in tpo.properties:
                                tpo.addPeriod(periodID - 1, 1, productID)
                            tpo.addPeriod(periodID, 1, productID)
                        
                        # Case 1.1.3: Substitution
                        elif statusID == 2:
                            if (periodID - 1) not in tpo.properties:
                                tpo.addPeriod(periodID - 1, 1, productID)
                            tpo.addPeriod(periodID, 2, productID)
                
                # Case 1.2: The assigned product of the TPO does not have a commodity classification.
                else:
                    self.unclassifiedCount += 1
            
            # Case 2: TPO is uninitialized
            else:
                # need commodity classification and UOM of TPOs
                pass
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # assignTPO Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def assignTPO(self, 
                  cluster: clu.Cluster, 
                  tpo: tpro.TargetProductOffer,
                  currentPeriodID: int,
                  geoAggKey: str = 'City',
                  lowerQuantityCutoff: float = 0.5,
                  upperQuantityCutoff: float = 1,
                  neighbourCount: int = None,
                  relaunchDistanceCutoff: float = 0,
                  lowerDistanceCutoff: float = 0.5,
                  upperDistanceCutoff: float = 1,
                  samplingStrategy: str = 'cutoff') -> str:
        
        """  
        Method:     str assignTPO
                    (
                        Cluster cluster, 
                        TargetProductOffer tpo, 
                        int currentPeriodID, 
                        str geoAggKey,
                        float lowerQuantityCutoff,
                        float upperQuantityCutoff,
                        int neighbourCount,
                        float relaunchDistanceCutoff,
                        float lowerDistanceCutoff,
                        float upperDistanceCutoff,
                        str samplingStrategy
                    )
        
        Description: 
            Constructs and returns a list of Cluster objects for a single commodity class. The method iterates over the TargetProductOffer 
            objects belonging to the Commodity, and creates a Cluster object for each unique geographic class. 
            
        Arguments:
            string geoAggKey:
                 A string that describes the lowest geography level by which products are to be clustered.
                     'Province' : clusters include all products within a province
                     'City' : clusters include all products within a city
                     'SiteID' : clusters include all products within an outlet
            
        Output:
            A string describing the status of the TPO.
        """
        
        # Check whether the TPO is new
        newTPO = True
        prevProductID = -1
        if currentPeriodID - 1 in tpo.properties:
            prevProductID = tpo.properties[currentPeriodID - 1].productID
            if prevProductID != -1:
                newTPO = False
        
        # Assign the TPO an 'out of stock' status if the cluster is empty.
        if len(cluster.products) == 0:
            tpo.addPeriod(currentPeriodID, 3, prevProductID)
            return "OUT OF STOCK - EMPTY CLUSTER"
        else:
            cluster.addFilterSet('CURRENT')
        
        # Filter out already assigned products
        #----------------------------------------------------------------------------------------------------------------------------------
        assignedProductIDs = cluster.commodity.getAssignedProductIDs(self.tpoMap, currentPeriodID, tpo.outletID)
        cluster.applyFilterMask('CURRENT', assignedProductIDs, filterMode = 'drop')
        
        # Undo filtering if the cluster is empty.
        if len(cluster.filterSets['CURRENT']) == 0:
            cluster.addFilterSet('CURRENT')
        
        # Filter out products not belonging to the same outlet
        #----------------------------------------------------------------------------------------------------------------------------------
        cluster.copyFilterSet('CURRENT', 'OUTLET')
        cluster.applyFilterFunction('OUTLET', lambda product: tpo.outletID in product.properties[currentPeriodID].outletIDs)
        
        # Filter out products that are not measured with the same unit of measure
        #----------------------------------------------------------------------------------------------------------------------------------
        cluster.applyFilterFunction('OUTLET', lambda product: tpo.UOM == product.UOM)
        
        # Assign the TPO an 'out of stock' status if the cluster is empty.
        if len(cluster.filterSets['OUTLET']) == 0:
            tpo.addPeriod(currentPeriodID, 3, prevProductID)
            return "OUT OF STOCK - EMPTY OUTLET"
        
        if not newTPO:
            # Calculate distance
            #----------------------------------------------------------------------------------------------------------------------------------
            # Calculate the distances between the previously-selected product and all products in the cluster.
            # Return at most the top nCount nearest neighbors.
            
            nCount = neighbourCount
            if nCount == None:
                nCount = len(cluster.products)
            
            refProductID = tpo.properties[currentPeriodID - 1].productID
            refFeatures = self.productDescData.loc[self.productDescData[self.productIDKey] == refProductID]
            refFeatures = refFeatures.drop(columns = [self.productIDKey, self.commodityIDKey])
            refFeatures = refFeatures.fillna('')
            refFeatures = refFeatures.iloc[:,:].apply(lambda x: ' '.join(x), axis=1)
            
            hom.computeDistance('distance', refFeatures, cluster.products, nCount)
                                    
            # Identify relaunched products
            #----------------------------------------------------------------------------------------------------------------------------------
            # Identify potentially-relaunched products via a distance cut-off.
            cluster.copyFilterSet('OUTLET', 'RELAUNCH')
            cluster.applyFilterFunction('RELAUNCH', lambda product: product.variables['distance'] <= relaunchDistanceCutoff)
            
            # If one or more potential product relaunches exist, randomly select one and assign to the TPO a status of 'continuity'. Otherwise, continue.
            if len(cluster.filterSets['RELAUNCH']) > 0:
                try:
                    relaunchedProductID = sam.sample(cluster.products, 
                                                     cluster.filterSets['RELAUNCH'], 
                                                     cluster.filterSets['OUTLET'], 
                                                     getProbability = lambda product: product.variables['distance'],
                                                     samplingStrategy = 'cutoff',
                                                     sampleSize = 1)
                    tpo.addPeriod(currentPeriodID, 1, relaunchedProductID[0])
                    return "RELAUNCH"
                except sam.SamplingError as e:
                    pass
        
        # Calculate quantity
        #----------------------------------------------------------------------------------------------------------------------------------
        getQuantity = lambda product: product.properties[currentPeriodID].sales
        
        # Normalize quantity.
        cluster.addNormalizedVariable(self.salesKey, getQuantity, 'OUTLET', 'rank', False)
        
        # Apply quantity cutoff
        #----------------------------------------------------------------------------------------------------------------------------------
        
        # Filter out products outside of the quantity cut-offs.
        cluster.copyFilterSet('OUTLET', 'TOP_SELLERS')
        cluster.applyCutoffFilter('TOP_SELLERS',  
                                  lambda product: product.variables[self.salesKey], 
                                  lowerCutoff = lowerQuantityCutoff, 
                                  upperCutoff = upperQuantityCutoff)
        
        # Undo filtering if the filter set is empty.
        if len(cluster.filterSets['TOP_SELLERS']) == 0:
            pdb.set_trace()
            cluster.copyFilterSet('OUTLET', 'TOP_SELLERS')
        
        # Calculate word similarity
        #----------------------------------------------------------------------------------------------------------------------------------
        # Calculate word similarity scores between each product description and the previous RP name.
        
        for productID in cluster.filterSets['TOP_SELLERS']:    
            cluster.products[productID].variables['similarity'] = hom.computeWordSimilarity(tpo.rpName, cluster.products[productID].desc, '\s|/|_')
            
        maxSimilarity = cluster.find(lambda refProd, prod: refProd.variables['similarity'] < prod.variables['similarity'], 
                                     lambda prod: prod.variables['similarity'],
                                     'TOP_SELLERS')
        
        # Filter out products with word similarity scores below the maximum score.
        cluster.copyFilterSet('TOP_SELLERS', 'SIMILAR')
        if maxSimilarity != 0:
            cluster.applyFilterFunction('SIMILAR', lambda prod: prod.variables['similarity'] >= maxSimilarity)
        
        if not newTPO:
            # Apply distance cutoff
            #----------------------------------------------------------------------------------------------------------------------------------
            # Invert and rescale the distance metric.
            getDistance = lambda product: product.variables['distance']
            cluster.addNormalizedVariable(varKey='normDistance',  
                                          retriever=getDistance,
                                          setName='SIMILAR',
                                          normMode='rank', 
                                          invert=True)
            
            # Filter out products that are outside of the distance cut-offs.                         
            cluster.copyFilterSet('SIMILAR', 'DISTANCE')
            cluster.applyCutoffFilter('DISTANCE', 
                                      lambda product: product.variables['normDistance'], 
                                      lowerCutoff = lowerDistanceCutoff, 
                                      upperCutoff = upperDistanceCutoff)
            
            # Undo filtering if the filter set is empty.
            if len(cluster.filterSets['DISTANCE']) == 0:
                pdb.set_trace()
                cluster.copyFilterSet('SIMILAR', 'DISTANCE')
        
        # Select product
        #----------------------------------------------------------------------------------------------------------------------------------                      
        # Randomly select a product and assign the TPO a status of 'substitution'.
        
        if not newTPO:
            outerSet = 'DISTANCE'
            weightVar = 'normDistance'
        else:
            outerSet = 'SIMILAR'
            weightVar = self.salesKey
        
        try:
            sample = sam.sample(cluster.products, 
                                cluster.filterSets[outerSet], 
                                cluster.filterSets['OUTLET'], 
                                getProbability = lambda product: product.variables[weightVar], 
                                samplingStrategy = samplingStrategy,
                                sampleSize = 1)
            tpo.addPeriod(currentPeriodID, 2, sample[0])
        
        # Otherwise, assign the TPO a status of 'Out of Stock'.
        except sam.SamplingError as e:
            print(e)
            tpo.addPeriod(currentPeriodID, 3, prevProductID)
            return "UNASSIGNED"
            
        return "ASSIGNED"
        
    #--------------------------------------------------------------------------------------------------------------------------------------
    # buildClusterList Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def buildClusterList(self, commodity: com.Commodity, periodID: int, geoAggKey: str = 'City') -> list:
        
        """  
        Method:     list<Cluster> buildClusterList
                    (
                        Commodity commodity,
                        string geoAggKey
                    )
        
        Description: 
            Constructs and returns a list of Cluster objects for a single commodity class. The method iterates over the TargetProductOffer 
            objects belonging to the Commodity, and creates a Cluster object for each unique geographic class. 
            
        Arguments:
            Commodity commodity:
                A Commodity object that represents a given commodity class.
            string geoAggKey:
                 A string that describes the lowest geography level by which products are to be clustered.
                     'Province' : clusters include all products within a province
                     'City' : clusters include all products within a city
                     'SiteID' : clusters include all products within an outlet
            
        Output:
            list<Cluster> clusters
        """
        
        print('\nBuilding a cluster for each unique geography ...')
        
        # Construct an empty list
        clusters = []
        
        # Iterate over all TPOs assigned to the commodity class
        for tpoID in commodity.tpoIDs:
            
            tpo = self.tpoMap[tpoID]
            
            # Only consider the unassigned TPOs
            if not tpo.isAssigned(periodID):
                
                # Setup a list of geographic properties
                #   [0] := province
                #   [1] := city
                #   [2] := outlet ID
                geoProperties = ['', '', '']
                
                # Retrieve the geographic properties selected for filtering 
                if geoAggKey == self.provinceKey:
                    geoProperties[0] = tpo.province
                elif geoAggKey == self.cityKey:
                    geoProperties[0] = tpo.province
                    geoProperties[1] = tpo.city
                elif geoAggKey == self.outletIDKey:
                    geoProperties[0] = tpo.province
                    geoProperties[1] = tpo.city
                    geoProperties[2] = tpo.outletID
                
                # Check whether a Cluster object with the same geoProperties already exists.
                exists = False
                for cluster in clusters:
                    if cluster.geography.equals(geoProperties):
                        cluster.tpoIDs.append(tpoID)
                        exists = True
                        break
                       
                # If not, create a new Cluster object and add it to the cluster list.
                if exists == False:
                    
                    cluster = clu.Cluster(commodity, geo.Geography(geoProperties))
                    
                    cluster.tpoIDs.append(tpoID)
                    
                    # Find all of the outlets that are within this cluster
                    outlets = None
                    if geoAggKey == self.provinceKey:
                        outlets = self.outletData.loc[self.outletData[self.provinceKey] == tpo.province]
                    elif geoAggKey == self.cityKey:
                        outlets = self.outletData.loc[(self.outletData[self.provinceKey] == tpo.province) & (self.outletData[self.cityKey] == tpo.city)]
                    elif geoAggKey == self.outletIDKey:
                        outlets = self.outletData.loc[(self.outletData[self.provinceKey] == tpo.province) & (self.outletData[self.cityKey] == tpo.city) & (self.outletData[self.outletIDKey] == tpo.outletID)]
                    
                    # Assign the outlet IDs to the cluster
                    cluster.geography.addOutlet(outlets[self.outletIDKey].tolist())
                    
                    clusters.append(cluster)
                    
        return clusters

    #--------------------------------------------------------------------------------------------------------------------------------------
    # populateCluster Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def populateCluster(self, cluster: clu.Cluster): 
        
        """  
        Method:     void populateCluster
                    (
                        Cluster cluster
                    )
        
        Description: 
            This method finds all products belonging to the commodity class and the site IDs, and adds them to the cluster. Products are 
            aggregated together by geography.
            
        Arguments:
            Cluster cluster:
                An empty Cluster object that already has an assigned Geography object.
        """
        
        print('\nPopulating cluster ...')
        
        for outletID, outlet in cluster.geography.outlets.items():
            
            prodCluster = self.productData.loc[(self.productData[self.commodityIDKey] == cluster.commodity.ID) & (self.productData[self.outletIDKey] == outletID)]
            
            for row in prodCluster.itertuples():
                productID = getattr(row, self.productIDKey)
                unitSize = 0
                UOM = str(getattr(row, self.uomKey))
                brandType  = str(getattr(row, self.brandTypeKey))
                periodID = int(getattr(row, self.periodIDKey))
                unitCount = float(getattr(row, self.unitCountKey))
                sales = float(getattr(row, self.salesKey))
                desc = str(getattr(row, 'Desc'))
                    
                cluster.addUniqueProduct(productID, unitSize, UOM, brandType, desc, periodID, outletID, unitCount, sales)

    #--------------------------------------------------------------------------------------------------------------------------------------
    # appendResult Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def appendResult(self, tpo: tpro.TargetProductOffer, periodID: int = 0, status: str = '', cluster: clu.Cluster = None):
        
        """  
        Method:     void appendResult
                    (
                        TargetProductOffer tpo,
                        int periodID,
                        string status,
                        Cluster cluster
                    )
        
        Description: 
            This method searches through the outlets dataset for all site IDs belonging to a single cluster. Subsequently, the method finds 
            all products belonging to the commodity class and the site IDs, and adds them to the cluster. Products are aggregated together 
            by geography.
            
        Arguments:
            TargetProductOffer tpo:
                A TargetProductOffer object that represents the TPO.
            int periodID:
                An integer identifier denoting the current period. 
            string status:
                A string message that explains whether a product was assigned.
            Cluster cluster:
                A Cluster object containing all products related to the previously-selected product.
            
        """

        comID = -1
        prevDesc = ''
        prevBrandType = ''
        productCount = -1
        currentTotal = 0
        outletTotal = 0
        newDesc = ''
        newBrandType = ''
        soldAtSite = False
        inCommodity = False
        normQuant = 0
        priceHomo = 0
        distance = 0
        wordSimilarity = 0
        
        if cluster != None:
            comID = cluster.commodity.ID
            productCount = len(cluster.products)
        
        try:
            currentTotal = len(cluster.filterSets['CURRENT'])
        except:
            pass
        
        try:
            outletTotal = len(cluster.filterSets['OUTLET'])
        except:
            pass
        
        if (periodID - 1) in tpo.properties:
            try:
                prevProdDesc = self.productDescData.loc[self.productDescData[self.productIDKey] == int(tpo.properties[periodID - 1].productID)]
                prevBrandType = getattr(prevProdDesc, self.brandTypeKey)[prevProdDesc.index[0]]
                prevDesc = ds.concatenateRow(prevProdDesc, 0, ' ', [self.productIDKey, self.commodityIDKey])
            except:
                pass
        
        tpoProp = tpo.properties[periodID]
        if tpoProp.statusID == 1 or tpoProp.statusID == 2:
            
            soldAtSite = tpo.outletID in cluster.products[tpoProp.productID].properties[periodID].outletIDs
            
            newProdDesc = self.productDescData.loc[self.productDescData[self.productIDKey] == int(tpoProp.productID)]
            newBrandType = getattr(newProdDesc, self.brandTypeKey)[newProdDesc.index[0]]
            newDesc = ds.concatenateRow(newProdDesc, 0, ' ', [self.productIDKey, self.commodityIDKey])
            prodComID = int(newProdDesc.iloc[0][self.commodityIDKey])
            inCommodity = cluster.commodity.ID == prodComID
            
            product = cluster.products[tpoProp.productID]
            if self.salesKey in product.variables:
                normQuant = product.variables[self.salesKey]
            if 'homogeneity' in product.variables:
                priceHomo = product.variables['homogeneity']
            if 'distance' in product.variables:
                distance = product.variables['distance']
            
            if status == 'RELAUNCH':
                wordSimilarity = hom.computeWordSimilarity(tpo.rpName, newDesc, '\s|/|_')
            else:
                wordSimilarity = cluster.products[tpoProp.productID].variables['similarity']
        
        ds.addRow(self.tpoMatchedData,
                  [comID,
                  tpo.ID, tpo.rpName, tpo.outletID,
                  tpo.properties[periodID - 1].productID, prevDesc, prevBrandType,
                  tpo.properties[periodID].productID, newDesc, newBrandType,
                  productCount, currentTotal, outletTotal,
                  soldAtSite, inCommodity, normQuant, priceHomo, distance, wordSimilarity,
                  tpo.properties[periodID].statusID, status])