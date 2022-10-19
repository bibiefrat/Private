import threading
import time

from definitions.Globals import cfg, parser
from model.LSCP import LscpSession, LSCP_Op_code_enum


class Lscp_session_thread(threading.Thread):
    def __init__(self,assets, stb_addr,  numSess):
        threading.Thread.__init__(self)
        self.session = LscpSession.LscpSession(assets, stb_addr, "0", numSess, False)
        self.session.allocate()
        self.session.start()

    def run(self):
        print "running"
        while(1):
            self.session.__lscp_trick_play__(LSCP_Op_code_enum.LSCP_PLAY,120,"NOW", "END",0, )
            time.sleep(0.05)
            self.session.__lscp_trick_play__(LSCP_Op_code_enum.LSCP_PLAY,-24,"NOW", "END",0, )
            time.sleep(0.05)

path = "../"
allLinesList = parser.get_assets(cfg.asset_list_path, cfg.manager, path)
#for asset in allLinesList:
#    asset[0].start = asset[0].duration-0.5

fakestb = cfg.fake_stb.split(';')
session_array = []
playlists_index = 0
numOfPlayLists = len(allLinesList)
numSess = cfg.total_sessions

for i in xrange(cfg.total_sessions):
    if numSess > numOfPlayLists:
        numOfPlayLists += playlists_index
        playlists_index = 0
    cfg.init_port += 1

    session = Lscp_session_thread(allLinesList[playlists_index],fakestb[0] + ':' + str(cfg.init_port),i)

    session.start()

    session_array.append(session)

while 1:
    time.sleep(1)