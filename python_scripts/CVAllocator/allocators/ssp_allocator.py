'''
Created on Mar 16, 2015

@author: yuval
'''
# python libraries
import time
import urllib

# project libraries
from tests_utils import HTTPtransactions
from tests_utils.basicPythonUtils import static_var



# TODO:
# many configurations should become variables, and configured in the using script (ex: TOTAL_ALLOCS)
# build an allocator class from which SSP allocator and pltv allocator inherit
# build a recorder class to do all the recordings

# Allocations configurations
_NUM_ALLOCATIONS_IN_SECOND=1
_NUM_TOTAL_ALLOCATIONS=50             # the total number of allocations that will be created
_ASSET_CVC_PREFIX='2_'
_DSMCC_ID_LENGTH=20                   # you should probably don't change this one

# Teardown configurations
_ENABLE_TEARDOWN=True                 # teardown allocated sessions
_TIME_TO_WAIT_UNTIL_TEARDOWN=20       # in seconds (counting starts upon first allocation request)
_ENABLE_TEARDOWN_ALL=True             # teardown of all remaining sessions in the end of running
_TIME_TO_WAIT_UNTIL_TEARDOWN_ALL=10   # in seconds (counting starts when all allocations were finished))


class SSPAllocator(object):
    '''
    Handles allocations and teardowns of SSP sessions 
    '''

    def __init__(self, ssp_ip, ssp_port, service_group, stb_ip, stb_port, home_id, dsmcc_id=1, asset_ext_id=1, verobsity=0):
        self.ssp_ip = ssp_ip
        self.ssp_port = ssp_port
        self.service_group = service_group
        self.stb_ip = stb_ip
        self.stb_port = stb_port
        self.home_id = home_id
        self.dsmcc_id = dsmcc_id
        self.asset_ext_id = asset_ext_id
        self.verobsity = verobsity
        
    def allocate_all_sessions(self):
        '''
        Sends all allocation request to the manager. Every allocation is done on a different asset but all on the same home.  
        '''
        allocated_sessions_ids=[]
        sspServicesFactory = HTTPtransactions.HTTPRequestFactory(self.ssp_ip, self.ssp_port)
    
        allocation_service = sspServicesFactory.makeServiceRequestFunc(servicePath='', functionName='allocate_ssp_session')
        teardown_service = sspServicesFactory.makeServiceRequestFunc(servicePath='', functionName='teardown_ssp_session')
        
        print 'starting to allocate sessions'
        sleep_between_allocations = 1.0 / _NUM_ALLOCATIONS_IN_SECOND
        i = 1
        start_time = time.time()
        while i <= _NUM_TOTAL_ALLOCATIONS:
            # allocate one session
            new_session_id = self.allocate_ssp_session(allocation_service)
            allocated_sessions_ids.append(new_session_id)
            if _ENABLE_TEARDOWN and time.time() - start_time > _TIME_TO_WAIT_UNTIL_TEARDOWN:
                # Tear down oldest session
                self.teardown_ssp_session(teardown_service, allocated_sessions_ids.pop(0))
            i += 1    
            time.sleep(sleep_between_allocations)
            
        print 'finished allocating all sessions'
        if _ENABLE_TEARDOWN_ALL:
            print 'waiting for %s seconds before teardown of all sessions' % _TIME_TO_WAIT_UNTIL_TEARDOWN_ALL
            time.sleep(_TIME_TO_WAIT_UNTIL_TEARDOWN_ALL)
            print 'tearing down all sessions'
            for session_id in allocated_sessions_ids:
                self.teardown_ssp_session(teardown_service, session_id)
                
    def allocate_ssp_session(self, allocation_service):
        '''
        Alocates a session. 
        @return: The session dsmcc ID
        '''
        allocation_url,current_id = self._get_next_alloc_url()
        allocation_service.setServicePath(allocation_url)
        print_http_transactions = True if self.verobsity > 0 else False
        resp = allocation_service(print_http_transactions, print_http_transactions)
        # verify no errors in response
        if resp.getXMLAllValues('./error_id'):
            if not print_http_transactions:
                print resp 
            print '(Error allocating session ' + str(current_id) + ')'
        return current_id
    
    def teardown_ssp_session(self, teardown_service, dsmcc_id):
        '''
        Tears down a session. 
        '''
        teardown_url = 'mng_session_teardown?type=0&isa_consistency=0&ngod_reason=0&get_info=0&id=' + urllib.quote_plus(str(dsmcc_id).zfill(_DSMCC_ID_LENGTH))
        teardown_service.setServicePath(teardown_url)
        print_http_transactions = True if self.verobsity > 0 else False
        teardown_service(print_http_transactions, print_http_transactions)

    def _get_next_alloc_url(self):
        def advance_ids():
            self.dsmcc_id += 1
            self.asset_ext_id += 1
            self.stb_port += 1
        
        current_id = str(self.dsmcc_id) 
        allocation_url="mng_session_allocate?size=1&internal_asset_id=0&seg_start=0&seg_end=0&asset_type=-1&size=0&size=0&size=0" \
        + "&c2_far_server_addr=0.0.0.0%3A0&c2_far_asset_id=&c2_far_provider_id=&splice_on_key_frame=97&ingest_start_time=0&" \
        + "asset_id=" + urllib.quote_plus(_ASSET_CVC_PREFIX + str(self.asset_ext_id) + '$' + self.home_id) \
        +"&loop=0&abr=0&requested_layer=&abr_type=0" \
        + "&service_group=" + urllib.quote_plus(self.service_group) \
        + "&type=0&dsmcc_id=" + urllib.quote_plus(current_id.zfill(_DSMCC_ID_LENGTH)) \
        + "&streamer_id=0&initiator=&stb_id=&requested_bw=4000000&stb_addr=" + urllib.quote_plus(self.stb_ip + ':' + str(self.stb_port)) \
        + "&edge_name=&stb_ip=" + urllib.quote_plus(self.stb_ip + ':' + str(self.stb_port))
        
        advance_ids()
        return allocation_url,current_id

        
        
        
        
        
        
