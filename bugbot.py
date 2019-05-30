#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import sys
import os
import re
import json
import subprocess
from datetime import datetime

# Refactoring note: I did not know about os.makedirs() when doing this, so there's a bunch of redundant code.

class bugbot:
	def __init__(self, company_name):
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
		return 

	def create_company_db(self):
		# Create the SQLite db
		return 0

	# We run this function on any discovered subdomains / live IP addresses
	# This whole function can do with rewriting, as it turns out making dirs is way easier than I thought.
	def setup_target_folder(self, target, ip_or_domain):
		target = target.replace('/', '-')
		# mkdir ~/bb/COMPANY/targets/domains||ips/TARGET
		target_dir = self.company_dir + '/targets/' + ip_or_domain + 's/' + target

		if os.path.exists(target_dir) == False:
				os.makedirs(target_dir)

		if ip_or_domain == 'domain':
			with open('tools.json', 'r') as tools_file:
				tools = json.loads(tools_file)
				for tool, tool_options in tools.items():
					if tool_options['type'] == 'domain' or tool_options['type'] == 'both':
						if os.path.exists(target_dir + '/' + tool_options['category']):
							os.mkdir(target_dir + '/' + tool_options['category'])
							# Make a folder for the category of scan
			
		elif ip_or_domain == 'ip':
			with open('tools.json', 'r') as tools_file:
				tools = json.load(tools_file)
				for tool, tool_options in tools.items():
					if tool_options['type'] == 'domain' or tool_options['type'] == 'both':
						tool_category_dir = target_dir + '/' + tool_options['category']
						tool_dir = tool_category_dir + '/' + tool
						# Make a folder for the scan, including the category
						os.makedirs(tool_dir)

	# @param scope: string: comma deliniated list of targets
	# @param in_or_out: string: either 'in' or 'out', to determine if it is in or out of scope.
	# @filesystem: adds the new hosts to in_scope_domains/ips.txt, sorts the file by unique entries.
	# @filesystem: adds a directory to company dir for each inscope host.
	# @return parsed_scope: dict: dict with an array for both ip_list and domain_list
	def parse_cli_scope(self, scope, in_or_out='in'):
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
		subprocess.Popen('sort -u ' + domain_scope_file + ' > ' + domain_scope_file + '.tmp && mv ' + domain_scope_file + '.tmp ' + domain_scope_file, shell=True)
		subprocess.Popen('sort -u ' + ip_scope_file + ' > ip_tmp.txt && mv ip_tmp.txt ' + ip_scope_file, shell=True)

		parsed_scope = { 'ip_list': ip_list, 'domain_list': domain_list }

		if in_or_out == 'in':
			return parsed_scope
		else:
			# Probably a bad idea, but why return anything when it's out of scope?
			return {}

	def create_tool_table(self, target, tool, ):
		conn = sqlite3.connect('')
		c = conn.cursor()
		# Create table for scan
		c.execute('''CREATE TABLE ?
             (date text, \
             trans text, \
             symbol text, \
             qty real, \
             price real )''')

	def

	# @param parsed_scope: list: list of parsed hosts. Default = get from local file 
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
				
		# Make sure the files don't have any repeats	
		print('[+] Sorting the wildcard domains & fragments by unique')
		subprocess.Popen('sort -u ' + wildcard_domain_file + ' > ' + wildcard_domain_file + '.tmp && mv ' + wildcard_domain_file + '.tmp ' + wildcard_domain_file, shell=True)	
		subprocess.Popen('sort -u ' + wildcard_fragment_file + ' > ' + wildcard_fragment_file + '.tmp && mv ' + wildcard_fragment_file + '.tmp ' + wildcard_fragment_file, shell=True)	

		return parsed_domains					

	def run_subdomain_enum(self, category, target):
		with open('tools.json', 'r') as tools_file:
			for tool, tool_options in tools.items():
				if category == 'subdomain_enum':
					output_dir = self.company_dir + '/targets/domain/' +  '/' + target + '/' + category + '/' + tool + '/' datetime.today().strftime('%d%m%Y')
					output_file = output_file + '/' + datetime.now().strftime('%H%M%S') + '.txt'
					

		subprocess.Popen('', shell=True)
		# Parse output into db - remove any out of scope 
		# remove previous symlink from /current
		# add new symlink for this scan
		return 




