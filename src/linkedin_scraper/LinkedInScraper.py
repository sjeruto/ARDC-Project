from src.linkedin_scraper.Variables import my_username, my_password, gov_keywords
import json
import os
from fuzzywuzzy import fuzz
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from src.model.models import *

class LinkedInScraper:
    def __init__(self, name_search, company_search, driver, persist_to_db = True):
        # Chrome driver install
        self.driver = driver
        self.driver.get('https://www.linkedin.com/')
        self.wait = WebDriverWait(self.driver, 10)
        sleep(2)
        self.name_search = name_search
        self.company_search = company_search
        # self.file_name = "/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/linkedin_scraper/" + name_search + ".json"
        print(os.getcwd())
        self.presist_to_db = persist_to_db
        if self.presist_to_db:
            self.db_session = Session(engine)
            Base.metadata.create_all(engine)

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

    def checkCompanyNameAndRoleAgainstGovtPositions(self, company_name, role, duration):
        gov_exp = False
        for gov_keys in gov_keywords:
            if gov_keys in company_name or gov_keys in role:
                self.work_for_gov = True
                gov_exp_dict = {
                    "CompanyName": company_name,
                    "Role": role,
                    "Duration": duration
                }
                if gov_exp_dict != self.prev_gov_exp_dict:
                    self.gov_experience.append(gov_exp_dict)
                    self.prev_gov_exp_dict = gov_exp_dict
                    gov_exp = True
        return gov_exp

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
            gov_exp = self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role_mult, duration=duration_role)
            roles_dict = {
                "Role": role_mult,
                "Duration": duration_role,
                "Location": location_role
            }
            list_roles.append(roles_dict)
            linkedInUserProfileWorkExperience = LinkedInUserProfileWorkExperience(
                profile_id = self.linkedInProfileInfo.id,
                name = self.name,
                company_name = company_name,
                role = role_mult,
                duration = duration_role,
                location = location_role,
                government_experience = gov_exp
            )
            if self.presist_to_db:
                self.db_session.add(linkedInUserProfileWorkExperience)
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
        gov_exp = self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role, duration=duration)
        exp_dict = {
            "CompanyName": company_name,
            "Role": role,
            "Duration": duration,
            "Location": location
        }
        linkedInUserProfileWorkExperience = LinkedInUserProfileWorkExperience(
            profile_id = self.linkedInProfileInfo.id,
            name = self.name,
            company_name = company_name,
            role = role,
            duration = duration,
            location = location,
            government_experience = gov_exp
        )
        if self.presist_to_db:
            self.db_session.add(linkedInUserProfileWorkExperience)
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
            gov_exp = self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role_mult, duration=duration_role)
            roles_dict = {
                "Role": role_mult,
                "Duration": duration_role,
                "Location": location_role
            }
            list_roles.append(roles_dict)
            linkedInUserProfileWorkExperience = LinkedInUserProfileWorkExperience(
                profile_id = self.linkedInProfileInfo.id,
                name = self.name,
                company_name = company_name,
                role = role_mult,
                duration = duration_role,
                location = location_role,
                government_experience = gov_exp 
            )
            if self.presist_to_db:
                self.db_session.add(linkedInUserProfileWorkExperience)
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
        gov_exp = self.checkCompanyNameAndRoleAgainstGovtPositions(company_name=company_name, role=role, duration=duration)
        exp_dict = {
            "CompanyName": company_name,
            "Role": role,
            "Duration": duration,
            "Location": location
        }
        linkedInUserProfileWorkExperience = LinkedInUserProfileWorkExperience(
            profile_id = self.linkedInProfileInfo.id,
            name = self.name,
            company_name = company_name,
            role = role,
            duration = duration,
            location = location,
            government_experience = gov_exp
        )
        if self.presist_to_db:
            self.db_session.add(linkedInUserProfileWorkExperience)
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
    
    def scrapeProfileInfo(self, i, file_name, profile):
        with open(file_name, "r+") as json_file:
            if not profile:
                profiles_dict = {
                    "NameSearched": self.name_search,
                    "CompanySearched": self.company_search,
                    "SuccessfulGoogleQuery": False,
                    "ProfilesScraped": []
                }
            else:
                self.correct_name = False
                self.correct_company = False
                self.work_for_gov = False
                self.gov_experience = []
                self.prev_gov_exp_dict = {}
                self.driver.get(profile)
                sleep(3)
                main_profile_info = self.scrapeMainProfileSection()
                self.name = main_profile_info["name"]
                if self.getMatchingScoreForTwoTexts(main_profile_info["current_company"], self.company_search) >= 70:
                    self.correct_company = True
                self.linkedInProfileInfo = LinkedInProfileInfo(
                    name = main_profile_info["name"],
                    profile_title = main_profile_info["profile_title"],
                    sub_title = main_profile_info["sub_title"],
                    current_company = main_profile_info["current_company"],
                    university = main_profile_info["university"],
                    linkedin_url = main_profile_info["linkedin_url"]
                )
                if self.presist_to_db:
                    self.db_session.add(self.linkedInProfileInfo)
                    self.db_session.commit()
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
                profiles_dict = {
                    "NameSearched": self.name_search,
                    "CompanySearched": self.company_search,
                    "SuccessfulGoogleQuery": True,
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
                linkedInUserProfileIdentification = LinkedInUserProfileIdentification(
                    profile_id=self.linkedInProfileInfo.id,
                    name=self.name,
                    correct_company=self.correct_company,
                    correct_name=self.correct_name,
                    worked_for_gov=self.work_for_gov
                )
                if self.presist_to_db:
                    self.db_session.add(linkedInUserProfileIdentification)
                    self.db_session.commit()
            json_file.seek(os.stat(file_name).st_size -1)
            if i == 0:
                json_file.write( "{}]".format(json.dumps(profiles_dict)))
            else:
                json_file.write( ",{}]".format(json.dumps(profiles_dict)))
