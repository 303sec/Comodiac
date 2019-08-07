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


class scheduling:
    def __init__(self, verbose=False):
        self.util = util()
        self.verbose = verbose
        self.base_dir = os.path.expanduser('~') + '/bb'
        self.db = bbdb(self.base_dir)
        return

    # @param: info: dict: A dictionary of relevant information about the schedule, including:
    #
    # schedule['active']: default = 1
    # schedule['target']: required by CLI.
    # schedule['company']: self.company
    # schedule['schedule_interval']: default: 86400 (daily). Provided by CLI.
    # schedule['tool']: name of the tool (or category, if use_category == 1) required by CLI. 
    # schedule['use_category']: 1 if the scan is a category of tools (or just one). In the CLI, this can be used with --category

    # schedule['wordlist']: default: the wordlist in tools.json
    # schedule['input']: if 'intype' == file, use this input. From tools.json
    # schedule['intype']: 'file' or 'target'. If file, use the supplied 'input', which should be available in tools.json
    # schedule['outfile']: output file for the tool. Does this need to be here? This has confused me! ????!!!???? 
    # schedule['parser']: the parser regular expression to use on the output file. From tools.json
    # schedule['meta']: any extra functions to perform post-scan. From tools.json
    #
    # Main use is to parse stuff out of tools.json and add it to the schedule table.
    def add_schedule(self, info:dict):

        with open('tools.json', 'r') as tools_file:
            tool_found = False
            tools = json.loads(tools_file.read())
            for tool_name, tool_options in tools.items():
                if tool_name == info['tool'] or tool_options['category'] == info['tool']:

                    '''
                        id                  INTEGER PRIMARY KEY,
                        active              INTEGER NOT NULL,
                        target              TEXT NOT NULL,
                        company             TEXT NOT NULL,
                        schedule_interval   TEXT NOT NULL,
                        schedule_uuid       TEXT NOT NULL,
                        tool                TEXT,
                        last_run            DATE,
                        last_scan_id        INTEGER,
                        input               TEXT NOT NULL,
                        intype              TEXT NOT NULL,
                        informat            TEXT NOT NULL,
                        output              TEXT NOT NULL,
                        outtype             TEXT NOT NULL,
                        outformat           TEXT NOT NULL,
                        outfile             TEXT,
                        wordlist            TEXT,
                        wordlist_file       TEXT,
                        wordlist_input      TEXT,
                        wordlist_informat   TEXT,
                        parser              TEXT NOT NULL,
                        filesystem          TEXT
                    '''


                    tool_found = True
                    if 'wordlist' in tool_options:
                        wordlist = tool_options['wordlist']
                    else:
                        wordlist = None
                    if tool_options['intype'] == 'file':
                        schedule_input = tool_options['input']
                    else:
                        schedule_input = target


                    schedule['active'] = 1
                    
                    schedule['target'] = info['target']
                    schedule['company'] = info['company']
                    schedule['schedule_interval'] = info['schedule_interval']
                    schedule['uuid'] = str(uuid.uuid4())
                    schedule['tool'] = info['tool']

                    schedule['intype'] = tool_options['intype']
                    schedule['informat'] = tool_options['informat']
                    schedule['input'] = tool_options['input']
                    schedule['outtype'] = tool_options['outtype']
                    schedule['outformat'] = tool_options['outformat']
                    schedule['output'] = tool_options['output']
                    schedule['parser'] = tool_options['parse_result']
                    schedule['meta'] = tool_options['meta']
                    



                    schedule = {'active': 1, 'target': target, 'company': company, 'schedule_interval': schedule_interval, \
                    'tool': tool, 'use_category': use_category, 'wordlist': wordlist, 'input': schedule_input, 'intype':intype, \
                    'parser':parser, 'meta': meta, 'alert': alert, 'uuid': schedule_uuid}
                    scheduler.add_schedule(schedule)
        if tool_found == False:
            click.echo('[-] Tool not found.')



        self.util.verbose_print('[+] Adding schedule to database')
        self.db.add_schedule(info)
        return 0

    def get_schedule(self, company, target=None, schedule_id=None, all=None):
        if target is None and schedule_id is None:
            results = self.db.get_schedule_by_company(company)
        elif target is not None and schedule_id is None:
            results = self.db.get_schedule_by_target(target)
        elif schedule_id is not None and target is None:
            results = self.db.get_schedule_by_id(schedule_id)
        else:
            return -1
        parsed_table_list = []
        parsed_table_headers = []

        if results:
            # Get the header array
            for key, item in results[0].items():
                parsed_table_headers.append(key)

            parsed_table_list.append(parsed_table_headers)

            for result in results:
                result_list = []
                for key, item in results[0].items():
                    result_list.append(item)
                parsed_table_list.append(result_list)

            return parsed_table_list
        else:
            print('No schedule found. Exiting.')
            exit()
        
    # function not completed
    def immediate_scan(self, company, target, tool, schedule_id=None):
        if schedule_id:
            schedule = self.db.get_schedule_by_id(schedule_id)
            if not schedule:
                self.util.verbose_print(True, '[-] No schedules with that ID found. Exiting.')
                exit()
            else:
                return


    def heartbeat(self):
        all_schedules = self.db.get_active_schedules()
        print('all_active_schedules:', all_schedules)
        for schedule in all_schedules:
            if schedule['last_run'] == None:
                last_run = 0
            else:
                last_run = schedule['last_run']
            time_since_last_run = self.util.timestamp() - last_run
            interval = schedule['schedule_interval']
            if not isinstance(interval, int):
                interval = self.util.parse_interval(interval)
            print(time_since_last_run, interval)

            if schedule['last_run'] == None or int(interval) < int(time_since_last_run):
                # If it hasn't been run before, run it! (assuming empty last_run = None)
                # If the differnce between the last scan and now is greater than the interval, run it! 
                # if use_categories == 1, then the tool item contains the category name.
                # The db only contains 1 tool or category per run now, not a comma delimited list.
                if schedule['wordlist'] != None:
                    wordlist = 'default'
                else:
                    wordlist = schedule['wordlist']

                if schedule['use_category'] == 0:            
                    self.prepare_tool(schedule['tool'], schedule['company'], schedule['target'], wordlist)
                elif schedule['use_category'] == 1:
                    self.run_tools_by_category(schedule['tool'],  schedule['company'], schedule['target'], wordlist)
                else:
                    self.util.verbose_print('this should not ever happen.')
        return 0












    # Not sure running by category is too important. 


    # @param: category: string: categroy of the scan, to be parsed from tools.json
    # @param: target: string: the name of the target
    # @param: wordlist: string: default='default': path to a wordlist, if applicable.
    # @thread: starts new thread running the run_cmd function.
    # @return: 0 for success
    def run_tools_by_category(self, category, target, wordlist='default'):
        with open('tools.json', 'r') as tools_file:
            tools = json.loads(tools_file.read())
            for tool, tool_options in tools.items():
                if category == tool_options['category']:
                    output_dir = self.company_dir + '/targets/' + '/' + target + '/' + category + '/' + tool + '/' + datetime.today().strftime('%d%m%Y')
                    try:
                        os.makedirs(output_dir)
                    except:
                        self.util.verbose_print('[+] Directory', output_dir, 'found.')
                        pass
                    output_file = output_dir + '/' + tool + '.' + str(self.util.timestamp())
                    # Check that the tool actually uses a wordlist
                    if 'WORDLIST' in tool_options['command']:
                        # If no wordlist supplied, use the wordlist given as a param
                        if wordlist == 'default':
                            wordlist = tool_options['wordlist']
                    # Replaces the placeholders in the scan.
                    command = tool_options['command'].replace('INPUT', target).replace('OUTPUT', output_file).replace('WORDLIST', wordlist)
                    # This should really popen another command, not call exec(). For the time being though (and testing) it stays.
                    scan_id = target.strip() + tool + str(self.util.timestamp())
                    scan_data = {'category': category, 'tool': tool, 'command': command, 'output': output_file, 'scan_id': scan_id, 'status': 'waiting'}
                    # Add the scan to db (before the threading stuff comes into play)
                    self.db.add_scan(target, scan)
                    # This should launch the command into a different thread!
                    threading.Thread(target=self.run_cmd, args=(target, scan_data)).start()
        return 0


    # @param: tool_name: string: name of the scan, to be parsed from tools.json
    # @param: target: string: the name of the target
    # @param: wordlist: string: default='default': path to a wordlist, if applicable.
    # @thread: starts new thread running the run_cmd function.
    # @return: 0 for success
    def run_tool(self, tool_name, company, target, wordlist='default'):
        with open('tools.json', 'r') as tools_file:
            tools = json.loads(tools_file.read())
            for tool, tool_options in tools.items():
                if tool_name == tool:
                    output_dir = self.base_dir + '/' + company + '/targets/' target + '/' + tool_options['category'] + '/' + tool + '/' + str(datetime.today().strftime('%d%m%Y'))
                    try:
                        os.makedirs(output_dir)
                        self.util.verbose_print('[+] Creating directory', output_dir, '.')
                    except:
                        self.util.verbose_print('[+] Directory', output_dir, 'found.')
                        pass
                    output_file = output_dir + '/' + tool + '.' + str(self.util.timestamp())
                    # Check that the tool actually uses a wordlist
                    if 'WORDLIST' in tool_options['command']:
                        # If no wordlist supplied, use the wordlist given as a param
                        if wordlist == 'default':
                            wordlist = tool_options['wordlist']
                    else:
                        wordlist = ''
                    # Replaces the placeholders in the scan.
                    command = tool_options['command'].replace('INPUT', target).replace('OUTPUT', output_file).replace('WORDLIST', wordlist)
                    # This should really popen another command, not call exec(). For the time being though (and testing) it stays.
                    scan_id = target.strip() + tool + str(self.util.timestamp())
                    scan_data = {'category': tool_options['category'], 'tool': tool, 'command': command, 'output': output_file, 'scan_id': scan_id, 'status': 'waiting'}
                    # Add the scan to db (before the threading stuff comes into play)
                    self.util.verbose_print('[+] Adding scan to database.')
                    self.db.add_scan(company, target, scan_data)
                    # This should launch the command into a different thread!
                    self.util.verbose_print('[+] Starting new thread for scan.')
                    #self.run_cmd(target, scan_data)
                    # Python3's way of threading
                    threading.Thread(target=self.run_thread_cmd, args=(company, target, scan_data)).start()
        return 0


    def prepare_tool(self, schedule_id):
        '''

        '''



    # Never accessed directly - run through threading.thread in run_tool*
    # @param: target: string: target name
    # @param: scan: dict: 
    def run_thread_cmd(self, company, target, scan:dict):
        # This command will essentially be run as it's own process via threading
        # Need a scan dict containing:
        # scan['id'] = target, scan name & timestamp concatenated
        # scan['tool']
        # scan['command']
        # scan['started']
        # scan['pid'] - Later 
        # scan['status'] 

        company_dir = self.base_dir + '/' + company
        
        process = subprocess.Popen(shlex.split(scan['command']), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Below could be used later for printing output to web interface.
        scan['pid'] = process.pid
        scan['status'] = 'started'
        scan['started'] = self.util.timestamp()
        self.db.start_scan(company, target, scan)
        # blocks processing until command is complete
        stdout, stderr = process.communicate()
        

        if process.returncode != 0:
            scan['status'] = 'error'
            scan['completed'] = ''
        else:
            scan['status'] = 'completed'
            scan['completed'] = self.util.timestamp()

        self.db.scan_complete(company, target, scan)

        outfile_assets = self.util.parse_output_file(target, scan['category'], company_dir, scan['output'], scan['tool'])

        #self.db.add_asset() # for each asset
        #self.db.add_assets() # List of tuples
        '''
        # Parse output into db - remove any out of scope (or set to ignore)
        # remove previous symlink from /current
        # add new symlink for this scan

        return 0 


        #0 - Have an 'executor' script/CLI functionality to handle scans/processes, doing the following:
        #1 - Adds scan info to the target db in a table called 'live_scans' or something equally appropriate.
        #1 - Uses a blocking Popen, starttime/scan endtime PID and any errors. 
        #2 - The followng is a rough idea for the live_scans table:
        #     id:                  PRIMARY KEY
        #    scan_name:            TEXT NOT NULL
        #    scan_command:         TEXT NOT NULL
        #    scan_started:         DATE NOT NULL
        #    scan_completed:       DATE
        #    scan_pid:             TEXT NOT NULL
        #    scan_status:          TEXT NOT NULL
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
        '''


 