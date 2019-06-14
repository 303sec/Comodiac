#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import sys
import os
import glob
import re
import json
import subprocess
from datetime import datetime
import time
import bbdb
import shlex
import _thread
 

class bugbot:
	def __init__(self, company_name, target=None):
		self.company_name = company_name
		if os.path.exists(os.path.expanduser('~') + '/bb') == False:
			print('[+] Creating ~/bb directory')
			os.mkdir(os.path.expanduser('~') + '/bb')
		self.base_dir = '~/bb/'
		self.company_dir = os.path.expanduser('~/bb/') + self.company_name
		self.add_new_company()
		
	def add_new_company(self):
		if os.path.exists(self.company_dir):
			print('[+] Company directory found')
			return 
		else:
			os.mkdir(self.company_dir)
			os.mkdir(self.company_dir + '/scope')
			os.mkdir(self.company_dir + '/discovered')
			os.mkdir(self.company_dir + '/targets')
			os.mkdir(self.company_dir + '/targets/ips')
			os.mkdir(self.company_dir + '/targets/domains')
			os.mkdir(self.company_dir + '/notes')
			self.db = bbdb.bbdb(self.company_name, self.company_dir)
		return 

	# This function has been basically tested, but not much. Seems to work.
	def ip_or_domain(self, target):
		if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', target):
			print('[+]', target, 'identified as IP address.')
			return 'ip'
		elif re.match('([a-z0-9|-]+\.)*[a-z0-9|-]+\.[a-z]+', target):
			print('[+]', target, 'identified as domain name.')
			return 'domain'
		else:
			return None


	# We run this function on any discovered subdomains / live IP addresses
	# @filesystem: writes all the relevant tools to the ip or domain folder in the given target
	# @param: target: string: the name of the target in which to create the folder for. If wildcard!=false, then this is the host target.
	# @param: wildcard_root: string: default=None: a sting of the discovered subdomain to be initialised, using target as the 'host' .

	# This function needs some work, and is important:
	# Needs to:
	'''
	- Create the directory in the correct place (if it's discovered from a wildcard in the host, give the top-level dir.)
	- Create database for the target in the dir
	- Add target to discovered_hosts.txt
	- (maybe) add target to a base db.
	'''
	def add_new_target(self, target, wildcard_root=None):
		# Create the table in the company db
		self.db.create_target_table(target)
		# Avoid any silly dir issues
		target = target.replace('/', '-')
		if wildcard_root == None:
			target_dir = self.company_dir + '/targets/' + self.ip_or_domain(target) + 's/' + target
		else:
			target_dir = self.company_dir + '/targets/' + self.ip_or_domain(target) + 's/' + wildcard_root + '/' + target

		if os.path.exists(target_dir) == False:
				os.makedirs(target_dir)



		# This whole part feels redundant, like it'd surely be done when the scan runs?
		# Still might be a useful snippet, so I haven't deleted it.
		'''
		if '*' in target or '*' in wildcard:
			with open('tools.json', 'r') as tools_file:
				tools = json.load(tools_file)
				for tool, tool_options in tools.items():
					if tool_options['type'] == ip_or_domain(target) or tool_options['type'] == 'both':
						tool_category_dir = target_dir + '/' + tool_options['category']
						tool_dir = tool_category_dir + '/' + tool
						# Make a folder for the scan, including the category
						os.makedirs(tool_dir)
		'''



	# @param: scope: string: comma deliniated list of targets
	# @param: in_or_out: string: either 'in' or 'out', to determine if it is in or out of scope.
	# @param: file: bool: default=False: set to True if a file is used. It'll be converted to a string
	# @filesystem: adds the new hosts to in_scope_domains/ips.txt, sorts the file by unique entries.
	# @filesystem: adds a directory to company dir for each inscope host.
	# @return parsed_scope: dict: dict with an array for both ip_list and domain_list
	def parse_cli_scope(self, scope, in_or_out='in', file=False):
		# Bit of a hack to get the file formatted like the comma-demlimited input.
		if file == True:
			tmp_scope = []
			with open(scope, 'r+') as scope_file:
				for line in scope_file:
					line = line.strip()
					tmp_scope.append(line + ',')
			scope = ''.join(tmp_scope)

		scope_array = scope.split(',')
		filename_base = self.company_dir + '/scope/' + in_or_out + 'scope'
		ip_scope_file = filename_base + '_ips.txt'
		domain_scope_file = filename_base + '_domains.txt'
		ip_list = []
		domain_list = []

		for target in scope_array:
			# Avoids any issues with ip ranges or domain content being added.
			target_no_slash = target.split('/')[0]
			# Checks the TLD or last digits of the IP.
			if target_no_slash.split('.')[-1].isdigit():
				# IP addresses
				ip_list.append(target)
				# Add IP address to inscope_ips.txt
				with open(ip_scope_file, 'a') as file:
					file.write(target + '\n')
				print('[+] Writing IP address ' + target + ' to scope')
			else:
				# Hostnames
				domain_list.append(target)
				# Add domain to inscope_domains.txt
				with open(domain_scope_file, 'a') as file:
					file.write(target + '\n')
				print('[+] Writing domain ' + target + ' to scope')

		# Sort both files to only have unique entries
		print('[+] Sorting scope files by unique values')

		# Honestly, this bit below needs fixing to be honest. Maybe write a function to do this.
		subprocess.Popen('sort -u ' + domain_scope_file + ' > ' + domain_scope_file + '.tmp && mv ' + domain_scope_file + '.tmp ' + domain_scope_file, shell=True)
		subprocess.Popen('sort -u ' + ip_scope_file + ' > ip_tmp.txt && mv ip_tmp.txt ' + ip_scope_file, shell=True)

		parsed_scope = { 'ip_list': ip_list, 'domain_list': domain_list }

		if in_or_out == 'in':
			return parsed_scope
		else:
			# Probably a bad idea, but why return anything when it's out of scope?
			return {}


	# @param parsed_scope: list: list of parsed hosts. Default = get from local file 
	# @filesystem: add the wildcards to the 'wildcard_domains.txt' file
	def parse_wildcard_domains(self, parsed_scope=None):
		in_scope_domains = self.company_dir + '/scope/inscope_domains.txt'
		wildcard_domain_file = self.company_dir + '/scope/wildcard_domains.txt'
		wildcard_fragment_file = self.company_dir + '/scope/wildcard_fragments.txt'
		wildcard_domains = []
		wildcard_fragments = []
		if parsed_scope == None:
			# Parse all from inscope domain file
			with open(in_scope_domains, 'r') as file:
				for domain in file:
					if '*' in domain:
						split_domain = domain.split('.')
						for part in split_domain:
							if part == '*':
								wildcard_domains.append(domain)
								break
							elif '*' in part:
								wildcard_fragments.append(domain)
								break	
			parsed_domains = {'wildcard_domains': wildcard_domains, 'wildcard_fragments': wildcard_fragments}
		else:
			for domain in parsed_scope:
				if '*' in domain:
					split_domain = domain.split('.')
					for part in split_domain:
						if part == '*':
							wildcard_domains.append(domain)
							break
						elif '*' in part:
							wildcard_fragments.append(domain)
							break	
			parsed_domains = {'wildcard_domains': wildcard_domains, 'wildcard_fragments': wildcard_fragments}	

		# Add parsed_domains to the wildcard file, and make them 'scannable'
		with open(wildcard_domain_file, 'a') as file:
			print('[+] Writing wildcard domains to wildcard_fragments.txt')
			for domain in parsed_domains['wildcard_domains']:
				# Remove the * in *.xxx.com		
				scannable_domain = domain.replace('*.', '') + '\n'
				# Write scannable wildcard domains to file
				file.write(scannable_domain)
		# Add parsed_domains to the fragment file.
		with open(wildcard_fragment_file, 'a') as file:
			print('[+] Writing wildcard fragments to wildcard_domains.txt')
			for domain in parsed_domains['wildcard_fragments']:
				# Write scannable wildcard domains to file
				file.write(domain + '\n')
				
		# Make sure the files don't have any repeats... also this is not a good way of doing this.
		print('[+] Sorting the wildcard domains & fragments by unique')
		subprocess.Popen('sort -u ' + wildcard_domain_file + ' > ' + wildcard_domain_file + '.tmp && mv ' + wildcard_domain_file + '.tmp ' + wildcard_domain_file, shell=True)	
		subprocess.Popen('sort -u ' + wildcard_fragment_file + ' > ' + wildcard_fragment_file + '.tmp && mv ' + wildcard_fragment_file + '.tmp ' + wildcard_fragment_file, shell=True)	

		return parsed_domains

	# Need to create a scan dict containing:
	# scan['id'] = target, scan name & timestamp concatenated
	# scan['tool']
	# scan['command']
	# scan['started']
	# scan['pid'] - Later 
	# scan['status'] 
	def run_tools_by_category(self, category, target, wordlist='default'):
		with open('tools.json', 'r') as tools_file:
			for tool, tool_options in tools.items():
				if category == tool_options['category']:
					output_dir = self.company_dir + '/targets/' + self.ip_or_domain(target) +  '/' + target + '/' + category + '/' + tool + '/' + datetime.today().strftime('%d%m%Y')
					output_file = output_dir + '/' + tool + '.' + time.time()
					# Check that the tool actually uses a wordlist
					if 'WORDLIST' in tool_options['command']:
						# If no wordlist supplied, use the wordlist given as a param
						if wordlist == 'default':
							wordlist = tool_options['wordlist']
					# Replaces the placeholders in the scan.
					command = tool_options['command'].replace('INPUT', target).replace('OUTPUT', output_file).replace('WORDLIST', wordlist)
					# This should really popen another command, not call exec(). For the time being though (and testing) it stays.
					scan_id = target.strip() + tool + datetime.timestamp(datetime.now())
					scan_data = {'category': category, 'tool': tool, 'command': command, 'output': output_file, 'scan_id': scan_id, 'status': 'waiting'}
					# Add the scan to db (before the threading stuff comes into play)
					self.db.add_scan(target, scan)
					# This should launch the command into a different thread!
					_thread.start_new_thread(run_cmd, (target, scan_data))

		return 

	# scan_data:
	#	scan_id
	# 	tool
	# 	category
	# 	command
	# 	output
	#	pid
	#	status
	#	id
	#
	#


	def run_cmd(target, scan:dict):
		# This command will essentially be run as it's own process via _thread
		# Need a scan dict containing:
		# scan['id'] = target, scan name & timestamp concatenated
    	# scan['tool']
    	# scan['command']
    	# scan['started']
    	# scan['pid'] - Later 
    	# scan['status'] 
    	
    	
		process = subprocess.Popen(shlex.split(scan_data['command']), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		# Below could be used later for printing output to web interface.
		output = process.stdout.read()
		scan['pid'] = process.pid
		scan['status'] = 'started'
		scan['started'] = datetime.timestamp(datetime.now())
		self.db.start_scan(target,scan)
		# blocks processing until command is complete
		stdout, stderr = process.communicate()

		if process.returncode != 0:
			scan['status'] = 'error'

		# Now we need to read the output file and parse it accordingly.
		'''

		TODO

		outfile_assets = self.parse_output_file(scan['output'], scan['tool'])
		bbdb.add_asset() # for each asset
		bbdb.add_assets() # List of tuples
		'''
		# Parse output into db - remove any out of scope 
		# remove previous symlink from /current
		# add new symlink for this scan

		return result 


		#0 - Have an 'executor' script/CLI functionality to handle scans/processes, doing the following:
		#1 - Adds scan info to the target db in a table called 'live_scans' or something equally appropriate.
		#1 - Uses a blocking Popen, starttime/scan endtime PID and any errors. 
		#2 - The followng is a rough idea for the live_scans table:
		#	 id:                   PRIMARY KEY
		#    scan_name:            TEXT NOT NULL
		#    scan_command:         TEXT NOT NULL
		#    scan_started:         DATE NOT NULL
		#    scan_completed:	   DATE
		#    scan_pid:			   TEXT NOT NULL
		#    scan_status:		   TEXT NOT NULL
		#
		#3 - scan_status can be:
		#waiting
		#running
		#completed
		#error
		#parsed
		#(more can be added if needed)
		#
		#4 - Once a scan is complete, it parses the output of the scans within the script with the BB functionality.
		#5 - Once scan is completed and parsed, runs a bb_alert tool to look over database history and see if there has been any change.
		#6 - Quite likely worth having slack chats dedicated to progress monitoring - like a room for errors, a room for completed scans, a room for started scans.
		#7 - Can take an input of multiple tools at once, to run them all in a blocking fashion in a loop to keep processing down.
		#8 - Possible later feature: run scans as either blocking or async!


					
		


	# Should return a list of tuples ready for putting into the database.
	def parse_output_file(self, file, tool):
		with open('tools.json', 'r') as tools_file:
			for tool_name, tool_options in tools_file.items():
				if tool_name == tool:
					file_directory = self.company_dir + '/targets/domain/' +  '/' + target + '/' + category + '/'
					with open(target):
						re.findall(tool_options['parse_result'])
			# os.path.getmtime = Check the time the file was edited last.
						

'''
Useful snippet to get latest file in dir:
	file_directory = self.company_dir + '/targets/domain/' +  '/' + target + '/' + category + '/' + tool + '/' datetime.today().strftime('%d%m%Y')
	list_of_files = glob.glob(file_directory + '/*')
	latest_file = max(list_of_files, key=os.path.getmtime)

Get the time of a file:
	os.path.getmtime()
'''




