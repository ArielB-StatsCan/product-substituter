import targetproductoffer as tpro

#==========================================================================================================================================
# Outlet Class
#==========================================================================================================================================
class Outlet:
    
    """
    Class:     Outlet
    
    Description:
        Represents an outlet.
        
    Instance Variables:
        int ID: Unique identifier of an outlet in Phoenix.
        dict<int, int> siteIDs:
            Corresponding site IDs over the course of given time frame.
            Key: Period ID
            Value: Site ID
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, ID):
        """
        Constructor:
            
            Outlet
            (
                int ID
            )
            
        Description:
            Constructs an Outlet object.
            
        Arguments:
            int ID:
                Unique identifier of the outlet.
        """
        
        self.ID = ID
        self.siteIDs = {}
        
    #--------------------------------------------------------------------------------------------------------------------------------------
    # addSiteID Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def addSiteID(self, periodID: int, siteID: int):
        """
        Method:
            
            void addSiteID
            (
                int periodID,
                int siteID
            )
            
        Description:
            Links the given site ID to the ID of this outlet for the given period ID.
            
        Arguments:
            int periodID:
                Unique identifier of a reference period.
            int siteID:
                Unique retailer identifier of an outlet.
        """
        
        self.siteIDs[periodID] = int(siteID)
    
     #--------------------------------------------------------------------------------------------------------------------------------------
    # toString Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def toString(self, escChars: str = "\n") -> str:
        response = escChars + "------------------------------"
        response += escChars + "Data type: Outlet"
        
        response += escChars + "ID: " + str(self.ID)
        
        response += escChars + "Site IDs that correspond to this outlet:"
        for periodID, siteID in self.siteIDs.items():
            response += escChars + str(periodID) + ". " + str(siteID)
        
        response += escChars + "------------------------------"
        return response
    
#==========================================================================================================================================
# Geography Class
#==========================================================================================================================================
class Geography:
    
    """
    Class:     Geography
    
    Description:
        Represents a geographic class.
        
    Instance Variables:
        list<T> properties
        dict<int, Outlet>:
            Map of Outlet objects belonging to this geographic class.
            Key: Outlet ID
            Value: Outlet object
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, properties: list):
        
        """
        Constructor:
            
            Geography
            (
                list<T> properties
            )
            
        Description:
            Constructs a Geography object.
            
        Arguments:
            list<T> properties:
                List of properties belonging to the geographic class. Can be of any type.
        """
        
        self.properties = list(properties)
        self.outlets = {}
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # addSiteID Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def addOutlet(self, outletIDs):
        """
        Method:
            
            void addOutlet
            (
                list<int> outletIDs
            )
            
        Description:
            Creates Outlet objects for each identifier given in outletIDs.
            
        Arguments:
            list<int> outletIDs: List of identifiers of the Outlet objects to be created.
        """
        
        for outletID in outletIDs:
            if outletID not in self.outlets.keys():
                self.outlets[outletID] = Outlet(outletID)
        
    #--------------------------------------------------------------------------------------------------------------------------------------
    # equals Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def equals(self, props: list) -> bool:
        """
        Method:
            
            bool equals
            (
                list<T> props
            )
            
        Description:
            Checks whether the given property array is equal to the properties of the Geography object.
            
        Arguments:
            list<T> props: List of properties.
        """
        
        # Return False if the property vectors are of unequal lengths
        if len(props) < len(self.properties):
            return False
        
        # Return False if any of the properties are not equal to their counterparts
        for i in range(0, len(self.properties)):
            if self.properties[i] != props[i]:
                return False
        
        # Return True otherwise.
        return True
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # toString Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def toString(self, escChars: str = "\n") -> str:
        response = escChars + "------------------------------"
        response += escChars + "Data type: Geography"
        
        for geoProperty in self.properties:
            response += escChars + str(geoProperty)
        
        response += escChars + "Outlets that belong to this geography:"
        for i, ID in enumerate(self.outlets):
            response += escChars + str(i + 1) + ".\n" + str(self.outlets[ID].toString(escChars + "\t"))
            if i == 9:
                break
        
        response += escChars + "------------------------------"
        return response
        