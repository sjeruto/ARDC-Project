from scrappers.DonationsNswScraper import *
from scrappers.DonationsNtScraper import *

def nsw_scraper():
    scraper = DonationsNswScraper()
    scraper.listAllDonors()
    #scraper.navigateTo157Page()
    scraper.retrieveInfoAboutDonors()

    scraper.browserClose()

def nt_scraper():
    scraper = DonationsNtScraper()
    scraper.retrieveIndividualDonors()


#nsw_scraper()

nt_scraper()