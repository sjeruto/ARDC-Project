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

An example of each of the lobbyist scrappers usage can be found in the TestScrappers.py script.

## Lobbyist Service

The lobbyist service class contains all the methods which query the lobbyist tables created by the lobbyist scrappers, below is an example of its usage:

```python
import sqlite3
from src.services.LobbyistService import LobbyistDataService
# pass in the path to the data.db file created by the scrappers
cnx = sqlite3.connect('../data.db')

lobbyistDataService = LobbyistDataService(cnx)

# gets a list of all lobbyist employee's
all_lobbyist_employees_df = lobbyistDataService.get_all_lobbyist_employees()
# gets a list of unique lobbyist organisations
unique_lobbyist_orgs_df = lobbyistDataService.get_unique_lobbyist_abns()
# gets a list of unique lobbyist employee's
unique_employees = lobbyistDataService.get_unique_employee_to_lobbyists()
# gets a list of al lobbyist clients
all_lobyist_clients_df = lobbyistDataService.get_all_lobbyist_clients()
```

When instanciating the LobbyistDataService class you need to pass in a database connection, in the above example we are passing in an sqlite3 connection which has been created by passing in the directory path to the data.db file, this example is using a relative path where the data.db file is in the parent directory of the execution directory.

## DiaryParser

The MinisterialDiaryParser class is used for parsing the ministerial diary PDF files, this code is based of the POC parser originally written by Gnana Bharathy at UTS, we have extracted this code from his notebooks and encapsulated it in a class, added extra error handlings, and implemented logic to persist the data to our database, below is an example of how to use this parser:

```python
from diary_parsers.DiaryParser import MinisterialDiaryParser
folder = 'NSW_pdfs'
jurisdiction = 'NSW'
parser = MinisterialDiaryParser(folder, jurisdiction)
data = parser.extract_data()
if len(parser.errors) > 0:
    for error in errors:
        print(error)
```

Similar to the lobbyist scrappers if the database does not alread exist it will create the database and table required using SQLAlchemy, if any errors are capture while it is parsing the PDF documents they will be stored in the errors property of the MinisterialDiaryParser class.

## Cleaners
