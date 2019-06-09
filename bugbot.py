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
# Refactoring note: I did not know about os.makedirs() when doing this, so there's a bunch of redundant code.

class bugbot:
	def __init__(self, company_name, target=None):
		self.company_name = company_name
		if os.path.exists(os.path.expanduser('~') + '/bb') == False:
			print('[+] Creating ~/bb directory')
			os.mkdir(os.path.expanduser('~') + '/bb')
		self.base_dir = '~/bb/'
		self.company_dir = os.path.expanduser('~/bb/') + self.company_name
		self.add_new_company()
		if target != None:
			self.bbdb = bbdb.bbdb(self.company_dir, target)

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
	# This param has been replace with a function. @param: ip_or_domain: string: either 'ip' or 'domain', depending on what type the target is.
	# @param: wildcard: string: default=None: a sting of the discovered subdomain to be initialised, using target as the 'host' .

	# This function needs some work, and is important:
	# Needs to:
	'''
	- Create the directory in the correct place (if it's discovered from a wildcard in the host, give the top-level dir.)
	- Create database for the target in the dir
	- Add target to discovered_hosts.txt
	- (maybe) add target to a base db.
	'''
	def setup_target_folder(self, target, wildcard=None):
		target = target.replace('/', '-')
		# mkdir ~/bb/COMPANY/targets/domains||ips/TARGET
		if wildcard == None:
			target_dir = self.company_dir + '/targets/' + ip_or_domain(target) + 's/' + target
		target_dir = self.company_dir + '/targets/' + ip_or_domain(target) + 's/' + target + '/' + wildcard

		if os.path.exists(target_dir) == False:
				os.makedirs(target_dir)

		# This whole part feels redundant, like it'd surely be done when the scan runs?
		# Still might be a useful snippet.
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
				
		# Make sure the files don't have any repeats... this is not a good way of doing this.
		print('[+] Sorting the wildcard domains & fragments by unique')
		subprocess.Popen('sort -u ' + wildcard_domain_file + ' > ' + wildcard_domain_file + '.tmp && mv ' + wildcard_domain_file + '.tmp ' + wildcard_domain_file, shell=True)	
		subprocess.Popen('sort -u ' + wildcard_fragment_file + ' > ' + wildcard_fragment_file + '.tmp && mv ' + wildcard_fragment_file + '.tmp ' + wildcard_fragment_file, shell=True)	

		return parsed_domains

	def run_tools_by_category(self, category, target, wordlist='default'):
		with open('tools.json', 'r') as tools_file:
			for tool, tool_options in tools.items():

				if category == tool_options['category']:
					output_dir = self.company_dir + '/targets/' + self.ip_or_domain(target) +  '/' + target + '/' + category + '/' + tool + '/' + datetime.today().strftime('%d%m%Y')
					output_file = output_dir + '/' + tool + '.' + time.time()
					# Check that the tool actually uses a wordlist
					if 'WORDLIST' in tool_options['command']:
						# If not wordlist supplied, use the wordlist in the 
						if wordlist == 'default':
							wordlist = tool_options['wordlist']
					# Replaces the placeholders in the scan.
					command = tool_options['command'].replace('INPUT', target).replace('OUTPUT', output_file).replace('WORDLIST', wordlist)
					# Runs the process in the background, no output or input in the script
					exec(command)
		# Parse output into db - remove any out of scope 
		# remove previous symlink from /current
		# add new symlink for this scan
		return 

	def exec(command):
		# This command will essentially be run as it's own process.
		# Executing commands: Most Important!
		# We need to make sure there are no errors from the shell command.
		# This can be achieved by checking there's nothing in the STDERR (possibly) and that it returns a status code of 0.
		# Needs to be non-blocking. All of the processes need to be run with Popen, and then polled for when they return success
		# Possibly need to use async/await? 
		# Probably worth creating a table in either a company or root db to store process PIDs to keep track of processes.
		# Could also just have it blocking. Why not? Probably a good way of not completely overwhelming everything. 
		process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



		return result 
					
		



	def parse_output_file(self, target, file, tool):
		with open('tools.json', 'r') as tools_file:
			for tool_name, tool_options in tools_file.items():
				if tool_name == tool:
					file_directory = self.company_dir + '/targets/domain/' +  '/' + target + '/' + category + '/'
					with open(target):
						re.findall(tool_options['parse_result'])
						

'''
Useful snippet to get latest file in dir:
	file_directory = self.company_dir + '/targets/domain/' +  '/' + target + '/' + category + '/' + tool + '/' datetime.today().strftime('%d%m%Y')
	list_of_files = glob.glob(file_directory + '/*')
	latest_file = max(list_of_files, key=os.path.getmtime)

Get the time of a file:
	os.path.getmtime()
'''




