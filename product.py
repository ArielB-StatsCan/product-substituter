import pdb

#==========================================================================================================================================
# Properties Class
#==========================================================================================================================================
class ProductProperties:
    
    """
    Class:     ProductProperties
    
    Description:
        Contains the time-dependent properties of a product during a single period.
        
    Instance Variables:
        int periodID
        list<int> outletIDs
        float unitSize
        float units
        float sales
        int aggregateCount
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, periodID: int, outletID: int, unitSize: float, unitCount: float, sales: float):
        """
        Constructor:    ProductProperties
                        (
                            int periodID,
                            int outletID,
                            float unitSize,
                            float unitCount,
                            float sales
                        )
                        
        Arguments:
            int periodID: Unique identifier of the references period during which the product was sold.
            int outletID: Unique idenfitier of the outlet at which the product was sold.
            float unitSize: Volume or mass of a single unit of product.
            float unitCount: Number of units sold during the reference period.
            float sales: Amount of revenue in CAD that was made from the product.
        """
        
        self.periodID = int(periodID)
        self.outletIDs = [int(outletID)]
        self.unitSize = float(unitSize)
        self.unitCount = float(unitCount)
        self.sales = float(sales)
        self.aggregateCount = 1
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # aggregate Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def aggregate(self, addition):
        """
        Method:     void aggregate
                    (
                        ProductProperties addition
                    )
        
        Description: 
            This method aggregates self and addition together.
            
        Arguments:
            ProductProperties addition: Object that is aggregated with self.
        """
        
        self.outletIDs.extend(addition.outletIDs)
        self.unitCount += addition.unitCount
        self.sales += addition.sales
        self.aggregateCount += 1
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # price Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def price(self) -> float:
        """
        Method:     float price()
        
        Description: 
            This method returns the unit price.
            
        Output:
            Unit price of the product.
        """
        
        return self.sales / self.unitCount
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # size Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def size(self) -> float:
        """
        Method:     float size()
        
        Description: 
            This method returns the total volume or mass of the product.
            
        Output:
            product size
        """

        
        return self.unitCount * self.unitSize
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # toString Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def toString(self, escChars: str = "\n", UOM: str = "", limit: bool = True) -> str:
        response = escChars + "------------------------------"
        response += escChars + "Data type: Product Properties"
        
        response += escChars + "Period ID: " + str(self.periodID)
        response += escChars + "Unit Size: " + str(self.unitSize) + " " + UOM
        response += escChars + "Number of Units: " + str(self.unitCount)
        response += escChars + "Size: " + str(self.size()) + " " + UOM
        response += escChars + "Sales: " + str(self.sales)
        response += escChars + "Price: $" + str(self.price())
        response += escChars + "Aggregate Count: " + str(self.aggregateCount)
        
        response += escChars + "Outlet IDs at which this product was sold:"
        for i, outletID in enumerate(self.outletIDs):
            response += escChars + str(i + 1) + ". " + str(outletID)
            if i == 9 and limit:
                response += escChars + "..." 
                break
        
        response += escChars + "------------------------------"
        return response

#==========================================================================================================================================
# Product Class
#==========================================================================================================================================
class Product:
    
    """
    Class:     Product
    
    Description:
        Represents a product aggregate over a specific geographic area. Time-dependent product properties are stored in ProductProperties 
        objects.
        
    Instance Variables:
        T productID:
            Unique identifier of the product.
        str UOM:
            Unit of measure.
        str brandType:
            Private or manufacturer brand.
        str desc:
            Concatenated string containing all of the text features of the product.
        dict<int, ProductProperties> properties:
            Collection of ProductProperties objects. Each one contains the properties of the Product object at a different reference period.
            Key: periodID
            Value: ProductProperty object
        dict<str, T> variables:
            Collection of variables of type T. Each variable is identified by a name.
            Key: name of the variable
            Value: variable of type T
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, productID, UOM: str, brandType: str, desc: str):
        
        """
        Constructor:    Product
                        (
                            T productID,
                            string UOM,
                            string desc
                        )
                        
        Arguments:
            T productID: Unique identifier of the product.
            string UOM: Unit of measure.
            string desc: A string of concatenated text features of the product.
        """
        
        self.productID = productID
        self.UOM = str(UOM)
        self.desc = str(desc)
        self.brandType = str(brandType)
        
        # Dict of ProductProperties.
        # Key: Reference Period ID. Value: ProductProperties.
        self.properties = {}
        
        # Dict of variables.
        # Key: Variable name. Value: Value of the variable.
        self.variables = {}
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # isPresent Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def isPresent(self, periodID: int):
        """
        Method:     bool isPresent()
        
        Description: 
            This method returns True if the product was present during the given reference period.
            
        Output:
            True if present
            False if absent
        """
        
        return periodID in self.properties
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # priceRelative Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def priceRelative(self, periodID: int, basePeriodID: int) -> float:
        """
        Method:     float priceRelative
                    (
                        int periodID,
                        int basePeriodID
                    )
        
        Description: 
            This method calculates a price relative between periodID and basePeriodID.
            
        Output:
            price relative
        """
        
        return self.properties[periodID].price() / self.properties[basePeriodID].price()
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # addProperties Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def addProperties(self, periodID: int, outletID: int, unitSize: float, unitCount: float, sales: float):
        """
        Method:     void addProperties
                    (
                        int periodID,
                        int outletID,
                        float unitSize,
                        float unitCount,
                        float sales
                    )
        
        Description: 
            This method creates a new ProductProperties object. If a ProductProperties object already exists for the given periodID,
            the two are aggregated together.
        """
        
        if periodID not in self.properties:
            self.properties[periodID] = ProductProperties(periodID, outletID, unitSize, unitCount, sales)
        else:
            self.properties[periodID].aggregate(ProductProperties(periodID, outletID, unitSize, unitCount, sales))
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # toString Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def toString(self, escChars: str = "\n", limit: bool = True) -> str:
        response = escChars + "------------------------------"
        response += escChars + "Data type: Product"
        
        response += escChars + "Product ID: " + str(self.productID)
        response += escChars + "Description: " + str(self.desc)
        
        response += escChars + "Periods: " + str(len(self.properties))
        for periodID, attr in self.properties.items():
            response += attr.toString(escChars + "\t", self.UOM, limit)
            
        response += escChars + "Variables: " + str(len(self.variables))
        for varName, var in self.variables.items():
            response += escChars + "\t" + varName + ": " + str(var)
        
        response += escChars + "------------------------------"
        return response