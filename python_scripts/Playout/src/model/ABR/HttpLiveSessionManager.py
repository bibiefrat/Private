#import httplib
#import time
#import datetime
#from definitions import DefObjects
#from model.ABR import HttpSessionManager, AbrSessionStateEnum
#from model.ABR.HttpSessionManager import _HttpSessionManager

#class HttpLiveSessionManager(_HttpSessionManager):
#    def __init__(self, networkService, sendingThread):
#        super(HttpLiveSessionManager, self).__init__(networkService, sendingThread)
#
#
#    def parse_asset(self, asset_line):
#        asset_name,start,end = asset_line.split()
#
#        asset_duration =  60
#        self.assets.append(DefObjects.Asset(asset_name,start,end,asset_duration))
#
#    def handleSessionState(self, session):
#        super(HttpLiveSessionManager, self).handleSessionState(session)
#
#
#    def handleHttpMsg(self, session, msg, content=None):
#        session.state+=1
#
#        if(msg.status == httplib.OK ):
#
#            if(session.state == AbrSessionStateEnum.MANIFEST_REQUEST_RECEIVED):
#                session.handle_manifest_response(content)
#                session.request_fregments_list()
#            elif (session.state == AbrSessionStateEnum.FRAGMENT_LIST_REQUEST_RECEIVED):
#                session.handle_fragment_list_response(content)
#                session.request_next_fragment()
#                fragment_delta = datetime.timedelta(seconds=float(session.selected_fragment.length))
#                fragment_delta_length  = fragment_delta.seconds + (fragment_delta.microseconds / 1.0E6)
#                self.scheduler.addNewTask(time.time() +fragment_delta_length,session.request_fregments_list)
#            elif (session.state == AbrSessionStateEnum.MANAGER_MANIFEST_REQUEST_RECEIVED):
#                session.handle_manager_response(content)
#                self.networkService.UnRegister(session)
#                session.request_manifest()
##            elif (session.state == AbrSessionStateEnum.FRAGMENT_REQUEST_RECEIVED):
##                session.handle_fragment_response()
##
#
#        else:
#            session.session_log.error(content)
#
#
#
#
