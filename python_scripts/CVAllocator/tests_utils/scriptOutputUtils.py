'''
Created on Aug 21, 2014

@author: yuval


TODO: this module!!


Utilities to handle scripts outputs.
This module uses a file that holds all the script constructed output (the output that should be parsed by tools (FX_Tester)
to decide if the test was successful or failed).
This file can then be read and printed to the standard output stream of the script at the end of the script running,
so the parsed output will be concentrated nicely at the end of the output.
'''

import comparisonWithToleration

''' the output file. This gets closed when printOutput gets called '''
#outFile = open('output','r+')

''' do checks and print output '''
    
def checkEqualAndPrint(value1, value2, tolerance, okMessage='', failMessage=None):
    '''
    if two values are equal (or within tolerance range), print okMessage, else, print failMessge
    messages are optional. If fail message is omitted, ok message will be used as both.
    '''
    if failMessage is None:
        failMessage = okMessage
    if comparisonWithToleration.compareTolerate(value1, value2, tolerance) == 0:
        saveOutput(True, okMessage + ' (' + str(value1) + ' and ' + str(value2) + ' are equal with tolerance: ' + str(tolerance) + ')')
    else:
        saveOutput(False, failMessage + ' (' + str(value1) + ' and ' + str(value2) + ' are not equal with tolerance: ' + str(tolerance) + ')')


def checkGreaterAndPrint(value1, value2, tolerance, okMessage='', failMessage=None):
    '''
    if first value + tolerance is greater than the second, print okMessage, else, print failMessge
    messages are optional. If fail message is omitted, ok message will be used as both.
    '''
    if failMessage is None:
        failMessage = okMessage
    if comparisonWithToleration.gtTolerate(value1, value2, tolerance):
        saveOutput(True, okMessage + ' (' + str(value1) + ' is greater than ' + str(value2) + ' using tolerance: ' + str(tolerance) + ')')
    else:
        saveOutput(False, failMessage + ' (' + str(value1) + ' is not greater than ' + str(value2) + ' using tolerance: ' + str(tolerance) + ')')

def checkLesserAndPrint(value1, value2, tolerance, okMessage='', failMessage=None):
    '''
    if first value - tolerance is lesser than the second, print okMessage, else, print failMessge
    messages are optional. If fail message is omitted, ok message will be used as both.
    '''
    if failMessage is None:
        failMessage = okMessage
    if comparisonWithToleration.ltTolerate(value1, value2, tolerance):
        saveOutput(True, okMessage + ' (' + str(value1) + ' is lesser than ' + str(value2) + ' using tolerance: ' + str(tolerance) + ')')
    else:
        saveOutput(False, failMessage + ' (' + str(value1) + ' is not lesser than ' + str(value2) + ' using tolerance: ' + str(tolerance) + ')')

def checkBetweenAndPrint(value, lower, upper, tolerance, okMessage='', failMessage=None):
    '''
    if value is between lower and upper limits (with tolerance), print okMessage, else, print failMessge
    messages are optional. If fail message is omitted, ok message will be used as both.
    '''
    if failMessage is None:
        failMessage = okMessage
    if comparisonWithToleration.betweenTolerate(value, lower, upper, tolerance):
        saveOutput(True, okMessage + ' (' + str(value) + ' is between ' + str(lower) + ' and ' + str(upper) + ' using tolerance: ' + str(tolerance) + ')')
    else:
        saveOutput(False, failMessage + ' (' + str(value) + ' is not between ' + str(lower) + ' and ' + str(upper) + ' using tolerance: ' + str(tolerance) + ')')


def saveOutput(boolIsOK, message=''):
    # initialize an inside counter for printing
    if not hasattr(saveOutput, "counter"):
        saveOutput.counter = 0
    saveOutput.counter += 1
    
    if boolIsOK:
        initial = '~~OUTPUT ' + str(saveOutput.counter) + ' OK: '
    else:
        initial = '~~OUTPUT ' + str(saveOutput.counter) + ' FAIL: '
    
    print initial + message

"""
def printOutput():
    '''
    prints all the saved output to the standard output and deletes the file
    '''
    # should also flush the script's output
    pass
"""








