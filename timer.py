from datetime import datetime

class Timer:
    
    startTime = 0
    
    @classmethod
    def startTimer(cls):
        cls.startTime = datetime.now()
    
    @classmethod
    def elapsedTime(cls):
    
        """  
        Method:     datetime elapsedTime()
        
        Description: 
            Returns the time elapsed since the starting time.
            
        Output:
            datetime
        """
        
        return datetime.now() - cls.startTime