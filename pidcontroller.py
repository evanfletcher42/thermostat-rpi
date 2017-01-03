# Implements a PID controller with minor derivative filtering.  

class PIDController(object):
    
    # PID coefficients.
    # WARNING: I tuned these for my apartment in particular, which is pretty small and leaky.  
    # They may not work well for you.
    P = -1.812273
    I = -0.018923
    D = -0.563824
    
    # Low pass (exponential) filter coefficient for filtering error.  
    # Makes derivatives a little more sensible.  
    LPF_COEF = 0.25
    
    # Max integrator magnitude (prevents windup)
    MAX_I_VAL = 1.0
    
    def __init__(self):
        # p/i/d values during evaluation
        self.pValue = 0.0;
        self.iValue = 0.0;
        self.dValue = 0.0;
        
        self.lastErrorLpf = 0.0; #memory for low pass filter
    
    def update(self, tMeas, tSet):
        error = tMeas - tSet;
        
        self.pValue = self.P * error
        
        self.iValue = self.I * error + self.iValue
        self.iValue = max(min(self.MAX_I_VAL, n), -1*self.MAX_I_VAL)
        
        errFiltered =  self.lastErrorLpf*(1-self.LPF_COEF) + error*self.LPF_COEF
        self.dValue = self.D * (errFiltered - self.lastErrorLpf)
        self.lastErrorLpf = errFiltered
        
        return (self.pValue + self.iValue + self.dValue)