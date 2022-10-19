#!/usr/bin/env

'''
Created on Mar 12, 2015

creates many allocations

@author: yuval
'''

# python libraries
import sys
import os
import time
import datetime
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

# project libraries
from tests_utils import HTTPtransactions
from tests_utils.basicPythonUtils import static_var

# package libraries
from allocators.ssp_allocator import SSPAllocator


__all__ = []
__version__ = 0.2
__updated__ = '2015-15-03'


# Topology and manager configurations
_DEFAULT_MANAGER_IP='192.168.5.81'
_DEFAULT_MANAGER_PORT=1929
_DEFAULT_SSP_SIM_IP='192.168.5.81'
_DEFAULT_SSP_SIM_PORT=1989
_DEFAULT_SERVICE_GROUP='000000000005'
_DEFAULT_STB_IP='192.168.7.225'
_DEFAULT_STB_PORT=1234                # this may be incremented by the allocator
_DEFAULT_CHANNEL_NAME='uv_chan'
_DEFAULT_HOME='200001'

# Recordings configurations
_ASSET_CVC_PREFIX='2_'
_ASSET_FIRST_EXT_ID=3000
_DEFAULT_RECORDING_DURATION=30        # in seconds
_MANAGER_TIME_STRING_FORMAT='%Y-%m-%dT%H:%M:%SZ' # the format of the times sent to the manager in XML requests
_NUM_TOTAL_RECORDINGS=50              # the total number of recordings that will be created

# Allocations configurations
_DSMCC_FIRST_ID=3000


# Used for development purpose
DEBUG_ARGS = 0
DEBUG = 1

# A script global
_USER_ARGUMENTS=[]


@static_var('asset_ext_id',_ASSET_FIRST_EXT_ID)
def create_all_recordings(manager_ip = _DEFAULT_MANAGER_IP,
                          manager_port = _DEFAULT_MANAGER_PORT,
                          home_id = _DEFAULT_HOME):
    '''
    Sends all ingest requests to the manager. Creates one recording per (future) session.
    '''
    def advance_ids():
        create_all_recordings.asset_ext_id += 1
    
    managerServicesFactory = HTTPtransactions.HTTPRequestFactory(manager_ip, manager_port)
    ingest_service = managerServicesFactory.makeServiceRequestFunc(servicePath='Rev3_RSDVR',
                                                                    requestMethod='POST',
                                                                    requestBody='requests/schedule_CV_recording.xml',
                                                                    requestBodyFromFile=True,
                                                                    requestMimeType='application/atom+xml',
                                                                    functionName='ingest_recording')
    # prepare request parameters
    ingest_service.setRequestBodyXMLProperty('.', 'CallSign', _DEFAULT_CHANNEL_NAME)
    now = datetime.datetime.utcnow()
    some_minimal_wait_time = 5
    rec_start = now + datetime.timedelta(seconds=some_minimal_wait_time)
    rec_end = now + datetime.timedelta(seconds=(some_minimal_wait_time + _DEFAULT_RECORDING_DURATION))
    ingest_service.setRequestBodyXMLProperty('.', 'StartTime', rec_start.strftime(_MANAGER_TIME_STRING_FORMAT))
    ingest_service.setRequestBodyXMLProperty('.', 'EndTime', rec_end.strftime(_MANAGER_TIME_STRING_FORMAT))
    ingest_service.setRequestBodyXMLProperty('./PVRList/PVRListItem', 'HomeID', home_id)
    ingest_service.setRequestBodyXMLProperty('./PVRList/PVRListItem', 'MACAddress', _DEFAULT_STB_IP)
    print_http_transactions = True if _USER_ARGUMENTS.verbose > 1 else False
    
    print 'starting to create recordings'
    i = 1
    while i <= _NUM_TOTAL_RECORDINGS:
        ingest_service.setRequestBodyXMLProperty('.', 'AssetID', str(create_all_recordings.asset_ext_id))
        ingest_service(print_http_transactions, print_http_transactions)
        i += 1
        advance_ids()

    # wait until ingest completes
    print 'finished schedule all recordings. waiting for ingestions to end.'
    time.sleep(_DEFAULT_RECORDING_DURATION + some_minimal_wait_time + 1)
    

def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    
    if DEBUG_ARGS:
        print argv
    
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '%s' % (program_shortdesc)

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        
        # Process arguments
        global _USER_ARGUMENTS
        _USER_ARGUMENTS = parser.parse_args()  # this method doesn't raise exceptions on errors. it exits the program and prints errors to user
        
        # ingest all assets and then start allocations
        create_all_recordings()
        allocator = SSPAllocator(_DEFAULT_SSP_SIM_IP, _DEFAULT_SSP_SIM_PORT, _DEFAULT_SERVICE_GROUP, _DEFAULT_STB_IP, _DEFAULT_STB_PORT,
                                 _DEFAULT_HOME, _DSMCC_FIRST_ID, _ASSET_FIRST_EXT_ID, _USER_ARGUMENTS.verbose)
        allocator.allocate_all_sessions()
                
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        if DEBUG_ARGS or DEBUG:
            raise Exception, str(e), sys.exc_info()[2]
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    
if __name__ == '__main__':
    if DEBUG_ARGS:
        sys.argv.append("--help")
    if DEBUG:
        sys.argv.append("-vv")
    sys.exit(main())