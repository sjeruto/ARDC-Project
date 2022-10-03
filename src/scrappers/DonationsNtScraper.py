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

    def initializeDataFrame(self, columns, tabHeading, year, donorType, receiptType):
        colnames = []
        if donorType == 'Individual' or donorType == 'Organisation':
            colnames.append("Donor Name")
            colnames.append("Donor Type")
        else:
            colnames.append("Political Party")
            colnames.append("Annual Returns Year")
        for l in range(1,columns+1):
            if l == 3 and receiptType == "Debts":
                colnames.append("Receipt type")
            try:
                colnames.append(self.driver.find_element(By.XPATH, "//h4[contains(text(),'" + tabHeading + "')]/../..//descendant::table/tbody/tr[1]/th[" + str(l) + "]").text)
            except:
                print("Exception thrown, refreshing page")
                self.driver.refresh()
                colnames.append(self.driver.find_element(By.XPATH, "//h4[contains(text(),'" + tabHeading + "')]/../..//descendant::table/tbody/tr[1]/th[" + str(l) + "]").text)
        print(colnames)
        self.df = pd.DataFrame(columns=colnames)

        if (year == "2014-2015" and donorType == "Individual") or (year == "2014-2015" and receiptType == "Receipts"):
            self.createCsvHeaders(type=donorType)

    def detailsAboutEachDonation(self, rows, columns, name, tabHeading, donorType, receiptType, year):
        for i in range(2,rows+2):
            eachRow = []
            eachRow.append(name)
            if donorType == 'Individual' or donorType == 'Organisation':
                eachRow.append(donorType)
            else:
                eachRow.append(year)
            for j in range(1,columns+1):
                if j == 3 and receiptType == 'Debts':
                    eachRow.append("Loan/Debt")
                try:
                    print("Locator:" + "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")
                    self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    eachRow.append(self.driver.find_element(By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]").text)
                except:
                    print("Exception thrown")
                    print("Locator:" + "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")
                    self.driver.refresh()
                    self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]")))
                    eachRow.append(self.driver.find_element(By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[" + str(i) + "]/td[" + str(j) + "]").text)
                
            print(eachRow)
            self.df.loc[len(self.df)] = eachRow
            sleep(4)

    def getNameFromTabHeading(self, tabHeading):
        headingArray = tabHeading.split(" -")
        return headingArray[0]

    def getDonorTabElements(self, year, donorType):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//a[text()='" + year + " annual returns']")))
        yearReturnsTab = self.driver.find_element(By.XPATH, "//a[text()='" + year + " annual returns']")
        self.clickElement(yearReturnsTab, "Year Returns Tab: " + year)

        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'" + year + " annual returns')]")))

        donorsTab = self.driver.find_element(By.XPATH, "//h2[text()='Donors (" + donorType + ")']")
        self.clickElement(donorsTab, "Donors (" + donorType + ") Tab")
        sleep(5)

        donationsMadeToPoliticalParties = self.driver.find_element(By.XPATH, "//h3[contains(text(),'Donors (" + donorType + ") - Donations made to political parties')]")
        self.clickElement(donationsMadeToPoliticalParties, "Donations Made To political parties (" + donorType + ")")
        sleep(5)

        donorTabs = self.driver.find_elements(By.XPATH, "//h3[contains(text(),'Donors (" + donorType + ") - Donations made to political parties')]/../..//descendant::h4[contains(text(), 'Donations made to political parties')]")
        sleep(5)
        return donorTabs

    def retrieveInfoAboutDonations(self, year, donorType, receiptType, tabElements):
        for i in range(len(tabElements)):
                tabHeading = tabElements[i].text
                sleep(5)
                self.clickElement(tabElements[i], "Tab: " + tabHeading)
                
                columns = len(self.driver.find_elements(By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr[1]/th"))
                rows = len(self.driver.find_elements(By.XPATH, "//h4[text()='" + tabHeading + "']/../..//descendant::table/tbody/tr/td[1]"))

                if i == 0:
                    self.initializeDataFrame(columns=columns, tabHeading=tabHeading, year=year, donorType=donorType, receiptType=receiptType)

                name = self.getNameFromTabHeading(tabHeading=tabHeading)
                self.detailsAboutEachDonation(rows=rows, columns=columns, name=name, tabHeading=tabHeading, donorType=donorType, 
                                                receiptType=receiptType, year=year)
                sleep(3)
                self.clickElement(tabElements[i], "Tab: " + tabHeading)

        self.outputToCsv(type=donorType)

    
    def retrieveDonations_DonorAnnualReturns(self):
        years = ['2014-2015','2015-2016','2016-2017','2017-2018','2018-2019','2020-2021']
        #years = ['2014-2015']

        for y in years:
            donorTabs = self.getDonorTabElements(year=y, donorType="Individual")
            self.retrieveInfoAboutDonations(year=y, donorType="Individual", receiptType=" ", tabElements=donorTabs)
            donorTabs = self.getDonorTabElements(year=y, donorType="Organisation")
            self.retrieveInfoAboutDonations(year=y, donorType="Organisation", receiptType=" ", tabElements=donorTabs)
            sleep(3)

    def openPoliticalPartiesTab(self, year):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//a[text()='" + year + " annual returns']")))
        yearReturnsTab = self.driver.find_element(By.XPATH, "//a[text()='" + year + " annual returns']")
        self.clickElement(yearReturnsTab, "Year Returns Tab: " + year)

        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'" + year + " annual returns')]")))

        politicalPartiesTab = self.driver.find_element(By.XPATH, "//h2[text()='Political Parties']")
        self.clickElement(politicalPartiesTab, "Political Parties Tab")
        sleep(5)

    def getPoliticalPartiesSubTabElements(self, receiptType):
        politicalPartiesReceiptTab = self.driver.find_element(By.XPATH, "//h3[text()='Political Parties - " + receiptType + " of $1500 or more']")
        self.clickElement(politicalPartiesReceiptTab, "Political Parties - " + receiptType + " of $1500 or more")
        sleep(4)

        politicalPartiesSubTab = self.driver.find_elements(By.XPATH, "//h3[text()='Political Parties - " + receiptType + " of $1500 or more']/../../descendant::h4[contains(text(),'" + receiptType + " of $1500 or more')]")
        sleep(5)
        return politicalPartiesSubTab

    def retrieveDonations_PoliticalPartiesAnnualReturns(self):
        years = ['2014-2015','2015-2016','2016-2017','2017-2018','2018-2019','2020-2021']
        #years = ['2014-2015']

        for y in years:
            self.openPoliticalPartiesTab(year=y)
            politicalPartiesSubTab = self.getPoliticalPartiesSubTabElements(receiptType="Receipts")
            self.retrieveInfoAboutDonations(year=y, donorType=" ", receiptType="Receipts", tabElements=politicalPartiesSubTab)
            politicalPartiesSubTab = self.getPoliticalPartiesSubTabElements(receiptType="Debts")
            self.retrieveInfoAboutDonations(year=y, donorType=" ", receiptType="Debts", tabElements=politicalPartiesSubTab)
            sleep(3)

    def outputToCsv(self, type):
        if type == "Individual" or type == "Organisation":
            self.df.to_csv('/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/ARDC-Project/output.csv', mode = 'a', index=False, header=False)
        else:
            self.df.to_csv('/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/ARDC-Project/output2.csv', mode = 'a', index=False, header=False)

    def createCsvHeaders(self, type):
        if type == "Individual":
            self.df.to_csv('/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/ARDC-Project/output.csv', index=False)
        else:
            self.df.to_csv('/Users/naeeramin/Documents/UTS_3rd_semester/ilab2/ARDC-Project/output2.csv', index=False)
    
    def browserClose(self):
        self.driver.quit()

    def closeTab(self):
        self.driver.close()




