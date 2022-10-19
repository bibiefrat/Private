import requests
import sys
import json
import datetime
import time

class CreateIso(object):
	def __init__(self, version, url="http://192.168.5.58:8080/api"):
		self.url = url
		self.time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
		self.version = version
		self.brand = "Fabrix"
		self.OS = "CENTOS"
		self.OsVersion = "6.6"

	# input : None
	# output : meta data in JSON format, matching the version given to class instance
	def getMetaData(self):
		req_url = '/iso_metadata/filter'
		req_body = {"StartRange" : self.version,"EndRange" : self.version}
		full_url = "%s%s" % (self.url,req_url)
		print "retrieving iso meta data infromation from ISO server,"
		response =  requests.post(full_url, json=req_body)
		print "Response: %s" % str(response.status_code)
		if response.status_code != 200:
			msg ="\nISO meta data request failed. exiting.\n"
			sys.exit(msg)
		json_data = response.json()
		return json_data

	# input : meta_data, should be in JSON format.
	# output : an ID number for which ISO type to create [[VERSION]/fabrix/centos/6.6]
	def getId(self,meta_data):
		for entry in meta_data:
			DataVersion = entry['Version']
			DataBrand = entry['Brand']['ShortName']
			DataOS = entry['OsMetaData']['Type']['ShortName']
			DataOsRevision = entry['OsMetaData']['Revision']
			DataOsVersion = entry['OsMetaData']['Version']
			if  DataVersion== self.version and DataBrand == self.brand and \
				DataOS == self.OS and "%s.%s" % (DataOsRevision,DataOsVersion) == "6.6":
				buildId = entry['Id']
		return buildId

	# input : ID number of the ISO type we want to create
	# output : ID number of the actual ISO we have created (added to list)
	def send_create_request(self,buildId):
		req_url = '/iso/create/%s' % buildId
		body = "auto_%s" % self.time
		req_body = {"Comment":body}
		full_url = "%s%s" % (self.url,req_url)
		print "sending new ISO create request to server,"
		response = requests.post(full_url, json=req_body)
		print "Response: %s" % str(response.status_code)
		if response.status_code != 200:
			msg ="\nISO create request failed. exiting."
			sys.exit(msg)
		json_data = response.json()
		iso_id = json_data['Id']
		return iso_id

	# input : ID number of the ISO instance we want to build 
	# output : paths to SWRawPath, OSRawPath
	def send_build_request(self,iso_id):
		req_url = '/iso/build/none/%s' % iso_id
		full_url = "%s%s" % (self.url,req_url)
		print "sending new ISO build request to server,"
		response = requests.get(full_url)
		print "Response: %s" % str(response.status_code)
		if response.status_code != 200:
			msg ="\nISO build request failed. exiting.\n"
			sys.exit(msg)
		json_data = response.json()
		SWRawPath = json_data['RawPath']
		OSRawPath = json_data['OsRawPath']
		return [SWRawPath,OSRawPath]

	# input : ID number of the ISO instance
	# output : return [4]-"Ready" or [6]-"Aborted" when the ISO is done proccesing 
	def send_status_request(self,iso_id):
		req_url = '/iso/status/%s' % iso_id
		full_url = "%s%s" % (self.url,req_url)
		response = requests.get(full_url)
		if response.status_code != 200:
			msg ="\nISO status request failed. exiting."
			sys.exit(msg)
		json_data = response.json()
		status = json_data['State']
		return status

	# this method runs as long as the ISO is not done proccesing,
	# input : ID number of the ISO instance
	# output : return [4]-"Ready" or [6]-"Aborted" when the ISO is done proccesing 
	def check_status(self,iso_id):
		status = -1
		while (status != 4 and status != 6):
			status = self.send_status_request(iso_id)
			print "status : %s" % status
			time.sleep(20)
		return status