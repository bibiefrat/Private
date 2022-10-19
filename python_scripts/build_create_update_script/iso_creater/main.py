import re
import os
import sys

from AutoBuildISO import CreateIso

# input:
# if more then 1 argument, or no arguments, exit code
def get_version():
	args = sys.argv
	num_of_args = len(sys.argv)
	if num_of_args != 2:
		msg = "\ni only need one argument, you gave me : %s\n" % (num_of_args-1)
		sys.exit(msg)
	return args[1]

def validate_version(version):
	creatorObj = CreateIso("")
	json_data = creatorObj.getMetaData()
	version_list = []
	for meta_data in json_data:
		version_list.append(meta_data['Version'])
	if version not in version_list:
		msg ="\nInput was invalid and i don't know what version that is\n"
		sys.exit(msg)
	return True

def main():
    version = get_version()
    valid = validate_version(version)
    creatorObj = CreateIso(version)
    meta_data = creatorObj.getMetaData()
    buildId = creatorObj.getId(meta_data)
    isoId = creatorObj.send_create_request(buildId)
    paths = creatorObj.send_build_request(isoId)
    status = creatorObj.check_status(isoId)
    if status == 4:
    	print "ISO ready to be loaded to machines"
    	sys.exit(0)

if __name__ == "__main__":
    main()