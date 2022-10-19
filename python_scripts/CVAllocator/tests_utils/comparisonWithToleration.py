'''
Created on Sep 7, 2014

comparison functions with an option to tolerate some error  

@author: yuval
'''


def compareTolerate(value1,value2,tolerance):
    '''
    Compares two values with some toleration.
    @return: 0 if the two values are identical, or the difference between them is less than the toleration.
    positive if value1 is greater than value2 + toleration
    negative if value1 is smaller then value2 - toleration
    '''
    return 0 if abs(value1 - value2) <= tolerance else value1 - value2

def gtTolerate(value1,value2,tolerance):
    return True if value1 + tolerance > value2 else False

def ltTolerate(value1,value2,tolerance):
    return True if value1 - tolerance < value2 else False

def betweenTolerate(value,lower,upper,tolerance):
    return True if value - tolerance < upper and value + tolerance > lower else False 


