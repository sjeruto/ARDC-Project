from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from model.models import *

class LobbyistNswScrapper:
    def __init__(self, persist_to_db = True, max_retry = 5, run_headless = True):
        self.persist_to_db = persist_to_db

        if self.persist_to_db:
            self.db_session = Session(engine)
            Base.metadata.create_all(engine)

        self.max_retry = max_retry
        chrome_options = Options()
        if run_headless:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options = chrome_options)
        self.driver.get("https://lobbyists.elections.nsw.gov.au/whoisontheregister")

    def scrape(self):
        section_ids = ["AC", "INA", "CA"]
        for section_id in section_ids:
            lobbyists = self.get_lobbyists(section_id)
            [self.populate_details(l) for l in lobbyists]

        return lobbyists

    def get_lobbyists(self, section_id):
        lobbyists = []
        self.driver.find_element(By.CSS_SELECTOR, f'a[href="#{section_id}"').click()
        sleep(2)
        dataTableElement = self.driver.find_element(By.CSS_SELECTOR, f'#{section_id} .dataTable')
        rows = dataTableElement.find_elements(By.CSS_SELECTOR, 'tbody tr[role="row"]')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, "td")
            anchor = columns[0].find_element(By.TAG_NAME, 'a')
            lobbyist = LobbyistNsw(
                name = columns[0].text,
                abn = columns[1].text,
                trading_name = columns[2].text,
                on_watch_list = columns[3].text,
                status = columns[4].text,
                details_anchor = anchor
            )
            lobbyists.append(lobbyist)

        return lobbyists

    def populate_details(self, lobbyist: LobbyistNsw):
        tries = 0
        while(tries < self.max_retry):
            try:
                lobbyist.details_anchor.click()
                break
            except:
                print("Exception caught on click event, reissuing close command...")
                self.driver.execute_script('$("#lobby-details-modal .modal-header button.close").click()')
                sleep(2)
                tries = tries + 1
                if tries == self.max_retry:
                    raise
                
        sleep(3)
        modalBody = self.driver.find_element(By.CLASS_NAME, 'modal-body')
        lobbyist.status_note = modalBody.find_element(By.CSS_SELECTOR, '#DET tbody tr:nth-child(5) td').text
        lobbyist.last_updated = modalBody.find_element(By.CSS_SELECTOR, '#DET tbody tr:nth-child(3) td').text

        if self.persist_to_db:
            self.db_session.add(lobbyist)
            self.db_session.commit()

        self.retry(self.populate_clients, lobbyist, modalBody)
        self.retry(self.populate_employees, lobbyist, modalBody)
        self.retry(self.populate_owners, lobbyist, modalBody)

        if self.persist_to_db:
            self.db_session.add_all(lobbyist.clients)
            self.db_session.add_all(lobbyist.employees)
            self.db_session.add_all(lobbyist.owners)
            self.db_session.commit()

        # for some reason invoking a click from selenium directly throws a ElementNotInteractableException
        # exception, the work around is to execute javascript to click on the element.
        self.driver.execute_script('$("#lobby-details-modal .modal-header button.close").click()')
        sleep(2)
        

    def populate_owners(self, lobbyist: LobbyistNsw, modalBody):
        lobbyist.owners = []
        rows = modalBody.find_elements(By.CSS_SELECTOR, '#OWN .dataTable tbody tr')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            activeImg = row.find_element(By.CLASS_NAME, 'checkImg')
            owner = LobbyistNsw_Owner(
                name = columns[0].get_attribute('innerHTML'),
                active = activeImg.get_attribute('alt') == 'Checked',
                date_added= columns[2].get_attribute('innerHTML')
            )
            lobbyist.owners.append(owner)

    def populate_employees(self, lobbyist: LobbyistNsw, modalBody):
        lobbyist.employees = []
        rows = modalBody.find_elements(By.CSS_SELECTOR, '#EMP .dataTable tbody tr')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            activeImg = row.find_element(By.CLASS_NAME, 'checkImg')
            employee = LobbyistNsw_Employee(
                name = columns[0].get_attribute('innerHTML'),
                position = columns[1].get_attribute('innerHTML'),
                active = activeImg.get_attribute('alt') == 'Checked',
                date_added= columns[3].get_attribute('innerHTML')
            )
            lobbyist.employees.append(employee)

    def populate_clients(self, lobbyist: LobbyistNsw, modalBody):
        lobbyist.clients = []
        rows = modalBody.find_elements(By.CSS_SELECTOR, '#CLI .dataTable tbody tr')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            activeImg = row.find_element(By.CLASS_NAME, 'checkImg')
            abnElement = columns[1].find_element(By.CSS_SELECTOR, 'span[id^="j_id"] a')
            foreignPrincipalElement = columns[3].find_elements(By.CSS_SELECTOR, 'span')[0]
            countriesElement = columns[4].find_elements(By.CSS_SELECTOR, 'span')[0]
            client = LobbyistNsw_Client(
                name = columns[0].get_attribute('innerHTML'),
                abn = abnElement.get_attribute('innerHTML'),
                active = activeImg.get_attribute('alt') == 'Checked',
                foreign_principal = foreignPrincipalElement.get_attribute('innerHTML').lower() != 'no',
                countries = countriesElement.get_attribute('innerHTML'),
                date_added = columns[5].get_attribute('innerHTML')
            )
            if client.countries == '&nbsp;':
                client.countries = ''
            lobbyist.clients.append(client)

            if self.persist_to_db:
                client.lobbyist_nsw_id = lobbyist.id
            

    def retry(self, func, lobbyist: LobbyistNsw, modalBody):
        tries = 0
        while(tries < self.max_retry):
            try:
                func(lobbyist, modalBody)
                break
            except:
                tries = tries + 1
                if tries == self.max_retry:
                    raise
                print("Exception caught, retrying...")
                sleep(5)
                

    def close(self):
        self.driver.quit()