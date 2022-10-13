from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class GoogleSearchForLinkedInUrls:
    def __init__(self, name_search, company_search, driver):
        self.driver = driver
        self.name_search = name_search
        self.company_search = company_search

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
            profile_urls = []

            # To check the list content we run the following command
            [profile_urls.append(users.get_attribute("href")) for users in linkedin_users_urls_list]
            first_profile_per_page = []
            if profile_urls:
                first_profile_per_page.append(profile_urls[0])
                print(first_profile_per_page)
            return first_profile_per_page
            