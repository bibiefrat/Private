from logging.handlers import RotatingFileHandler

import logging
import signal
import string


import inspect

import time

#def timeit(f):
#
#    def timed(*args, **kw):
#
#        ts = time.time()
#        result = f(*args, **kw)
#        te = time.time()
#
#        print 'func:%r args: took: %2.4f sec' %\
#              (f.__name__,   te-ts)
#        return result
#
#    return timed

def extract_param_by_name(f, args, kwargs, param):
    """Find the value of a parameter by name, even if it was passed via *args or is a default value.

    Let's start with a fictional function:
    >>> def my_f(a,b,c='foo'):
    ...   {"a":a,"b":b,"c":c}
    ...

    Works with kwargs (easy):
    >>> extract_param_by_name(my_f, [], {'a':1}, 'a')
    1

    Works with args (not obvious):
    >>> extract_param_by_name(my_f, [2], {}, 'a')
    2

    Works with default kwargs (bet you didn't think about that one):
    >>> extract_param_by_name(my_f, [], {}, 'c')
    'foo'

    But of course you can override that:
    >>> extract_param_by_name(my_f, [99,98,97], {}, 'c')
    97

    In different ways:
    >>> extract_param_by_name(my_f, [], {'c':'gar'}, 'c')
    'gar'

    And dies with "grace" when you do something silly:
    >>> extract_param_by_name(my_f, [], {}, 'a')
    Traceback (most recent call last):
    ...
    LoggerBadCallerParametersException: ("Caller didn't provide a required positional parameter '%s' at index %d", 'a', 0)
    >>> extract_param_by_name(my_f, [], {}, 'z')
    Traceback (most recent call last):
    ...
    LoggerUnknownParamException: ('Unknown param %s(%r) on %s', <type 'str'>, 'z', 'my_f')
    """
    if param in kwargs:
        return kwargs[param]
    else:
        argspec = inspect.getargspec(f)
        if param in argspec.args:
            param_index = argspec.args.index(param)
            if len(args) > param_index:
                return args[param_index]

            if argspec.defaults is not None:
                # argsec.defaults holds the values for the LAST entries of argspec.args
                defaults_index = param_index - len(argspec.args) + len(argspec.defaults)
                if 0 <= defaults_index < len(argspec.defaults):
                    return argspec.defaults[defaults_index]

            raise LoggerBadCallerParametersException("Caller didn't provide a required positional parameter '%s' at index %d", param, param_index)
        else:
            raise LoggerUnknownParamException("Unknown param %s(%r) on %s", type(param), param, f.__name__)

class LoggerUnknownParamException(Exception):
    pass

class LoggerBadCallerParametersException(Exception):
    pass

def simple_decorator(decorator):
    '''This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.'''
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
        # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator

@simple_decorator
def my_simple_logging_decorator(func):
    def you_will_never_see_this_name(*args, **kwargs):
        if(len(args)>0):
            logging.getLogger(type(args[0]).__name__).devel("calling {%s}" % (func.__name__))
        else:
            logging.getLogger(func.__name__).devel("is called")
#        print "calling {%s}" % (func.__name__)
        return func(*args, **kwargs)
    return you_will_never_see_this_name

def signal_handler(signal, frame):
    raise SystemExit

class ExtendedLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        logging.Logger.__init__(self, name ,logging.getLogger('').level)


    def devel(self,msg, *args, **kwargs):
        self.log( 5, msg, *args, **kwargs)

def defineLogger(logfile,level):
# Defining the log level and handling


    logging.DEVEL = 5  # positive yet important
    logging.addLevelName(5,"DEVEL")

    if not str(level).isdigit():
        log_level = string.upper(level)
        print "Log level = " + log_level
        if log_level == "DEBUG":
            log_print = logging.DEBUG
        elif log_level == "INFO":
            log_print = logging.INFO
        elif log_level == "WARNING":
            log_print = logging.WARNING
        elif log_level == "ERROR":
            log_print = logging.ERROR
        elif log_level == "CRITICAL":
            log_print = logging.CRITICAL
        elif log_level == "DEVEL":
            log_print = 5
    else:
        log_print = int(level)

    logging.setLoggerClass(ExtendedLogger)

    formatter = logging.Formatter("[%(asctime)-19s.%(msecs).03d] [%(name)-8s] [%(levelname)s]  %(message)26s",
        datefmt='%d-%m-%Y %H:%M:%S')

    fileHandler = RotatingFileHandler(
        filename="../" + logfile, maxBytes=10 * 1024*1024, backupCount=10)
    fileHandler.setLevel(40)




    fileHandler.setFormatter(formatter)

#    logging.basicConfig(level=5,
#        format="[%(asctime)-19s.%(msecs).03d] %(name)-8s: [%(levelname)s] %(message)26s",
#        datefmt='%d-%m-%Y %H:%M:%S',
#        filename="../" + logfile,
#        filemode='w')


    console = logging.StreamHandler()
    console.setLevel(log_print)
    console.setFormatter(formatter)


    logging.getLogger('').addHandler(console)
    logging.getLogger('').addHandler(fileHandler)
    logging.getLogger('').setLevel(5)
    signal.signal(signal.SIGINT, signal_handler)

