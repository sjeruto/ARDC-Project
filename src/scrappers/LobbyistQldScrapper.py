from cgitb import text
from pydoc import cli
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from model.models import *
import regex as re

class LobbyistQldScrapper:
    def __init__(self, persist_to_db = True, max_retry = 5, run_headless = True):
        self.persist_to_db = persist_to_db

        if self.persist_to_db:
            self.db_session = Session(engine)
            if database_exists(engine.url) == False:
                Base.metadata.create_all(engine)

        self.max_retry = max_retry
        chrome_options = Options()
        if run_headless:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options = chrome_options)
        self.driver.get("https://lobbyists.integrity.qld.gov.au/who-is-on-the-register.aspx")

    def scrape(self):
        lobbyists = self.get_lobbyists()
        [self.populate_details(l) for l in lobbyists]
        return lobbyists

    def get_lobbyists(self):
        row_identifier_pattern = re.compile("\'(rc\d*)\'")
        lobbyists = []
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'table.mGrid[id$="grdCompanies"] tbody tr')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            row_identifier = re.findall(row_identifier_pattern, row.get_attribute('onclick'))[0]
            lobbyist = LobbyistQld(
                name = columns[1].text,
                trading_name = columns[0].text,
                abn = columns[2].text.replace(' ', ''),
                last_updated = columns[3].text,
                row_identifier = row_identifier
            )
            lobbyists.append(lobbyist)
        return lobbyists

    def populate_details(self, lobbyist: LobbyistQld):
        self.driver.find_element(By.CSS_SELECTOR, f'tr[onclick*="{lobbyist.row_identifier}"]').click()
        tables = self.driver.find_elements(By.CSS_SELECTOR, 'table.mGrid')

        if self.persist_to_db:
            self.db_session.add(lobbyist)
            self.db_session.commit()

        self.populate_owners(lobbyist, tables[0])
        self.populate_employees(lobbyist, tables[1])
        self.populate_clients(lobbyist, tables[2:])

        if self.persist_to_db:
            self.db_session.add_all(lobbyist.clients)
            self.db_session.add_all(lobbyist.employees)
            self.db_session.add_all(lobbyist.owners)
            self.db_session.commit()

        self.driver.execute_script("window.history.go(-1)")

    def populate_clients(self, lobbyist: LobbyistQld, tables):
        lobbyist.clients = []

        current_clients_table = tables[0]
        current_rows = current_clients_table.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in current_rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            client = LobbyistQld_Client(
                name = columns[0].text,
                paid_services_provided = columns[1].text.lower() == 'yes',
                client_added = columns[2].text,
                made_previous = ''
            )
            if self.persist_to_db:
                client.lobbyist_qld_id = lobbyist.id
            lobbyist.clients.append(client)

        previous_clients_table = tables[1]
        previous_rows = previous_clients_table.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in previous_rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            client = LobbyistQld_Client(
                name = columns[0].text,
                paid_services_provided = False,
                made_previous = columns[1].text,
                client_added = columns[2].text
            )
            if self.persist_to_db:
                client.lobbyist_qld_id = lobbyist.id
            lobbyist.clients.append(client)

    def populate_employees(self, lobbyist: LobbyistQld, table):
        lobbyist.employees = []
        rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            employee = LobbyistQld_Employee(
                name = columns[0].text,
                position = self.escape_null(columns[1].text),
                former_senior_gov_rep = columns[2].text.lower() == 'true',
                cessation_date = self.escape_null(columns[3].text),
                associations = self.escape_null(columns[4].text)
            )
            if self.persist_to_db:
                employee.lobbyist_qld_id = lobbyist.id
            lobbyist.employees.append(employee)

        
    def populate_owners(self, lobbyist: LobbyistQld, table):
        lobbyist.owners = []
        owners = table.find_elements(By.CSS_SELECTOR, 'tbody tr td')
        for owner_element in owners:
            owner = LobbyistQld_Owner(
                name = owner_element.text
            )
            if self.persist_to_db:
                owner.lobbyist_qld_id = lobbyist.id
            lobbyist.owners.append(owner)
        
    def escape_null(self, value):
        if value is None:
            return ''
        return value

    def close(self):
        self.driver.quit()
