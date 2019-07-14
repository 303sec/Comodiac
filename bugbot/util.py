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

class util:
    def __init__(self):
        return

    # This function has been basically tested, but not much. It returns none when it doesn't know, which is bad!
    def ip_domain_url(self, target):
        if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', target):
            self.verbose_print('[+]', target, 'identified as IP address.')
            return 'ip'
        elif re.match('([\*a-z0-9|-]+\.)*[\*a-z0-9|-]+\.[a-z]+', target):
            self.verbose_print('[+]', target, 'identified as domain name.')
            return 'domain'
        #elif re.match('^(?!mailto:)(?:(?:http|https|ftp)://)(?:\\S+(?::\\S*)?@)?(?:(?:(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}(?:\\.(?:[0-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))|(?:(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)(?:\\.(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)*(?:\\.(?:[a-z\\u00a1-\\uffff]{2,})))|localhost)(?::\\d{2,5})?(?:(/|\\?|#)[^\\s]*)?$')
        #    self.verbose_print('[+]', target, 'identified as url.')
        #    return 'url'
        else:
            return None

    def parse_interval(self, interval):
        preset_intervals = {'hourly': 3600, 'daily': 86400, 'weekly': 604800}
        if interval == 'hourly':
            parsed_interval = 3600
        elif interval == 'daily':
            parsed_interval = 86400
        elif interval == 'weekly':
            parsed_interval = 604800
        elif 'hr' in interval:
            hours = int(interval[0:-2])
            parsed_interval = hours * 60 * 60
        elif 'min' in interval:
            minutes - int(interval[0:-3])
            parsed_interval = minutes * 60
        else:
            if not parsed_interval.is_digit():
                print('[-] Fatal error parsing given interval', interval)
                exit()
        return parsed_interval

                    
    def timestamp(self):
        d = datetime.utcnow()
        unixtime = calendar.timegm(d.utctimetuple()) 
        return unixtime  


    # Should return a list of tuples ready for putting into the database.
    def parse_output_file(self, target, category, company_dir, file, tool):
        with open('tools.json', 'r') as tools_file:
            tools = json.loads(tools_file.read())
            for tool_name, tool_options in tools.items():
                if tool_name == tool:
                    file_directory = company_dir + '/targets/domain/' +  '/' + target + '/' + category + '/'
                    with open(file) as outfile:
                        re.findall(tool_options['parse_result'], outfile.read())
            # os.path.getmtime = Check the time the file was edited last.
                        
    def verbose_print(self, verbose, *arg):
        if verbose == True:
            to_print = [a + ' ' for a in arg]
            print(''.join(to_print))

    def uniq_file(self, path):
        if os.path.exists(path):
            uniq_list = []
            with open(path, 'r') as f: 
                lines = [line.rstrip('\n') for line in f]
                uniq_list = set(lines)
            with open(path, 'w') as w:
                for uniq in uniq_list:
                    w.write(uniq + '\n')
