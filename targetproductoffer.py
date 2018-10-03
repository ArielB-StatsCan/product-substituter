#==========================================================================================================================================
# TPOProperties Class
#==========================================================================================================================================
class TPOProperties:
    
    """
    Class:     TPOProperties
    
    Description:
        Contains the time-dependent properties of a TPO during a single period.
        
    Instance Variables:
        int periodID
        int statusID:
            Status of the TPO.
                0 := unassigned
                1 := continuity
                2 := substitution
                3 := out of stock
        T productID
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, periodID: int, statusID: int, productID):
        self.periodID = int(periodID)
        self.statusID = statusID
        self.productID = productID
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # toString Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def toString(self, escChars: str = "\n") -> str:
        response = escChars + "------------------------------"
        response += escChars + "Data type: TPO Properties"
        
        response += escChars + "Period ID: " + str(self.periodID)
        response += escChars + "Status ID: " + str(self.statusID)
        response += escChars + "Product ID: " + str(self.productID)
        
        response += escChars + "------------------------------"
        return response
    
#==========================================================================================================================================
# TargetProductOffer Class
#==========================================================================================================================================
class TargetProductOffer:
    
    """
    Class:     TargetProductOffer
    
    Description:
        Represents a TPO.
        
    Instance Variables:
        int ID:
            Unique ID of the TPO.
        str rpName:
            Name of the representative product.
        int outletID:
            Unique Phoenix ID of the outlet.
        dict<int, TPOProperties> properties:
            Map of TPOProperties objects. 
            Key: Period ID. 
            Value: TPOProperty object.
        string UOM:
            Unit of measure of the assigned product.
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, ID: int, rpName: str, outletID: int, city: str, province: str, UOM: str):
        
        """
        Constructor:
            
            TargetProductOffer
            (
                int ID,
                string rpName,
                int outletID,
                string city,
                string province,
                string UOM
            )
            
        Description:
            Constructs a TargetProductOffer object.
        """
        
        self.ID = int(ID)
        
        self.rpName = rpName
        
        self.outletID = int(outletID)
        
        self.city = str(city)
        
        self.province = str(province)
        
        self.UOM = UOM
        
        self.properties = {}
        
    #--------------------------------------------------------------------------------------------------------------------------------------
    # isAssigned Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def isAssigned(self, periodID: int) -> bool:
        
        """
        Method:
            
            bool isAssigned()
            
        Description:
            Returns true if the TPO has a newly-assigned product. Returns false otherwise.
            
        Output:
            bool
        """
        
        if self.properties[periodID].statusID == 0 or self.properties[periodID].statusID == 3:
            return False
        else:
            return True
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # addPeriod Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def addPeriod(self, periodID: int, statusID: int, productID):
        
        """
        Method:
            
            void addPeriod
            (
                int periodID,
                int statusID,
                T productID
            )
            
        Description:
            Assigns the given product ID to the TPO and sets the TPO status.
        """
        if periodID in self.properties:
            self.properties[periodID].productID = productID
            self.properties[periodID].statusID = statusID
        else:
            self.properties[periodID] = TPOProperties(periodID, statusID, productID)
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # toString Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def toString(self, escChars: str = "\n") -> str:
        response = escChars + "------------------------------"
        response += escChars + "Data type: Target Product Offer"
        
        response += escChars + "ID: " + str(self.ID)
        response += escChars + "RP Name: " + str(self.rpName)
        response += escChars + "Outlet ID: " + str(self.outletID)
        response += escChars + "UOM: " + str(self.UOM)
        
        response += escChars + "Properties: " + str(len(self.properties))
        for periodID, prop in self.properties.items():
            response += escChars + str(periodID) + ": " + str(prop.toString(escChars + '\t'))
            
        response += escChars + "------------------------------"
        return response