from scrappers.DonationsNswScraper import *

def nsw_scraper():
    scraper = DonationsNswScraper()
    scraper.listAllDonors()
    #scraper.navigateTo157Page()
    scraper.retrieveInfoAboutDonors()

    scraper.browserClose()

nsw_scraper()