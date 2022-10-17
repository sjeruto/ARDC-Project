from time import sleep
import pandas as pd
import datetime
import json
import sqlite3
from webdriver_manager.chrome import ChromeDriverManager
from src.linkedin_scraper.LinkedInScraper import LinkedInScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.services.LinkedInDataService import LinkedInDataService

now = datetime.datetime.now()
file_name = "results.json"

if __name__ == "__main__":
    cnx = sqlite3.connect('data.db')
    with open(file_name, "w") as json_file:
        json.dump([], json_file)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    df = pd.read_excel('ProfileUrls.xlsx')
    print(df)
    
    for i in range(len(df)):
        if pd.isna(df.loc[i, "Profile_Urls"]) or pd.isna(df.loc[i, "Employee_Name"]) or pd.isna(df.loc[i, "Lobbyist_Organisation"]):
            print("Row empty, index: " + str(i))
        else: 
            print(i)
            scraper = LinkedInScraper(name_search=df.loc[i, "Employee_Name"], company_search=df.loc[i, "Lobbyist_Organisation"], driver=driver)
            if i == 0:
                scraper.linkedInLogin()
            print(df.loc[i, "Profile_Urls"])
            scraper.scrapeProfileInfo(i=i, file_name=file_name, profile=df.loc[i, "Profile_Urls"])
            sleep(2)
            sleep(2)
            
    linkedInDataService = LinkedInDataService(cnx)
    lobbyist_employee_with_experience = linkedInDataService.get_all_lobbyist_employees_with_work_experience()
    lobbyist_employee_with_experience.to_csv("employees_experience.csv", index=False)
    driver.quit()