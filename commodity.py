#==========================================================================================================================================
# Commodity Class
#==========================================================================================================================================
class Commodity:
    
    """
    Class:     Commodity
    
    Description:
        Represents a commodity class.
        
    Instance Variables:
        int ID:
            Unique ID of the commodity class.
        list<TargetProductOffer> tpos:
            List of TPO IDs that fall within the commodity class.
    """
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, ID: int):        
        """
        Constructor:
            
            Outlet
            (
                int ID
            )
            
        Description:
            Constructs an Commodity object.
            
        Arguments:
            int ID:
                Unique identifier of the commodity class.
        """
        
        self.ID = int(ID)
        self.tpoIDs = set()
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # containsUnassignedTPOs Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def containsUnassignedTPOs(self, tpos: dict, periodID: int) -> bool:
        """
        Method:
            
            bool containsUnassignedTPOs
            (
                dict<int, TargetProductOffer> tpos,
                int periodID
            )
            
        Description:
            Returns True if any unassigned TPOs are associated with the commodity class.
            
        Arguments:
            dict<int, TargetProductOffer>:
                Map of all TargetProductOffer objects.
                Key: TPO ID
                Value: TargetProductOffer object
            int periodID:
                Unique identifier of a reference period.
                
        Output:
            True if it contains unassigned TPOs
            False otherwise
        """
        
        for tpoID in self.tpoIDs:
            if not tpos[tpoID].isAssigned(periodID):
                return True
        return False
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # getAssignedProductIDs Method
    #--------------------------------------------------------------------------------------------------------------------------------------
    def getAssignedProductIDs(self, tpos: dict, periodID: int, outletID: int = None) -> set:
        """
        Method:
            
            set<int> getAssignedProductIDs
            (
                dict<int, TargetProductOffer> tpos,
                int periodID,
                int outletID
            )
            
        Description:
            Returns the set of IDs belonging to products within this commodity class that were assigned during the given period. 
            
        Arguments:
            dict<int, TargetProductOffer>:
                Map of all TargetProductOffer objects.
                Key: TPO ID
                Value: TargetProductOffer object
            int periodID:
                Unique identifier of a reference period.
            int outletID: If not None, the search is limited to the given outlet.
                
        Output:
            set<int>
        """
        
        assignedProductIDs = list()
        
        # Iterate over all TPOs associated with this commodity class.
        if outletID == None:
            for tpoID in self.tpoIDs:
                tpo = tpos[tpoID]
                tpoProp = tpo.properties[periodID]
                if tpo.isAssigned(periodID) and tpoProp.productID not in assignedProductIDs:
                    assignedProductIDs.append(tpoProp.productID)
        
        # Limit the search to TPOs at the given outlet.
        else:
            for tpoID in self.tpoIDs:
                tpo = tpos[tpoID]
                tpoProp = tpo.properties[periodID]
                if tpo.isAssigned(periodID) and tpo.outletID == outletID and tpoProp.productID not in assignedProductIDs:
                    assignedProductIDs.append(tpoProp.productID)
                    
        return set(assignedProductIDs)
        