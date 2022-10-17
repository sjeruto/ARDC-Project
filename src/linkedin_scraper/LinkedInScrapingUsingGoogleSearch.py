import sqlite3
import json
import datetime
from time import sleep
from src.linkedin_scraper.GoogleSearch import GoogleSearchForLinkedInUrls
from src.services.LobbyistService import LobbyistDataService
from webdriver_manager.chrome import ChromeDriverManager
from src.linkedin_scraper.LinkedInScraper import LinkedInScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

now = datetime.datetime.now()
file_name = "results" + str(now) + ".json"


if __name__ == "__main__":
    # names_list = ["Adrian Michael Dolahenty", "Alex Cramb"]
    # companies_list = ["Kurrajong Strategic Counsel", "Crisis&Comms Co Pty Ltd"]
    cnx = sqlite3.connect('data.db')
    lobbyistDataService = LobbyistDataService(cnx)
    # unique_employees = lobbyistDataService.get_unique_employee_to_lobbyists()
    # unique_lobbyist_orgs_df = lobbyistDataService.get_unique_lobbyist_abns()
    # employees_org = unique_employees.merge(unique_lobbyist_orgs_df, left_on='lobbyist_abn_clean', right_on='abn_clean')
    # federal_employees = employees_org.query("federal==1")
    # federal_employees = federal_employees.sample(n=100)
    # print(federal_employees)
    # print(federal_employees.columns)
    # names_list = federal_employees["lobbyist_name_clean"].to_list()
    # companies_list = federal_employees["lobbyist_org_name"].to_list()

    unique_federal_employees = lobbyistDataService.get_unique_federal_lobbyist_employees()
    unique_lobbyist_orgs_df = lobbyistDataService.get_unique_lobbyist_abns()
    federal_employees_org = unique_federal_employees.merge(unique_lobbyist_orgs_df, left_on='lobbyist_abn_clean', right_on='abn_clean')
    federal_employees_with_govt_exp = federal_employees_org.query("former_govt_representative=='Yes'")
    print(federal_employees_with_govt_exp)
    print(federal_employees_with_govt_exp.columns)
    federal_employees_with_govt_exp = federal_employees_with_govt_exp.head(3)
    print(federal_employees_with_govt_exp)
    names_list = federal_employees_with_govt_exp["lobbyist_name_clean"].to_list()
    companies_list = federal_employees_with_govt_exp["lobbyist_org_name"].to_list()
    
    with open(file_name, "w") as json_file:
        json.dump([], json_file)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for i in range(len(names_list)):
        scraper = LinkedInScraper(name_search=names_list[i], company_search=companies_list[i], driver=driver)
        if i == 0:
            scraper.linkedInLogin()
        googleSearch = GoogleSearchForLinkedInUrls(name_search=names_list[i], company_search=companies_list[i], driver=driver)
        googleSearch.googleQuery()
        profile = googleSearch.getlinkedInProfileUrls()
        scraper.scrapeProfileInfo(i=i, file_name=file_name, profile=profile)
        sleep(2)
        sleep(2)
    driver.quit()