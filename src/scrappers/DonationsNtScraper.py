from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


class DonationsNtScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://ntec.nt.gov.au/financial-disclosure/financial-disclosure-returns-legislative-assembly/annual-returns2/2019-2020-annual-returns")
        self.wait = WebDriverWait(self.driver, 30)

    def clickElement(self, element, elementName):
        try:
            self.wait.until(EC.element_to_be_clickable(element))
            print("Clicking element: " + elementName)
            element.click()
        except:
            print("Could not click: " + elementName)

    def initializeDataFrame(self, columns, donorTabHeading):
        colnames = []
        colnames.append("Donor Name")
        for l in range(1,columns+1):
            try:
                colnames.append(self.driver.find_element(By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[1]/th[" + str(l) + "]").text)
            except:
                print("Exception thrown, refreshing page")
                self.driver.refresh()
                colnames.append(self.driver.find_element(By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[1]/th[" + str(l) + "]").text)
        print(colnames)
        self.df = pd.DataFrame(columns=colnames)

        self.createCsvHeaders()

    def detailsAboutEachDonation(self, rows, columns, donorName, donorTabHeading):
        for i in range(2,rows+2):
            eachRow = []
            eachRow.append(donorName)
            for j in range(1,columns+1):
                try:
                    self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    print("Locator:" + "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")
                    eachRow.append(self.driver.find_element(By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]").text)
                except:
                    print("Exception thrown")
                    self.driver.refresh()
                    self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    print("Locator:" + "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")
                    eachRow.append(self.driver.find_element(By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]").text)
            print(eachRow)
            self.df.loc[len(self.df)] = eachRow
            sleep(4)

    def getDonorNameFromDonorTab(self, donorTabHeading):
        headingArray = donorTabHeading.split(" -")
        return headingArray[0]

    def retrieveIndividualDonors(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'2019-2020 annual returns')]")))

        individualDonorsTab = self.driver.find_element(By.XPATH, "//h2[text()='Donors (Individual)']")
        self.clickElement(individualDonorsTab, "Donors (Individual) Tab")
        sleep(5)

        donationsMadeToPoliticalParties = self.driver.find_element(By.XPATH, "//h3[contains(text(),'Donors (Individual) - Donations made to political parties')]")
        self.clickElement(donationsMadeToPoliticalParties, "Donations Made To political parties (individual)")
        sleep(5)

        donorTabs = self.driver.find_elements(By.XPATH, "//h3[contains(text(),'Donors (Individual) - Donations made to political parties')]/../..//descendant::h4[contains(text(), 'Donations made to political parties')]")
        sleep(5)

        for i in range(len(donorTabs)):
            donorTabHeading = donorTabs[i].text
            sleep(5)
            self.clickElement(donorTabs[i], "Donor tab: " + donorTabHeading)
            
            columns = len(self.driver.find_elements(By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr[1]/th"))
            rows = len(self.driver.find_elements(By.XPATH, "//h4[contains(text(),'" + donorTabHeading + "')]/../..//descendant::table/tbody/tr/td[1]"))

            if i == 0:
                self.initializeDataFrame(columns=columns, donorTabHeading=donorTabHeading)

            donorName = self.getDonorNameFromDonorTab(donorTabHeading=donorTabHeading)
            self.detailsAboutEachDonation(rows=rows, columns=columns, donorName=donorName, donorTabHeading=donorTabHeading)
            sleep(3)
            self.clickElement(donorTabs[i], "Donor tab: " + donorTabHeading)

        self.outputToCsv()



    def outputToCsv(self):
        self.df.to_csv('/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/ARDC-Project/output.csv', mode = 'a', index=False, header=False)

    def createCsvHeaders(self):
        self.df.to_csv('/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/ARDC-Project/output.csv', index=False)
    
    def browserClose(self):
        self.driver.quit()

    def closeTab(self):
        self.driver.close()

    


