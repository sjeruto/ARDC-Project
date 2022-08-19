from cgitb import text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from model.models import *

class LobbyistQldScrapper:
    def __init__(self, persist_to_db = True, max_retry = 5):
        self.persist_to_db = persist_to_db

        if self.persist_to_db:
            self.db_session = Session(engine)
            if database_exists(engine.url) == False:
                Base.metadata.create_all(engine)

        self.max_retry = max_retry
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options = chrome_options)
        self.driver.get("https://lobbyists.integrity.qld.gov.au/who-is-on-the-register.aspx")

    def get_lobbyists(self):
        lobbyists = []
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'table.mGrid[id$="grdCompanies"] tbody tr')
        for row in rows:
            columns = row.find_elements(By.CSS_SELECTOR, 'td')
            lobbyist = LobbyistQld(
                name = columns[0].text,
                trading_name = columns[1].text,
                abn = columns[2].text,
                last_updated = columns[3].text,
                details_anchor = row
            )
            lobbyists.append(lobbyist)
        return lobbyists

    def close(self):
        self.driver.quit()
