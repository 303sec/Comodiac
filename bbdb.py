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

    Creates table: scan_info: containing meta info about running scans

    scan_info Table:

    ID:                   PRIMARY KEY
    scan_name:            TEXT NOT NULL
    scan_command:         TEXT NOT NULL
    scan_started:         DATE NOT NULL
    scan_completed:       DATE
    scan_pid:             TEXT NOT NULL
    scan_status:          TEXT NOT NULL


    """
    def __init__(self, company, company_dir):
        # Create company db
        # Check to see if the database exists. If not, create it.
        self.db_name = company_dir + '/' + company + '.db'
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Create the scan_info table for the company
        try:
            cursor.execute('''CREATE TABLE scan_info (
                id INTEGER PRIMARY KEY,
                scan_name TEXT NOT NULL,
                scan_command TEXT NOT NULL,
                scan_started DATE NOT NULL,
                scan_completed DATE,
                scan_pid TEXT NOT NULL,
                scan_status TEXT NOT NULL
                 )''')

        except Exception as e:
            print(e)

    """
    @create_target_table: create tables for targets
    @param: target: string: the name of the target to create a table.
    @return: 0 for success

    Uses Database: {company}.db

    Scans Table:

    ID:                    PRIMARY KEY
    asset_type:            TEXT NOT NULL
    asset_content:         TEXT NOT NULL
    scan_datetime:         DATE NOT NULL
    scan_id                INTEGER NOT NULL
    ignore                 INT NOT NULL

    """
    def create_target_table(self, target):
        # Check to see if the database exists. If not, create it.
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Check to see if the table exists. If not, create it.
        try:
            cursor.execute('''CREATE TABLE ? (
                id INTEGER PRIMARY KEY,
                asset_type TEXT NOT NULL,
                asset_content TEXT NOT NULL,
                asset_category TEXT NOT NULL,
                scan_datetime DATE NOT NULL,
                scan_id INTEGER NOT NULL,
                ignore INTEGER NOT NULL
                 )''', (target, ))
            return 0

        except Exception as e:
            print(e)
            return -1



    # Note: the asset_list needs to be a list of tuples.
    def add_assets(self, target, asset_list):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.executemany('INSERT INTO ? (asset_type, asset_content, asset_category, scan_datetime) VALUES (?, ?, ?, ?)',\
                (asset_list))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print(e)
            return -1
        return 0

    def add_asset(self, target, asset:dict):
        connection = sqlite3.connect(self.db_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('INSERT INTO ? (asset_type, asset_content, asset_category, scan_datetime) VALUES (?, ?, ?, ?)',\
                (asset['type'], asset['content'], asset['category'], asset['date']))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print(e)
            return -1
        return 0


    # There is obviously a way to not just use 3 different functions, but I don't like making my sql queries too vague.
    def get_assets_by_category(self, target, asset_category):
        connection = sqlite3.connect(self.db_name)
        connection.row_factory = sqlite3.Row
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM ? WHERE asset_category=?', (target, asset_category))
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
            cursor.execute('SELECT * FROM ? WHERE asset_type=?', (target, asset_type))
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(e)
            return -1        

    def get_assets_by_content(self, target, asset_content):
        connection = sqlite3.connect(self.db_name)
        connection.row_factory = sqlite3.Row
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM ? WHERE asset_content=?', (target, asset_category))
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
            cursor.execute('SELECT * FROM ? WHERE scan_date BETWEEN ? AND ?', \
                (target, start_time, end_time))
            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(e)
            return -1

        '''
        SELECT *
        FROM employees
        WHERE scan_date BETWEEN '2014-01-01' AND '2014-12-31';
        '''


        """
        add_ava_scan_row: Creates a row according to data in input

        Adds: 

        scan_data['scan_name']
        scan_data['scan_id']
        scan_data['chaos_id']
        scan_data['target_count']
        scan_data['status']
        scan_data['start']
        scan_data['end']
        scan_data['scan_uuid']

        The dictionary passed in needs to have these parameters.
        There is definitely a better way of doing this:
        https://stackoverflow.com/questions/10913080/python-how-to-insert-a-dictionary-to-a-sqlite-database/10913280
        The problem is, although it's more elegant it doesn't really work for the data we're using, and will take a while to implement.

        """ 

    # @param: scan_data: dict: key value pairs of items to be added to the database
    # @return int: 0 for success, non-zero for error.
    def add_ava_scan_row(self, scan_data:dict):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor();
        # Should add given information into the database.
        try:
            cursor.execute('INSERT INTO Scans(scan_name, scan_id, scan_uuid, chaos_id, target_count, status, start, finish) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', \
                (scan_data['scan_name'],scan_data['scan_id'],scan_data['scan_uuid'],scan_data['chaos_id'],scan_data['target_count'], \
                    scan_data['scan_status'],scan_data['start'],scan_data['end']))
            connection.commit() 
            connection.close()
            return 0
        except Exception as e:
            print(e)
            return -1

    # @param: scan_id: string: The scan_id of the entry to edit
    # @param: scan_data: dict: A dict of the entire scan, to update the whole entry
    # Database Query: `UPDATE Scans SET status= ? WHERE scan_id= ?`
    # @return: int: 0 for success, non-zero for error
    # Note: This query is completely broken, but I don't think it'll need to be used
    def update_scan_by_id(self,scan_id,scan_data:dict):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('UPDATE Scans(scan_name, scan_id, chaos_id, target_count, status, start, finish) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', \
                (scan_data['scan_name'],scan_data['scan_id'],scan_data['chaos_id'],scan_data['target_count'], \
                    scan_data['scan_status'],scan_data['start'],scan_data['end']))
            connection.commit() 
            connection.close()
            return 0

        except Exception as e:
            print(e)
            return -1

    # @param: scan_id: string: The scan_id of the entry to edit
    # @param: status: string: The status to change the scan_id entry to
    # Database Query: `UPDATE Scans SET status= ? WHERE scan_id= ?`
    # @return: int: 0 for success, non-zero for error
    def update_status_by_id(self,scan_id,status):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('UPDATE Scans SET status= ? WHERE scan_id= ?', \
                (status, scan_id))
            connection.commit() 
            connection.close()
            return 0

        except Exception as e:
            print(e)
            return -1

    # @param: scan_id: string: The scan_id of the entry to edit
    # @param: nessus_file: string: The location of the new nessus file
    # Database Query: `UPDATE Scans SET nessus_file= ? WHERE scan_id= ?`
    # @return: int: 0 for success, non-zero for error
    def update_nessus_file(self,scan_id,nessus_file):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('UPDATE Scans SET nessus_file= ? WHERE scan_id= ?', \
                (nessus_file, scan_id))
            connection.commit() 
            connection.close()
            return 0

        except Exception as e:
            print(e)
            return -1


    # @param: scan_id: string: The scan_id of the entry to edit
    # @param: nessus_file: string: The current error alert
    # Database Query: `UPDATE Scans SET error_alert= ? WHERE scan_id= ?`
    # @return: int: 0 for success, non-zero for error
    def update_error_alert(self,scan_id,error_alert):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('UPDATE Scans SET error_alert= ? WHERE scan_id= ?', \
                (error_alert, scan_id))
            connection.commit() 
            connection.close()
            return 0

        except Exception as e:
            print(e)
            return -1

    # @param: scan_id: string: The scan_id of the entry to get
    # Database Query: `SELECT error_alert FROM Scans WHERE scan_id= ?`
    # @return list of tuples containing all scan information.
    def get_error_alert(self,scan_id):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('SELECT error_alert FROM Scans WHERE scan_id= ?', \
                (scan_id))
            return cursor.fetchall()

        except Exception as e:
            print(e)
            return -1

    # @param: scan_id: string: The scan_id of the entry to get
    # Database Query: `SELECT error_alert FROM Scans WHERE scan_id= ?`
    # @return list of tuples containing all scan information.
    def get_status(self,scan_id):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('SELECT error_alert FROM Scans WHERE scan_id= ?', \
                (scan_id))
            return cursor.fetchall()

        except Exception as e:
            print(e)
            return -1

    # @param: scan_id: string: The scan_id of the entry to edit
    # @param: cujo_enagagement_id: string: The cujo_enagagement_id to add
    # @param: cujo_test_id: string: The cujo_test_id to add
    # Database Query: `UPDATE Scans SET cujo_engagement_id=?, cujo_test_id=? WHERE scan_id= ?`
    # @return: int: 0 for success, non-zero for error
    def update_cujo_details(self,scan_id, cujo_engagement_id, cujo_test_id):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('UPDATE Scans SET cujo_engagement_id=?, cujo_test_id=? WHERE scan_id= ?', \
                (cujo_engagement_id, cujo_test_id, scan_id))
            connection.commit() 
            connection.close()
            return 0

        except Exception as e:
            print(e)
            return -1

    # @param: scan_id: string: The scan_id of the entry to move to the archive
    def move_entry_to_archive(self,scan_id):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('INSERT INTO Archive SELECT * FROM Scans WHERE scan_id = ?', (scan_id))
            connection.commit()
            cursor.execute('DELETE FROM Scans WHERE scan_id= ?', (scan_id))
            connection.commit()
            connection.close()

        except Exception as e:
            print(e)
            return -1

    # @param: scan_data: dict: key value pairs of scan info. We need scan_id and scan_uuid
    # @return: bool: True if the UUID changed, false if not.
    def did_uuid_change(self,scan_data:dict):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            id_and_uuid = cursor.execute('SELECT scan_id, scan_uuid FROM Scans WHERE scan_id=? AND scan_uuid=?', (scan_data['scan_id'], scan_data['scan_uuid'])).fetchall()
            print(id_and_uuid[0][1])
            print(scan_data['scan_uuid'])

            if id_and_uuid[0][1] != scan_data['scan_uuid']:
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return -1       



    # @return list of tuples containing all scan information.
    # Note: This function probably won't get used but it's useful to have.
    def select_all_scans(self):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor()
        try:
            cursor.execute('SELECT * FROM Scans')
            return cursor.fetchall()

        except Exception as e:
            print(e)
            return -1

    # @param: string: Scan name to look up
    # Database Query: ` SELECT * FROM Scans where scan_name=?`
    # @return: list: list of tuples with database items
    def select_scan_by_name(self, scan_name):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM Scans WHERE scan_name=?', (scan_name))

            return cursor.fetchall()

        except Exception as e:
            print(e)
            return -1

    def select_all_scan_names(self):
        connection = sqlite3.connect(self.db_name_name)
        # This allows sqlite to return a list of strings, instead of a list of tuples
        connection.row_factory = lambda cursor, row: row[0]
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT scan_name FROM Scans')
            return cursor.fetchall()

        except Exception as e:
            print(e)
            return -1
    
    # @param: string: Scan ID to look up
    # Database Query: ` SELECT * FROM Scans where scan_id=?`
    # @return: list: list of tuples with database items
    def select_scan_by_scan_id(self, scan_id):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM Scans WHERE scan_id=?', (chaos_id))
            return cursor.fetchall()

        except Exception as e:
            print(e)
            return -1


    # @param: string: Chaos ID to look up
    # Database Query: ` SELECT * FROM Scans where chaos_id=?`
    # @return: list: list of tuples with database items
    def select_scan_by_chaos_id(self, chaos_id):
        connection = sqlite3.connect(self.db_name_name)
        cursor= connection.cursor();
        try:
            cursor.execute('SELECT * FROM Scans WHERE chaos_id=?', (chaos_id))
            return cursor.fetchall()

        except Exception as e:
            print(e)
            return -1