
from model.ABR import AbrAsset
from model.RTSP.RtspSessionManager import RtspSessionManager

class RollingBufferSessionManager(RtspSessionManager):
    def __init__(self, networkService, sendingThread):
        super(RollingBufferSessionManager, self).__init__(networkService, sendingThread)

    def parse_asset(self, asset_line):
        asset_name,start,end = asset_line.split()
        self.assets.append(AbrAsset(asset_name,start,end,"%Y-%m-%dT%H:%M:%SZ"))



