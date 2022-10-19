'''
Created on Aug 28, 2014

@author: yuval

Basic python utilities

'''

def map_dictionary(func,dic):
    '''
    the function should operate on the (key,value) pairs of the dictionary 
    '''
    dict2list = lambda dic: [(k, v) for (k, v) in dic.iteritems()]
    return dict(map(func,dict2list(dic)))




def static_var(var_name, var_init_value):
    '''
    A wrapper to a decorator to get name and value as an input
    Usage:
    @static_var('my_var',8)
    def my_foo(): ...
    '''
    
    def static_var_dec(func):
        '''
        A decorator that addes a static variable to a function
        '''
        setattr(func, var_name, var_init_value)
        return func
    
    return static_var_dec
    