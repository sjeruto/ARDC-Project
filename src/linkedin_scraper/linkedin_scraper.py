from src.linkedin_scraper.variables import my_password, my_username
import json
import os
import datetime
import sqlite3
from fuzzywuzzy import fuzz
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.services.LobbyistService import LobbyistDataService

now = datetime.datetime.now()
file_name = "results" + str(now) + ".json"

class LinkedInScraper:
    def __init__(self, name_search, company_search, driver):
        # Chrome driver install
        self.driver = driver
        self.driver.get('https://www.linkedin.com/')
        self.wait = WebDriverWait(self.driver, 10)
        sleep(2)
        self.name_search = name_search
        self.company_search = company_search
        # self.file_name = "/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/linkedin_scraper/" + name_search + ".json"
        print(os.getcwd())
        # self.name_search = "Alex Cramb"
        # self.company_search = "Crisis&Comms Co Pty Ltd"
        # self.name_search = "Aisling Acton"
        # self.company_search = "Michelson Alexander Pty Ltd"

    def linkedInLogin(self):  
        # getting the variables name and login
        username = self.driver.find_element(By.CLASS_NAME, 'input__input')
        username.send_keys(my_username) # username field

        password = self.driver.find_element(By.NAME, 'session_password')
        password.send_keys(my_password) # password field
        sleep(3)
        log_in_button = self.driver.find_element(By.CLASS_NAME,'sign-in-form__submit-button') # submit button
        log_in_button.click() # click the submit button
        sleep(60)

    def googleQuery(self):
        # Making the google query
        sleep(60)
        self.driver.get('https://www.google.com/')
        search_bar = self.driver.find_element(By.NAME, 'q')
        self.query = 'site:linkedin.com/in/ AND ("'+ self.name_search + '" OR "' + self.company_search + '")'
        print("Google query: " + self.query)
        sleep(10)
        search_bar.send_keys(self.query)
        search_bar.send_keys(Keys.ENTER) # Automating the enter key

    def getlinkedInProfileUrls(self):
        # Saving the linkedin users urls in an array to do the scraping
        sleep(5)
        linkedin_users_urls_list = self.driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]')
        self.profile_urls = []

        # To check the list content we run the following command
        [self.profile_urls.append(users.get_attribute("href")) for users in linkedin_users_urls_list]
        self.first_profile_per_page = []
        if self.profile_urls:
            self.first_profile_per_page.append(self.profile_urls[0])
            print(self.first_profile_per_page)

    # def extractElementText(self, locator):
    #     try:
    #         self.wait.until(EC.visibility_of_element_located((By.XPATH, locator)))
    #         element = self.driver.find_element(By.XPATH, locator)
    #         actions = ActionChains(self.driver)
    #         actions.move_to_element(element).perform()
    #     except:
    #         print("Exception thrown for locator: " + locator)
    #     finally:
    #         text = self.sel.xpath(locator + "/text()").extract_first()
    #         if text is None:
    #             self.driver.refresh()
    #             sleep(2)
    #             test_second_try = self.sel.xpath(locator + "/text()").extract_first()
    #             if test_second_try is None:
    #                 text = 'No Result'
    #             else:
    #                 text = text.strip()
    #         else:
    #             text = text.strip()
    #         return text

    def extractElementText(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, locator)))
            element = self.driver.find_element(By.XPATH, locator)
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            text = self.driver.find_element(By.XPATH, locator).text
        except:
            print("Exception thrown for locator: " + locator)
            text = 'No Result'
        finally:
            return text

    def extractElementsByLocator(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, locator)))
            elements = self.driver.find_elements(By.XPATH, locator)
        except:
            print("Exception thrown for locator: " + locator)
            elements = None
        finally:
            return elements

    def extractFirstElementByLocator(self, locator):
        # try:
        #     self.wait.until(EC.visibility_of_element_located((By.XPATH, locator)))
        #     element = self.driver.find_element(By.XPATH, locator)
        #     actions = ActionChains(self.driver)
        #     actions.move_to_element(element).perform()
        # except:
        #     print("Exception thrown for locator: " + locator)
        # finally:
        # element =  self.sel.xpath(locator).extract_first()
        try:
            element = self.driver.find_element(By.XPATH, locator)
        except:
            element = None
        finally:
            return element

    def splitCompanyNameFromJobType(self, text):
        if " · Part" in text:
            text_split = text.split(" · Part")
            company_name = text_split[0]
        elif " · Full" in text:
            text_split = text.split(" · Full")
            company_name = text_split[0]
        else:
            company_name = text
        return company_name

    def getMatchingScoreForTwoTexts(self, text1, text2):
        ratio = fuzz.ratio(text1.lower(), text2.lower())
        return ratio

    def checkCompanyNameAgainstCompanySearch(self, company_name):
        if not self.correct_company and self.getMatchingScoreForTwoTexts(company_name, self.company_search) >= 70:
            self.correct_company = True

    def checkCompanyNameAndRoleAgainstGovtPositions(self, company_name, role):
        gov_keywords = ['Parliament', 'Minister', 'NSW Government', 'Liberal Party', 'Labor Party', 'MP', 
        'Federal Cabiner Minister', 'Federal Government', 'Department of Defence', 'Australian Government', 
        'ACT Legislative Assembly', 'Office of the Treasurer', 'Office of Federal Health Minister', 
        'NSW Opposition Leader', 'House of Representatives', 'Deputy Prime Minister', 'Ministerial offices', 
        'Leader of the Opposition']
        for gov_keys in gov_keywords:
            if gov_keys in company_name or gov_keys in role:
                self.work_for_gov = True
                gov_exp_dict = {
                    "CompanyName": company_name,
                    "Role": role
                }
                if gov_exp_dict != self.prev_gov_exp_dict:
                    self.gov_experience.append(gov_exp_dict)
                self.prev_gov_exp_dict = gov_exp_dict



    def getExperiencesDictionary_ForMultipleRolesInCompany_InMainPage(self, i):
        sleep(2)
        company_name = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/a/div/span/span[1]")                        
        company_name = self.splitCompanyNameFromJobType(company_name)
        self.checkCompanyNameAgainstCompanySearch(company_name=company_name)
        duration = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/a/span/span[1]")        
        role_cards = self.extractElementsByLocator(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[2]/ul/li")
        
        list_roles = []
        for j in range(len(role_cards)):
            role_mult = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[2]/ul/li[" + str(j+1) + "]/div/div[2]/div/a/div/span/span[1]")            
            duration_role = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[2]/ul/li[" + str(j+1) + "]/div/div[2]/div/a/span[1]/span[1]")            
            location_role = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[2]/ul/li[" + str(j+1) + "]/div/div[2]/div/a/span[2]/span[1]")            
            self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role_mult)
            roles_dict = {
                "Role": role_mult,
                "Duration": duration_role,
                "Location": location_role
            }
            list_roles.append(roles_dict)


        exp_dict = {
            "CompanyName": company_name,
            "Role": list_roles,
            "Duration": duration
        }
        return exp_dict

    def getExperiencesDictionary_ForSingleRoleInCompany_InMainPage(self, i):
        sleep(2)
        company_name = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div/div[1]/span[1]/span[1]")                        
        company_name = self.splitCompanyNameFromJobType(company_name)
        self.checkCompanyNameAgainstCompanySearch(company_name=company_name)
        duration = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div/div[1]/span[2]/span[1]")        
        location = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div/div[1]/span[3]/span[1]")        
        role = self.extractElementText(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/div[1]/div/span/span[1]")
        self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role)
        exp_dict = {
            "CompanyName": company_name,
            "Role": role,
            "Duration": duration,
            "Location": location
        }
        return exp_dict

    def scrapeExperienceSectionInMainPage(self):
        sleep(4)
        experience_cards = self.extractElementsByLocator(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li")
        list_experiences = []
        if experience_cards is not None:
            print("Profile: " + self.name + " || Number of experience cards: " + str(len(experience_cards)))
            for i in range(len(experience_cards)):
                check_multiple_roles = self.extractFirstElementByLocator(locator="//*[text()='Experience']/../../../../../../descendant::div[6]/ul/li[" + str(i+1) + "]/div/div[2]/div[2]/ul/li[1]/div/div[2]/div/a")
                if check_multiple_roles:
                    list_experiences.append(self.getExperiencesDictionary_ForMultipleRolesInCompany_InMainPage(i=i))                        
                else:                        
                    list_experiences.append(self.getExperiencesDictionary_ForSingleRoleInCompany_InMainPage(i=i))
        return list_experiences

    def getExperiencesDictionary_ForMultipleRoles_InAllExperiencesPage(self, i):
        sleep(2)
        company_name = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/a/div/span/span[1]")
        company_name = self.splitCompanyNameFromJobType(company_name)
        self.checkCompanyNameAgainstCompanySearch(company_name=company_name)
        duration = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/a/span/span[1]")
        role_cards = self.extractElementsByLocator(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]//div/div[2]/div[2]/ul/li/div/div/div[1]/ul/li")
        list_roles = []
        for j in range(len(role_cards)):
            role_mult = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]//div/div[2]/div[2]/ul/li/div/div/div[1]/ul/li[" + str(j+1) + "]/div/div[2]/div[1]/a/div/span/span[1]")
            duration_role = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]//div/div[2]/div[2]/ul/li/div/div/div[1]/ul/li[" + str(j+1) + "]/div/div[2]/div[1]/a/span[1]/span[1]")
            location_role = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]//div/div[2]/div[2]/ul/li/div/div/div[1]/ul/li[" + str(j+1) + "]/div/div[2]/div[1]/a/span[2]/span[1]")
            self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role_mult)
            roles_dict = {
                "Role": role_mult,
                "Duration": duration_role,
                "Location": location_role
            }
            list_roles.append(roles_dict)

        exp_dict = {
            "CompanyName": company_name,
            "Role": list_roles,
            "Duration": duration
        }
        return exp_dict

    def getExperiencesDictionary_ForSingleRole_InAllExperiencesPage(self, i):
        sleep(2)
        company_name = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/div[1]/span[1]/span[1]")
        company_name = self.splitCompanyNameFromJobType(company_name)
        self.checkCompanyNameAgainstCompanySearch(company_name=company_name)
        role = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/div[1]/div/span/span[1]")
        duration = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/div[1]/span[2]/span[1]")
        location = self.extractElementText(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/div[1]/span[3]/span[1]")
        self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role)
        exp_dict = {
            "CompanyName": company_name,
            "Role": role,
            "Duration": duration,
            "Location": location
        }
        return exp_dict

    def scrapeAllExperiencesPage(self):
        sleep(4)
        experience_cards_locator = "//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li"
        experience_cards = self.extractElementsByLocator(locator=experience_cards_locator)
        if len(experience_cards) >= 20:
            element = self.driver.find_element(By.XPATH, experience_cards_locator + "[19]")
            print("here")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            sleep(3)
            experience_cards = self.extractElementsByLocator(locator=experience_cards_locator)
        print("Profile: " + self.name + " || Number of experience cards: " + str(len(experience_cards)))    
        list_experiences = []     
        for i in range(len(experience_cards)):
            check_multiple_roles = self.extractFirstElementByLocator(locator="//*[text()='Experience']/../../../div[contains(@class,'pvs-list__container')]/div/div/ul/li[" + str(i+1) + "]/div/div[2]/div[1]/a")
            if check_multiple_roles:
                list_experiences.append(self.getExperiencesDictionary_ForMultipleRoles_InAllExperiencesPage(i=i))
            else:
                list_experiences.append(self.getExperiencesDictionary_ForSingleRole_InAllExperiencesPage(i=i))
        return list_experiences

    def scrapeMainProfileSection(self):
        main_profile_dic = {}
        main_profile_dic["name"] = self.extractElementText(locator='//*[starts-with(@class, "text-heading-xlarge")]')
        main_profile_dic["profile_title"] = self.extractElementText(locator='//*[starts-with(@class, "text-body-medium")]')
        main_profile_dic["sub_title"] = self.extractElementText(locator='//*[starts-with(@class, "text-body-small")]')        
        sleep(3)                
        main_profile_dic["current_company"] = self.extractElementText(locator='//*[starts-with(@class, "pv-text-details__right-panel-item-text")]/../../../../../..//div[2]/div[2]/ul/li[1]/button/span/div')
        main_profile_dic["university"]= self.extractElementText(locator='//*[starts-with(@class, "pv-text-details__right-panel-item-text")]/../../../../../..//div[2]/div[2]/ul/li[2]/button/span/div')                                
        main_profile_dic["linkedin_url"]= self.driver.current_url
        sleep(3)
        if self.getMatchingScoreForTwoTexts(main_profile_dic["name"], self.name_search) >= 70:
                    self.correct_name = True
        return main_profile_dic
    
    def scrapeProfileInfo(self, i):
        with open(file_name, "r+") as json_file:
            if not self.profile_urls:
                profiles_dict = {
                    "NameSearched": self.name_search,
                    "CompanySearched": self.company_search,
                    "SuccessfulGoogleQuery": False,
                    "ProfilesScraped": []
                }
            else:
                list_dicts = []
                for profiles in self.first_profile_per_page:
                    self.correct_name = False
                    self.correct_company = False
                    self.work_for_gov = False
                    self.gov_experience = []
                    self.prev_gov_exp_dict = {}
                    self.driver.get(profiles)
                    sleep(3)
                    main_profile_info = self.scrapeMainProfileSection()
                    self.name = main_profile_info["name"]
                    if self.getMatchingScoreForTwoTexts(main_profile_info["current_company"], self.company_search) >= 70:
                        self.correct_company = True
                    try:
                        show_all_experiences = self.driver.find_element(By.XPATH, "//*[text()='Experience']/../../../../../../div[3]/div/div/a")
                        show_all_experiences_found = True
                    except:
                        show_all_experiences_found = False
                    list_experiences = []
                    if show_all_experiences_found:
                        sleep(2)
                        show_all_experiences.click()
                        list_experiences = self.scrapeAllExperiencesPage()
                    else:
                        list_experiences = self.scrapeExperienceSectionInMainPage()
                    output_dict = {
                        "Name": main_profile_info["name"],
                        "ProfileTitle": main_profile_info["profile_title"],
                        "ProfileSubTitle": main_profile_info["sub_title"],
                        "CurrentCompany": main_profile_info["current_company"],
                        "University": main_profile_info["university"],
                        "LinkedInUrl": main_profile_info["linkedin_url"],
                        "WorkExperience": list_experiences,
                        "CorrectName": self.correct_name,
                        "CorrectCompany": self.correct_company,
                        "WorkedForGovernment": self.work_for_gov,
                        "GovernmentPositions": self.gov_experience
                    }
                    list_dicts.append(output_dict)
                profiles_dict = {
                    "NameSearched": self.name_search,
                    "CompanySearched": self.company_search,
                    "SuccessfulGoogleQuery": True,
                    "ProfilesScraped": list_dicts
                }
            json_file.seek(os.stat(file_name).st_size -1)
            if i == 0:
                json_file.write( "{}]".format(json.dumps(profiles_dict)))
            else:
                json_file.write( ",{}]".format(json.dumps(profiles_dict)))


if __name__ == "__main__":
    # names_list = ["Adrian Michael Dolahenty", "Alex Cramb"]
    # companies_list = ["Kurrajong Strategic Counsel", "Crisis&Comms Co Pty Ltd"]
    cnx = sqlite3.connect('../data.db')
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
    names_list = federal_employees_with_govt_exp["lobbyist_name_clean"].to_list()
    companies_list = federal_employees_with_govt_exp["lobbyist_org_name"].to_list()
    
    with open(file_name, "w") as json_file:
        json.dump([], json_file)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for i in range(len(names_list)):
        scraper = LinkedInScraper(name_search=names_list[i], company_search=companies_list[i], driver=driver)
        if i == 0:
            scraper.linkedInLogin()
        scraper.googleQuery()
        scraper.getlinkedInProfileUrls()
        scraper.scrapeProfileInfo(i=i)
        sleep(2)
        sleep(2)
    driver.quit()
