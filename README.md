# Tracking Transparency- ARDC Project
This is a repository for ilab2 group project which is an exploratory research on the influence of lobbyist organisations in policy making in Australia. The aim of the project is to link different datasets together.

## Project Description
The repository contaains working web scrapers collected from various states (NSW, SA, Queensland and Federal state). These are 
1. LinkedIn Scraper
2. Political donations scraper
3. Lobbyist registers scrapers

The repository also includes codes for running the NLP analysis and visualisation.
The NLP codes cover Named Entity Recognition(NER) and sentiment analysis.
 

## Lobbyist Scrappers

The lobbyist scrappers are located in the scrappers directory, there are currently 4 lobbyist register scrappers, they are as follows:

1. LobbyistSaScrapper.py - Scrapes lobbyist data from the South Australian lobbyist register.
2. LobbyistFederalScrapper.py - Scrapes lobbyist data from the Federal lobbyist register.
3. LobbyistNswScrapper.py - Scrapes lobbyist data from the New South Wales lobbyist register. 
4. LobbyistQldScrapper.py - Scrapes lobbyist data from the Queensland lobbyist register.

Below is an example of how you can use on of these scrappers:

```python
from scrappers.LobbyistNswScrapper import *
# the persist_to_db argument will persist the scrapped data to an SQLite database
scrapper = LobbyistNswScrapper(persist_to_db=True)
# the scrape method will return the data scrapped
lobbyists = scrapper.scrape()
```

All of the lobbyist register scrappers can be used the same way, if you pass True into the 'persist_to_db' argument then the data will be persisted to an SQLite database, if the database does not exist it will create the database file in the directory your code is executing from, it will use the SQLAlchemey framework to create all the necessary tables and persist the data.

The lobbyist scrappers implement retry logic in the event of a runtime error, the 'max_retry' argument can be used to increase the defaul max_retry of 5, the scrappers use Selenium webdriver to scrape the websites and we provide an additional argumet to control whether Selenium runs in headless mode or not, this argument is called 'run_headless' and is defualted to True.

