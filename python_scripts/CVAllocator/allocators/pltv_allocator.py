'''
Created on Mar 16, 2015

@author: yuval
'''
# python libraries
import time
import urllib

# project libraries
from tests_utils import HTTPtransactions


# Allocations configurations
_NUM_ALLOCATIONS_IN_SECOND=1
_NUM_TOTAL_ALLOCATIONS=5              # the total number of allocations that will be created
_ASSET_CVC_PREFIX='2_'

# Teardown configurations
_ENABLE_TEARDOWN=True
_TIME_TO_WAIT_UNTIL_TEARDOWN=20       # in seconds (counting starts upon first allocation request)
_ENABLE_TEARDOWN_ALL=True
_TIME_TO_WAIT_UNTIL_TEARDOWN_ALL=10   # in seconds (counting starts when all allocations were finished))


class pltvAllocator(object):
    '''
    Handles allocations and teardowns of pltv sessions
    '''
    
    def __init__(self, manager_ip, manager_port, service_group, stb_address, channel, home_id, asset_ext_id=1, verobsity=0):
        self.manager_ip = manager_ip
        self.manager_port = manager_port
        self.service_group = service_group
        self.stb_address = stb_address
        self.channel = channel
        self.home_id = home_id
        self.asset_ext_id = asset_ext_id 
        self.verobsity = verobsity
        
    def allocate_all_sessions(self):
        '''
        Sends all allocation request to the manager. Every allocation is done on a different asset but all on the same home.  
        '''
        allocated_sessions_ids=[]
        pltvServicesFactory = HTTPtransactions.HTTPRequestFactory(self.manager_ip, self.manager_port)
    
        allocation_service = pltvServicesFactory.makeServiceRequestFunc(servicePath='', functionName='allocate_pltv_session')
        teardown_service = pltvServicesFactory.makeServiceRequestFunc(servicePath='', functionName='teardown_pltv_session')

        print 'starting to allocate sessions'
        sleep_between_allocations = 1.0 / _NUM_ALLOCATIONS_IN_SECOND
        i = 1
        start_time = time.time()
        while i <= _NUM_TOTAL_ALLOCATIONS:
            # allocate one session
            new_session_id = self.allocate_pltv_session(allocation_service)
            allocated_sessions_ids.append(new_session_id)
            if _ENABLE_TEARDOWN and time.time() - start_time > _TIME_TO_WAIT_UNTIL_TEARDOWN:
                # Tear down oldest session
                self.teardown_pltv_session(teardown_service, allocated_sessions_ids.pop(0))
            i += 1    
            time.sleep(sleep_between_allocations)
            
        print 'finished allocating all sessions'
        if _ENABLE_TEARDOWN_ALL:
            print 'waiting for %s seconds before teardown of all sessions' % _TIME_TO_WAIT_UNTIL_TEARDOWN_ALL
            time.sleep(_TIME_TO_WAIT_UNTIL_TEARDOWN_ALL)
            print 'tearing down all sessions'
            for session_id in allocated_sessions_ids:
                self.teardown_ssp_session(teardown_service, session_id)
        
        
    def allocate_pltv_session(self, allocation_service):
        '''
        Alocates a session. 
        @return: The session dsmcc ID
        '''
        allocation_url,current_id = self._get_next_alloc_url()
        allocation_service.setServicePath(allocation_url)
        print_http_transactions = True if self.verobsity > 0 else False
        allocation_service(print_http_transactions, print_http_transactions)
        return current_id
        
    def _get_next_alloc_url(self):
        def advance_ids():
            self.asset_ext_id += 1
        
        allocation_url = "/Rev3_RSDVR?type=StartLiveRecording&CallSign=" + urllib.quote_plus(self.chnnel) + "&EndTime=300&" \
        + "HomeID=" + urllib.quote_plus(self.home_id) + "&MACAddress=102030405060&" \
        + "ServiceGroup=" + urllib.quote_plus(self.service_group) + "&abr=0" \
        + "&TemporaryAssetID=temp_pltv_" + urllib.quote_plus(str(self.asset_ext_id))

        advance_ids()
        return allocation_url
    

        
        
        
        
        
        
        