from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

class LobbyistNsw:
    def __init__(self, name, abn, trading_name, on_watch_list, status, details_anchor):
        self.name = name
        self.abn = abn
        self.trading_name = trading_name
        self.on_watch_list = on_watch_list
        self.status = status
        self.details_anchor = details_anchor
        self._clients = []
        self._employees = []
    
    @property
    def clients(self):
        return self._clients

    @clients.setter
    def clients(self, value):
        self._clients = value

    @property
    def employees(self):
        return self._employees

    @employees.setter
    def employees(self, value):
        self._employees = value
    
    @property
    def owners(self):
        return self._owners

    @owners.setter
    def owners(self, value):
        self._owners = value

class LobbyistNsw_Client:
    def __init__(self, name, abn, active, foreign_principal, countries, date_added):
        self.name = name
        self.abn = abn
        self.active = active
        self.foreign_principal = foreign_principal
        self.countries = countries
        self.date_added = date_added

class LobbyistNsw_Employee:
    def __init__(self, name, position, active, date_added):
        self.name = name
        self.postion = position
        self.active = active
        self.date_added = date_added

class LobbyistNsw_Owner:
    def __init__(self, name, active, date_added):
        self.name = name
        self.active = active
        self.date_added = date_added

class LobbyistNswScrapper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options = chrome_options)
        self.driver.get("https://lobbyists.elections.nsw.gov.au/whoisontheregister")

    def scrape(self):
        lobbyists = self.get_lobbyists()
        [self.populate_details(l) for l in lobbyists]
        return lobbyists

    def get_lobbyists(self):
        lobbyists = []
        dataTableElement = self.driver.find_element(By.CLASS_NAME, 'dataTable')
        rows = dataTableElement.find_elements(By.CSS_SELECTOR, 'tbody tr[role="row"]')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, "*")
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
        lobbyist.clients = []
        lobbyist.details_anchor.click()
        sleep(3)
        modalBody = self.driver.find_element(By.CLASS_NAME, 'modal-body')
        self.populate_clients(lobbyist, modalBody)
        self.populate_employees(lobbyist, modalBody)
        self.populate_owners(lobbyist, modalBody)

        # for some reason invoking a click from selenium directly throws a ElementNotInteractableException
        # exception, the work around is to execute javascript to click on the element.
        self.driver.execute_script('$("#lobby-details-modal .modal-header button.close").click()')
        sleep(4)
        

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

    def close(self):
        self.driver.quit()