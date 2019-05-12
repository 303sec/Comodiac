#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import sys
import os
import re
import subprocess

class scope_parser:
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
		return 

	def create_company_db(self):
		# Create the SQLite db
		return 0


	# @param scope: string: comma deliniated list of targets
	# @param in_or_out: string: either 'in' or 'out', to determine if it is in or out of scope.
	# @filesystem: adds the new hosts to in_scope_domains/ips.txt, sorts the file by unique entries.
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
				with open(ip_scope_file, 'a') as file:
					file.write(target + '\n')
				print('[+] Writing IP address ' + target + ' to scope')
			else:
				# Hostnames
				domain_list.append(target)
				with open(domain_scope_file, 'a') as file:
					file.write(target + '\n')
				print('[+] Writing domain ' + target + ' to scope')


		# Sort both files to only have unique entries
		print('[+] Sorting scope files by unique values')
		subprocess.Popen('sort -u ' + domain_scope_file + ' > ' + domain_scope_file + '.tmp && mv ' + domain_scope_file + '.tmp ' + domain_scope_file)
		subprocess.Popen('sort -u ' + ip_scope_file + ' > ip_tmp.txt && mv ip_tmp.txt ' + ip_scope_file)

		parsed_scope = { 'ip_list': ip_list, 'domain_list': domain_list }

		if in_or_out == 'in':
			return parsed_scope
		else:
			# Probably a bad idea, but why return anything when it's out of scope?
			return {}

	# @param parsed_scope: list: list of parsed hosts. Default = get from local file 
	def parse_wildcard_domains(self, parsed_scope=None):
		in_scope_domains = self.company_dir + '/scope/inscope_domains.txt'
		wildcard_domains = []
		wildcard_fragments = []
		if parsed_scope == None:
			# Parse all from inscope domain file
			with open(in_scope_domains, 'r') as file:
				for domain in domains:
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
			return parsed_domains
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
			return parsed_domains


	def parse_ip_range(self):
		# Pretty sure I don't actually need to do this :D
		return



