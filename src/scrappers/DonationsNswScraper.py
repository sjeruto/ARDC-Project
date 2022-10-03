from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

class DonationsNswScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://searchdecs.elections.nsw.gov.au/search.aspx")
        self.wait = WebDriverWait(self.driver, 30)

    def elementVisible(self, element):
        if element.is_displayed():
            print("Element visible")
            return True
        else:
            print("Element not visible")
            return False

    def clickElement(self, element, elementName):
        try:
            self.wait.until(EC.element_to_be_clickable(element))
            print("Clicking element: " + elementName)
            element.click()
        except:
            print("Could not click")
    
    def listAllDonors(self):
        disclosureType = Select(self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder_ddlType"))
        disclosureType.select_by_value("Donor")
        disclosurePeriod = Select(self.driver.find_element(By.ID, 'ctl00_ContentPlaceHolder_ddlReportPeriod'))
        disclosurePeriod.select_by_value("All")
        searchButton = self.driver.find_element(By.XPATH, "//input[@value=' Search ']")
        self.clickElement(searchButton, "Search Button")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(),'Candidate/Member/Group/Party Name/Donor')]")))

    def nextPageNavigation(self, nextPageNumber):
        nextPageLocator = self.driver.find_element(By.XPATH, "//a[text()='" + str(nextPageNumber) + "']")
        self.clickElement(nextPageLocator, nextPageLocator.text)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(),'Candidate/Member/Group/Party Name/Donor')]")))
        sleep(3)
    
    def detailsAboutEachDonor(self, rows, columns, donorName):        
        for i in range(2, rows + 1):
            eachRow = []
            eachRow.append(donorName)
            for j in range(1, columns + 1):
                try:
                    self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    print("Locator:" + "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")
                    eachRow.append(self.driver.find_element(By.XPATH, "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]").text)
                except:
                    print("In except block")
                    self.refresh()
                    self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    print("Locator:" + "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")
                    eachRow.append(self.driver.find_element(By.XPATH, "//*[@id='resulttbl']/tbody/tr[" + str(i) + "]/td[" + str(j) + "]").text)
                print(eachRow)
            self.df.loc[len(self.df)] = eachRow
        if rows <= 5:
            sleep(3)
        self.closeTab()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(),'Click on the header to sort the column')]")))

    
    def nextTabNavigationForDonorDetails(self, donorLocators, j, i):
        if (i%2 == 0 and j%2 !=0) or (i%2 !=0 and j%2 == 0):
            sleep(3)
        else:
            sleep(4)
        self.clickElement(donorLocators[j], donorLocators[j].text)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ctl00_ContentPlaceHolder_tab6']/a")))

    def navigateDonationsMadeTab(self):
        sleep(2)
        donationsMade = self.driver.find_element(By.XPATH, "//*[@id='ctl00_ContentPlaceHolder_tab6']/a")
        self.clickElement(donationsMade, "Donations made")
        self.driver.execute_script("arguments[0].click();", donationsMade)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(), 'Date Donation Made')]")))
    
    def initializeDataFrameForDonationsMade(self, columns, i):
        colnames = []
        colnames.append("Donor Name")
        for l in range(1,columns+1):
            try:
                colnames.append(self.driver.find_element(By.XPATH, "//*[@id='resulttbl']/tbody/tr[1]/th[" + str(l) + "]").text)
            except:
                print('Exception thrown, Refreshing the webpage')
                self.refresh()
                colnames.append(self.driver.find_element(By.XPATH, "//*[@id='resulttbl']/tbody/tr[1]/th[" + str(l) + "]").text)
        print(colnames)
        self.df = pd.DataFrame(columns=colnames)
        if i == 0:
            self.createCsvHeaders()
    
    #def navigateTo157Page(self):
    #    for i in range(5,159,3):
    #        sleep(4)
    #        nextSetPages = self.driver.find_element(By.XPATH, "//a[contains(@onclick, 'javascript:setGotoPage(" + str(i) + ")')]")
    #        self.clickElement(nextSetPages, "Clicking: " + str(i))
    #    oneFiftySeven = self.driver.find_element(By.XPATH, "//a[text()='157']")
    #    self.clickElement(oneFiftySeven, "Clicking 157 page")
    #    sleep(10)
    
    def retrieveInfoAboutDonors(self):
        for i in range(248):
            if i != 0:
                self.nextPageNavigation(i+1)
            donorLocators = self.driver.find_elements(By.XPATH, "//table[@id='resulttbl']//td[1]//a")
            print("Length of dl:" + str(len(donorLocators)))
            for j in range(len(donorLocators)):
                donorName = donorLocators[j].text
                self.nextTabNavigationForDonorDetails(donorLocators=donorLocators, j=j, i=i+1)
                self.navigateDonationsMadeTab()

                rows = 1 + len(self.driver.find_elements(By.XPATH, "//*[@id='resulttbl']/tbody/tr/td[1]"))
                columns = len(self.driver.find_elements(By.XPATH, "//*[@id='resulttbl']/tbody/tr[1]/th"))
                
                if j == 0:
                    self.initializeDataFrameForDonationsMade(columns=columns, i=i)
                self.detailsAboutEachDonor(rows=rows, columns=columns, donorName=donorName)

            self.outputToCsv()

    def outputToCsv(self):
        self.df.to_csv('/Donations_scrape/output.csv', mode = 'a', index=False, header=False)

    def createCsvHeaders(self):
        self.df.to_csv('/Donations_scrape/output.csv', index=False)
    
    def browserClose(self):
        self.driver.quit()

    def closeTab(self):
        self.driver.close()

    def refresh(self):
        self.driver.refresh()