from ConfigReader import cfg
from model.ABR import AbrSessionProfile,  AbrSessionType, AbrAssetType


def manifest_request_decorator(method):
    def request_manifest_decorator(self):
        format = ""
        if(self.type == AbrSessionType.STATIC):
            if(self.profile == AbrSessionProfile.HLS ):
                if(self.asset_type == AbrAssetType.VOD_ASSET):
                    format = "/shls"+self.channel+"/"+str(cfg.fragment_length)+".m3u8?start="+self.startTime+"&end="+self.endTime+"&device=" + self.device_profile
                else:
                    format = "/shls/LIVE$"+self.channel.strip("LIVE$")+"/"+str(cfg.fragment_length)+".m3u8?start="+self.startTime+"&end="+self.endTime+"&device=" + self.device_profile
            elif (self.profile == AbrSessionProfile.SMOOTH):
                if(self.asset_type == AbrAssetType.VOD_ASSET):
                    format = "/shls"+self.channel.strip("LIVE$")+"/"+str(cfg.fragment_length)+".m3u8?start="+self.startTime+"&end="+self.endTime+"&device=" + self.device_profile
                else:
                    format="/shss/LIVE$"+self.channel.strip("LIVE$")+"/"+str(cfg.fragment_length)+".ism/Manifest?start="+self.startTime+"&end="+self.endTime+"&device=" + self.device_profile
            return method(self,format)
        elif(self.type == AbrSessionType.DYNAMIC):
            return method(self,self.streamer_url)

    return request_manifest_decorator

def fragment_list_request_decorator(method):
    def request_fragment_list_decorator(self):
        format = ""
        if(self.type == AbrSessionType.STATIC):
            if(self.profile == AbrSessionProfile.HLS ):
                if(self.asset_type == AbrAssetType.VOD_ASSET):
                    format = "/shls" +self.channel +"/" +self.levels[self.selected_level]
                else:
                    format = "/shls/LIVE$" +self.channel.strip("LIVE$") +"/" +self.levels[self.selected_level]

            elif (self.profile == AbrSessionProfile.SMOOTH):
                pass


            return method(self,format)
        elif(self.type == AbrSessionType.DYNAMIC):
            if(self.profile == AbrSessionProfile.HLS ):
                return method(self,"/http_adaptive_streaming/" +self.levels[self.selected_level])
            elif (self.profile == AbrSessionProfile.SMOOTH):
                pass
#            self.state = AbrSessionStateEnum.FRAGMENT_LIST_REQUEST_RECEIVED
#            return method(self,"/http_adaptive_streaming/"+self.levels[self.selected_level])

    return request_fragment_list_decorator


def fragment_request_decorator(method):
    def request_fragment_decorator(self):
        format = ""
        if(self.type == AbrSessionType.STATIC):
            if(self.profile == AbrSessionProfile.HLS ):
                if(self.asset_type == AbrAssetType.VOD_ASSET):
                    format = "/shls" +self.channel +"/"+str(cfg.fragment_length)+".m3u8/" + str(self.selected_fragment)
                else:
                    format = "/shls/LIVE$" +self.channel.strip("LIVE$") +"/"+str(cfg.fragment_length)+".m3u8/" + str(self.selected_fragment)
            elif (self.profile == AbrSessionProfile.SMOOTH):
                if(self.asset_type == AbrAssetType.VOD_ASSET):
                    format="/shss" +self.channel.strip("LIVE$")+"/"+str(cfg.fragment_length)+".ism/" +self.levels[self.selected_level] + "/" + str(self.selected_fragment)
                else:
                    format="/shss/LIVE$" +self.channel.strip("LIVE$")+"/"+str(cfg.fragment_length)+".ism/" +self.levels[self.selected_level] + "/" + str(self.selected_fragment)

            return method(self,format)
        elif(self.type == AbrSessionType.DYNAMIC):
            if(self.profile == AbrSessionProfile.HLS ):
                return method(self,self.streamer_url +"/"+str(self.selected_fragment) )
            elif (self.profile == AbrSessionProfile.SMOOTH):
                return method(self,self.streamer_url+self.levels[self.selected_level] +"/"+ str(self.selected_fragment))

    return request_fragment_decorator
