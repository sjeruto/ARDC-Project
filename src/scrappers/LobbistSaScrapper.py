from cgitb import text
import json
from pydoc import cli
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
from model.models import *
import regex as re
import os.path
import uuid
import pandas as pd
import sqlite3

class LobbyistSaScrapper:
    def __init__(self, persist_to_db = True, max_retry = 5, run_headless = True):
        self.persist_to_db = persist_to_db
        self.batch_id = uuid.uuid1()
        if self.persist_to_db:
            self.db_session = Session(engine)
            Base.metadata.create_all(engine)

        self.max_retry = max_retry
        chrome_options = Options()
        prefs = {"download.default_directory" : '/home/mick/git/iLab2'};
        chrome_options.add_experimental_option("prefs",prefs);

        if run_headless:
            chrome_options.add_argument("--headless")

        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        self.driver = webdriver.Chrome(options = chrome_options, desired_capabilities = capabilities)
        self.driver.get("https://www.lobbyists.sa.gov.au/")

    def scrape(self):
        self.download_data_file()
        if self.persist_to_db:
            self.process_data_file()

    def download_data_file(self):
        sleep(3)
        export_button = self.driver.find_element(By.CSS_SELECTOR, '.pi-external-link')
        export_button.click()
        print('waiting for download...')
        while os.path.isfile('Lobbyist Export.xls') == False:
            sleep(5)
        
        # We could potentially detected the file downlaod by analysing the performance logs
        # however we are not going to spend time on this now
        # print('checking performance logs')
        # self.driver.get('https://saglobbyistapi02prdaue.azurewebsites.net/api/lobbyist/export')
        # for entry in self.driver.get_log('performance'):
        #     print(entry)

    def process_data_file(self):
        cnx = sqlite3.connect('data.db')
        lobbyists_df = pd.read_excel('Lobbyist Export.xls', 'Lobbyists')
        lobbyists_df.columns = lobbyists_df.columns.str.replace(' ', '_')
        lobbyists_df.columns = lobbyists_df.columns.str.replace('(', '')
        lobbyists_df.columns = lobbyists_df.columns.str.replace(')', '')
        lobbyists_df.columns = lobbyists_df.columns.str.lower()
        lobbyists_df.abn = pd.to_numeric(lobbyists_df.abn.str.replace(' ', ''))
        lobbyists_df["batch_id"] = self.batch_id.__str__()
        lobbyists_df.to_sql('lobbyist_sa', cnx, index=False, if_exists='append')

        employees_df = pd.read_excel('Lobbyist Export.xls', 'Employees')
        employees_df.columns = employees_df.columns.str.replace(' ', '_')
        employees_df.columns = employees_df.columns.str.lower()
        employees_df["lobbyist_abn"] = pd.to_numeric(employees_df.lobbyist_abn.str.replace(' ', ''))
        employees_df = employees_df[[c for c in employees_df.columns if c not in ['lobbyist_business_name', 'lobbyist_trading_name']]]
        employees_df["batch_id"] = self.batch_id.__str__()
        employees_df.to_sql('lobbyist_sa_employee', cnx, index=False, if_exists='append')

        clients_df = pd.read_excel('Lobbyist Export.xls', 'Clients')
        clients_df.columns = clients_df.columns.str.replace(' ', '_')
        clients_df.columns = clients_df.columns.str.lower()
        clients_df["lobbyist_abn"] = pd.to_numeric(clients_df.lobbyist_abn.str.replace(' ', ''))
        clients_df = clients_df[[c for c in clients_df.columns if c not in ['lobbyist_business_name', 'lobbyist_trading_name']]]
        clients_df["batch_id"] = self.batch_id.__str__()
        clients_df.to_sql('lobbyist_sa_client', cnx, index=False, if_exists='append')

        os.rename('Lobbyist Export.xls', f'processed/sa_lobbyist_export_batch_{self.batch_id.__str__()}.xls')
