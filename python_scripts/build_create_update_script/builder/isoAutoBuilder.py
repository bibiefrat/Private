import ConfigParser
import os
import shlex
import subprocess
import sys
import pexpect
from datetime import datetime, date, time, timedelta
from itertools import izip

# constants to help the Pexpect module (recongnizing the shell)
COMMAND_PROMPT = '[#$] '
TERMINAL_PROMPT = '(?i)terminal type\?'
TERMINAL_TYPE = 'vt100'
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'
# time out value for the pexpect:
INTERACT_TIMEOUT = 600 # 10 minutes in seconds
BUILD_TIMEOUT = 10800 # 3 hours in seconds
# dictonary to store INI values:
value_dict = {}
# target for ssh:
user = "root"
host = "192.168.100.8"
password = "Pl@tform"
# other global variables:
now_in_time_format = ""
lookback_in_time_format = ""

#################################
# init part :					#
# 1. open variables.ini			#
# 2. get the variables			#
# 3. get the SVN log			#
# 4. check if there's change 	#
#################################

def init():
	variables = ConfigParser.ConfigParser()
	try:
		variables.readfp(open('variables.ini'))
	except IOError:
		print "\nCan't open file, check for variables.ini in the folder\n"
		sys.exit(os.EX_IOERR)
	values = variables.options(variables.sections()[0])
	now = datetime.now()
	global value_dict
	global now_in_time_format
	global lookback_in_time_format
	now_in_time_format = now.strftime('%Y-%m-%dT%H:%M:%SZ')

	# get the INI file into a dictonery so we can refer to it later in the code
	for value in values:
		value_dict[value] = variables.get(variables.sections()[0],value)
		if (value_dict[value] == ""):
			print "\n\"%s attribute has no value, please insert value and run again\n" % value
			sys.exit(os.EX_DATAERR)
			
	# make a start datetime argument from now and the varibles given in file
	offset_time_delta = timedelta(
						days=int(value_dict["look_back_days"]),
						hours=int(value_dict["look_back_hours"]),
						minutes=int(value_dict["look_back_minutes"]))

	offset = now - offset_time_delta
	lookback_in_time_format = offset.strftime('%Y-%m-%dT%H:%M:%SZ')

	#generate the relevant svn log read
	command = "svn log -r {%s}:{%s} http://%s/svn/branches/%s/" % (lookback_in_time_format,now_in_time_format,value_dict["svn_repo_ip"],value_dict["branch"])
	args = shlex.split(command)
	commit_changes = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
	delimiter = "------------------------------------------------------------------------"
	changes = commit_changes.split(delimiter)

	# check for changes in the alotted time:
	if changes[0] == '' and changes[1] == '\n':
		print("\nNo changes to the reposetory between %s and %s no reason to build\n") % (lookback_in_time_format,now_in_time_format)
		sys.exit(os.EX_OK)

#############################
# parse the branch menu		#
# to get the branch number	#
#############################

def parse_branch(log,branch):
	with open(log.name) as f:
		lines = f.readlines()
	for line in lines:
		if branch in line:
			line_prefix = line.split('.')[0]
			return line_prefix
	print "\n Can't find your branch friend (wanted: )\n please check again variables.ini\n" % str(branch)
	sys.exit(os.EX_DATAERR)

def print_out_result(components,results):
	print "\nResults of build session:\n"
	for component, result in izip(components,results):
		print "Component %s : %s" % (component, result)
	print "\nSummary:\n"
	print "Total components success: %d\n" % results.count("successful")
	print "Total components failed: %d\n" % results.count("failed")
	rate = results.count("successful")/len(results)
	rate = rate * 100
	print "Success rate of: %d\n" % rate

#####################################
# use a pexpect spawned process		#
# to interact with remote machine 	#
# in order to make a new build		#
#####################################

def build(child,parsing_log):
	print "starting building"
	child.sendline('/root/scripts/custom_rpm_build/_build_.pl')
	child.expect('username',timeout=INTERACT_TIMEOUT)
	child.sendline(value_dict['myname'])
	child.expect('reason',timeout=INTERACT_TIMEOUT)
	child.sendline(value_dict['myreason'])
	child.expect(value_dict["branch"],timeout=INTERACT_TIMEOUT)
	branch_number = parse_branch(parsing_log,value_dict["branch"])
	child.sendline(branch_number)
	child.expect('Enter revision',timeout=INTERACT_TIMEOUT)
	if value_dict['revision'] == 'latest':
		child.sendline('')
	else:
		child.sendline(value_dict['revision'])
	child.expect('customers',timeout=INTERACT_TIMEOUT)
	child.sendline(value_dict['customers'])
	child.expect('component',timeout=INTERACT_TIMEOUT)
	child.sendline(value_dict['component_list'])

	# building starts, check success and fails output:
	components = value_dict['component_list'].split()
	result_list = []
	num_of_components = len(components)
	for component in components:
		print "\nchecking component number %s," % component
		result = child.expect(['successful','failed'],timeout=BUILD_TIMEOUT)
		if result == 0:
			print "number %s, success" % component
			result_list.append('successful')
		else:
			print "number %s, failed" % component
			result_list.append('failed')

	# child.expect(COMMAND_PROMPT,timeout=BUILD_TIMEOUT)
	print "\nbuild done\n"
	print print_out_result(components,result_list)

#####################################
# connect to remote machine			#
# start a log file for the session	#
# and initiate the build func		#
#####################################

def connect_ssh():
	global COMMAND_PROMPT, TERMINAL_PROMPT, TERMINAL_TYPE, SSH_NEWKEY
	child = pexpect.spawn('ssh -l %s %s' % (user, host))
	builder_log = open('builder_log' + now_in_time_format + '.txt','w')
	child.logfile = builder_log
	parsing_log = open('parsing_log' + now_in_time_format + '.txt','w+')
	child.logfile_read = parsing_log
	i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, COMMAND_PROMPT, '(?i)password'])
	if i == 0: # Timeout
	    print('ERROR! SSH connection timedout - SSH response:')
	    print(child.before, child.after)
	    print(str(child))
	    sys.sys.exit (os.EX_UNAVAILABLE)
	elif i == 1: # In this case SSH does not have the public key cached.
	    child.sendline ('yes')
	    child.expect ('(?i)password')
	elif i == 2:
	    # This may happen if a public key was setup to automatically login.
	    pass
	elif i == 3: 
		# this is what happens most of the time when
		# the connection is proper and it's not the first time
		# we try to connect and there is no public ssh key present
		child.sendline(password)
		# Now we are either at the command prompt or
		# the login process is asking for our terminal type.
		# i = child.expect ([COMMAND_PROMPT, TERMINAL_PROMPT])
		# this is in case for some reason the commnad prompt didnt go up,
		# we send the type of terminal and continue
		if i == 1:
			child.sendline (TERMINAL_TYPE)
			child.expect (COMMAND_PROMPT)
	print "success ssh connection"
	build(child,parsing_log)

def main():
	print "starting init"
	init()
	print "success init"
	print "starting ssh connection"
	connect_ssh()

if __name__ == "__main__":
    main()