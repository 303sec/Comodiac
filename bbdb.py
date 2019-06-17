#!/bin/python3

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time
import random
import sqlite3


class bbdb:

    """
    @init: create company db

    Creates Database: {company}.db
    in the directory: ~/bb/{company}

    Creates table: scan_info: containing info on running scans

    scan_info Table:

    id:                   PRIMARY KEY
    company:              TEXT NOT NULL
    target:               TEXT NOT NULL
    scan_id:              TEXT NOT NULL
    scan_tool:            TEXT NOT NULL
    scan_category:        TEXT NOT NULL
    scan_command:         TEXT NOT NULL
    scan_started:         DATE NOT NULL
    scan_outfile          TEXT
    scan_completed:       DATE
    scan_pid:             TEXT NOT NULL
    scan_status:          TEXT NOT NULL

        Uses Database: {company}.db

    assets Table:

    id:                   PRIMARY KEY
    target:               TEXT NOT NULL
    company:              TEXT NOT NULL
    asset_type:           TEXT NOT NULL
    asset_content:        TEXT NOT NULL
    scan_datetime:        DATE NOT NULL
    scan_id               INTEGER NOT NULL
    ignore                INT NOT NULL


    Creates table: schedule_info: containing info on information on scheduled scans
    schedule_info table:

    id                  INTEGER PRIMARY KEY,
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
    next_run            DATE,
    infile              TEXT NOT NULL,
    intype              TEXT NOT NULL,
    # can be set to either file or asset
    # file = filename = input. asset = every line of file = input.
    outfile             TEXT NOT NULL,
    parser              TEXT NOT NULL,
    meta                TEXT




    """
    def __init__(self, base_dir, company):
        # Create base db (bb.db) scan_info and asset tables
        # Check to see if the database exists. If not, create it.
        self.company = company
        self.db_name = base_dir + '/bb.db'
        print('[+] Creating database at', self.db_name)
        connection = sqlite3.connect(self.db_name)

        cursor= connection.cursor();
        # Create the scan_info table for the company
        try:
            cursor.execute('''CREATE TABLE scan_info (
                id INTEGER PRIMARY KEY,
                company TEXT NOT NULL,
                target TEXT NOT NULL,
                scan_id TEXT NOT NULL,
                scan_tool TEXT NOT NULL,
                scan_category TEXT NOT NULL,
                scan_command TEXT NOT NULL,
                scan_outfile TEXT,
                scan_started DATE,
                scan_completed DATE,
                scan_pid TEXT,
                scan_status TEXT NOT NULL
                )''')
        except Exception as e:
            print(e)
        # Create the asset table
        try:
            cursor.execute('''CREATE TABLE assets (
                id INTEGER PRIMARY KEY,
                target TEXT NOT NULL,
                company TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                asset_content TEXT NOT NULL,
                asset_category TEXT NOT NULL,
                scan_datetime DATE NOT NULL,
                scan_id INTEGER NOT NULL,
                ignore INTEGER NOT NULL
                )''')
        except Exception as e:
            print(e)

        try:
            cursor.execute('''CREATE TABLE schedule_info (
                id INTEGER PRIMARY KEY,
                target TEXT NOT NULL,
                company TEXT NOT NULL,
                schedule TEXT NOT NULL,
                infile TEXT NOT NULL,
                intype TEXT NOT NULL,
                outfile TEXT NOT NULL
                parser TEXT NOT NULL,
                tools TEXT,
                categories TEXT,
                wordlist TEXT,
                last_run DATE,
                last_scan_id INTEGER,
                meta TEXT
                )''')
        except Exception as e:
            print(e)



    # @param: scan_data: dict: containing:
    #   scan['id'] = target, scan name & timestamp concatenated
    #   scan['tool']
    #   scan['command']
    #   scan['category']
    #   scan['status'] == waiting
    def add_scan(self, target, scan_data:dict):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('INSERT INTO scan_info (target, company, scan_id, scan_tool, scan_category, scan_command, scan_status) VALUES (?, ?, ?, ?, ?, ?, ?)',\
                (target, self.company, scan_data['scan_id'], scan_data['tool'], scan_data['command'], scan_data['category'], scan_data['status']))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print('[-] Database error in add_scan:')
            print(e)
            return -1
        return 0

    # @param: target: string: name of the target to update information
    # @param: scan_data: dict: containing:
    #   scan['pid']
    #   scan['started']
    #   scan['status'] == started
    #   scan['id']
    def start_scan(self, target, scan_data:dict):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('UPDATE scan_info SET scan_pid=?, scan_started=?, scan_status=?, scan_outfile=? WHERE scan_id=? AND target=? AND company=?',\
                (scan_data['pid'], scan_data['started'], scan_data['status'], scan_data['output'], scan_data['scan_id'], target, self.company))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print('[-] Database error in start_scan:')
            print(e)
            return -1
        return 0


    def scan_complete(self, target, scan_data:dict):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('UPDATE scan_info SET scan_completed=?, scan_status=? WHERE scan_id=? AND target=? AND company=?',\
                (scan_data['completed'], scan_data['status'], scan_data['scan_id'], target, self.company))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print('[-] Database error in start_scan:')
            print(e)
            return -1
        return 0


    # Note: the asset_list needs to be a 
    # Another note: the asset_list tuples need to have the target and company name in them!
    # @ param: asset_list: list of tuples with scan info
    def add_assets(self, target, asset_list):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.executemany('INSERT INTO assets (target, company, asset_type, asset_content, asset_category, scan_datetime) VALUES (?, ?, ?, ?, ?, ?)',\
                (asset_list))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print('[-] Database error in add_assets:')
            print(e)
            return -1
        return 0

    # @param: asset: dict: a dict of asset information to add to the db (needs to contain target & company)
    def add_asset(self, target, asset:dict):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('INSERT INTO assets (target, company, asset_type, asset_content, asset_category, scan_datetime) VALUES (?, ?, ?, ?, ?, ?)',\
                (asset))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print('[-] Database error in add_asset:')
            print(e)
            return -1
        return 0


    def get_assets_by_category(self, target, asset_category):
        connection = sqlite3.connect(self.db_name)
        connection.row_factory = sqlite3.Row
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM assets WHERE asset_category=? AND target=? AND company=?', (asset_category, target, self.company))
            result = cursor.fetchall()
            return [dict(row) for row in c.fetchall()]

        except Exception as e:
            print(e)
            return -1

    def get_assets_by_type(self, target, asset_type):
        connection = sqlite3.connect(self.db_name)
        connection.row_factory = sqlite3.Row
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM assets WHERE asset_type=? AND target=? AND company=?', (asset_type, target, self.company))
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(e)
            return -1        

    def get_assets_by_content(self, target, asset_content):
        connection = sqlite3.connect(self.db_name)
        connection.row_factory = sqlite3.Row
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM assets WHERE asset_content=? AND target=? AND company=?', (asset_content, target, self.company))
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(e)
            return -1


    def get_assets_between_dates(self, target, start_date, end_date=None):
        if end_date==None:
            end_date = datetime.datetime.now()
        connection = sqlite3.connect(self.db_name)
        connection.row_factory = sqlite3.Row
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM assets WHERE target= ? AND company= ? AND scan_date BETWEEN ? AND ?', \
                (start_time, end_time, target, self.company))
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(e)
            return -1

        '''
        SELECT *
        FROM employees
        WHERE scan_date BETWEEN '2014-01-01' AND '2014-12-31';
        '''


    # @param: string: table name to remove any non 0-9 a-z, . or - characters from
    # @return: a 'scrubbed' table name with everything bad removed. Hopefully.
    # Not sure we need this anymore.
    def scrub(self, table_name):
        return ''.join( chr for chr in table_name if re.match('[0-9a-zA-Z\.\-]', chr) )




'''
    Creates table: schedule_info: containing info on information on scheduled scans
    schedule_info table:

    id                  INTEGER PRIMARY KEY,
    active              INT NOT NULL,
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
    infile              TEXT NOT NULL,
    intype              TEXT NOT NULL,
    # can be set to either file or asset
    # file = filename = input. asset = every line of file = input.
    outfile             TEXT NOT NULL,
    parser              TEXT NOT NULL,
    meta                TEXT

'''


    # @param: asset: dict: a dict of asset information to add to the db (needs to contain target & company)
    def add_schedule(self, schedule:dict):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('INSERT INTO schedule_info (active, target, company, schedule, \
                tools, categories, wordlist, infile, intype, \
                outfile, parser, meta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',\
                (schedule['active'], schedule['target'], schedule['company'], schedule['schedule'], \
                    schedule['tools'], schedule['categories'], schedule['wordlist'], schedule['infile'], \
                    schedule['intype'], schedule['outfile'], schedule['parser'], schedule['meta'], ))
            # There will definintely be errors... not everything has all these values.
            # Could set them to blank on the way in?
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print('[-] Database error in add_schedule:')
            print(e)
            return -1
        return 0

    def modify_schedule(self, target, schedule:dict, company=self.company):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('UPDATE schedule_info SET scan_completed=?, scan_status=? WHERE scan_id=? AND target=? AND company=?',\
                (scan_data['completed'], scan_data['status'], scan_data['scan_id'], target, self.company))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print('[-] Database error in modify_schedule:')
            print(e)
            return -1
        return 0

