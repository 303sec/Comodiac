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
import calendar
from .bbdb import bbdb
import shlex
import threading
import math
from .util import *
# Not sure if scheduling is needed.
from .scheduling import scheduling


class scoping:
    def __init__(self, company_name, verbose=False):
        self.util = util()
        self.verbose = verbose
        self.company_name = company_name
        if os.path.exists(os.path.expanduser('~') + '/bb') == False:
            self.util.verbose_print(self.verbose, '[+] Creating ~/bb directory')
            os.mkdir(os.path.expanduser('~') + '/bb')
        self.base_dir = os.path.expanduser('~') + '/bb'
        self.company_dir = os.path.expanduser('~/bb/') + self.company_name
        self.add_new_company()
        self.db = bbdb(self.base_dir)

        # to remove, probably: 
        # self.db
        # self.company_dir
        # self.company_name
        # self.base_dir
        # self.verbose -> Should be in every module.
        
    def add_new_company(self):
        if os.path.exists(self.company_dir):
            self.util.verbose_print(self.verbose, '[+] Company directory found')
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
        # Create the table in the company db - we no longer need to do this with the db changes.
        # self.db.create_target_table(target)
        # Avoid any silly dir issues
        target = target.replace('/', '-')
        if wildcard_root == None:
            target_dir = self.company_dir + '/targets/' + target
            target_notes_dir = target_dir + '/notes'
        else:
            target_dir = self.company_dir + '/targets/' + wildcard_root + '/' + target



        #try:
        os.makedirs(target_dir)
        os.makedirs(target_notes_dir)
        self.util.verbose_print(self.verbose, '[+] Creating directory', target_dir)
        self.util.verbose_print(self.verbose, '[+] Creating directory', target_notes_dir)
        self.db.add_target(self.company_name, target, target_dir)
        self.util.verbose_print(self.verbose, '[+] Adding entry for', target ,'to database')

        # It's bad just excepting. Gotta get the right exception type to make this useful!
        #except:
        #    self.util.verbose_print(self.verbose, '[+] Directory', target_dir, 'found.')
        #    pass

    def does_target_exist(self, target):
        if not self.db.get_target_dir(target):
            return False
        elif self.db.get_target_dir(target):
            return True
        else:
            print('Something went unfathomably wrong. Exiting.')
            exit()


    # @param: scope: string: comma deliniated list of targets
    # @param: in_or_out: string: either 'in' or 'out', to determine if it is in or out of scope.
    # @param: file: bool: default=False: set to True if a file is used. It'll be converted to a string
    # @filesystem: adds the new hosts to in_scope_domains/ips.txt, sorts the file by unique entries.
    # @filesystem: adds a directory to company dir for each inscope host.
    # @return parsed_scope: dict: dict with an array for both ip_list and domain_list
    def parse_scope_to_files(self, scope, inscope=True):
        if inscope == True:
            filename_base = self.company_dir + '/scope/inscope'
        else:
            filename_base = self.company_dir + '/scope/outofscope'

        ip_scope_file = filename_base + '_ips.txt'
        domain_scope_file = filename_base + '_domains.txt'
        ip_list = []
        domain_list = []

        for target in scope:
            # Avoids any issues with ip ranges or domain content being added.
            target_no_slash = target.split('/')[0]
            # Checks the TLD or last digits of the IP.
            if self.util.ip_domain_url(target_no_slash) == 'ip':
                ip_list.append(target + '\n')
                # Add IP address to inscope_ips.txt
            else:
                # Hostnames
                domain_list.append(target + '\n')
                # Add domain to inscope_domains.txt


        with open(ip_scope_file, 'a+') as file:
            for ip in ip_list:
                self.util.verbose_print(self.verbose, '[+] Writing IP address', ip.strip(), 'to', ip_scope_file)
                file.write(ip)

        with open(domain_scope_file, 'a+') as file:
            for domain in domain_list:
                self.util.verbose_print(self.verbose, '[+] Writing Domain', domain.strip(), 'to', domain_scope_file)
                file.write(domain)
                
        # Sort both files to only have unique entries
        self.util.uniq_file(ip_scope_file)
        self.util.uniq_file(domain_scope_file)
        self.util.verbose_print(self.verbose, '[+] Sorting scope files by unique values')

        parsed_scope = {'ip_list': ip_list, 'domain_list': domain_list}

        return parsed_scope



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
            self.util.verbose_print(self.verbose, '[+] Writing wildcard domains to wildcard_fragments.txt')
            for domain in parsed_domains['wildcard_domains']:
                # Remove the * in *.xxx.com        
                scannable_domain = domain.replace('*.', '') + '\n'
                # Write scannable wildcard domains to file
                file.write(scannable_domain)
        # Add parsed_domains to the fragment file.
        with open(wildcard_fragment_file, 'a') as file:
            self.util.verbose_print(self.verbose, '[+] Writing wildcard fragments to wildcard_domains.txt')
            for domain in parsed_domains['wildcard_fragments']:
                # Write scannable wildcard domains to file
                file.write(domain + '\n')
                
        # Make sure the files don't have any repeats... also this is not a good way of doing this.
        self.util.verbose_print(self.verbose, '[+] Sorting the wildcard domains & fragments by unique')
        self.util.uniq_file(wildcard_domain_file)
        self.util.uniq_file(wildcard_fragment_file)

        return parsed_domains

    # Scheduling Stuff:

    '''
            id                  INTEGER PRIMARY KEY,
            active              TEXT NOT NULL,
            target              TEXT NOT NULL,
            company             TEXT NOT NULL,
            schedule            TEXT NOT NULL,
            # schedule (cron style?)
            tools               TEXT,
            # Contains a comma delimited list of tools to use. 
            categories          TEXT,
            # Contains a comma delimited list of tools to use from given categories. 
            wordlist            TEXT,
            last_run            DATE,
            last_scan_id        INTEGER,
            input               TEXT NOT NULL,
            intype              TEXT NOT NULL,
            # can be set to either file or asset
            # file = filename = input. asset = every line of file = input.
            outfile             TEXT NOT NULL,
            parser              TEXT NOT NULL,
            meta                TEXT
    '''






'''
Useful snippet to get latest file in dir:
    file_directory = self.company_dir + '/targets/domain/' +  '/' + target + '/' + category + '/' + tool + '/' datetime.today().strftime('%d%m%Y')
    list_of_files = glob.glob(file_directory + '/*')
    latest_file = max(list_of_files, key=os.path.getmtime)

Get the time of a file:
    os.path.getmtime()
'''




