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
    
    @property
    def clients(self):
        return self._clients

    @clients.setter
    def clients(self, value):
        self._clients = value

class LobbyistNsw_Client:
    def __init__(self, name, abn, active, foreign_principal, countries, date_added):
        self.name = name
        self.abn = abn
        self.active = active
        self.foreign_principal = foreign_principal
        self.countries = countries
        self.date_added = date_added



class LobbyistNswScrapper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options = chrome_options)
        self.driver.get("https://lobbyists.elections.nsw.gov.au/whoisontheregister")

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
        sleep(1)
        modalBody = self.driver.find_element(By.CLASS_NAME, 'modal-body')
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