# Tracking Transparency- ARDC Project
This is a repository for ilab2 group project which is an exploratory research on the influence of lobbyist organisations in policy making in Australia. The aim of the project is to link different datasets together.

## Project Description
The repository contains working web scrapers collected from various states (NSW, SA, Queensland and Federal state). These are 
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

## Diary Parser

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

## Ministerial Diary Service

The ministerial diaries data can be access from the database using the MinisterialDiaryDataService class, below is an example of its usage:

```python
import sqlite3
from src.services.MinisterialDiaryService import *

# pass in the path to the data.db file created by the scrappers
cnx = sqlite3.connect('../data.db')

ministerDataService = MinisterialDiaryDataService(cnx)
diaries_df = ministerDataService.get_diary_entries(state_filter = "NSW")
```
## Searcher

The searcher services is how we link the mining companies to lobbyist organisations and ministerial diaries, below is an example of its usage:

```python
import sqlite3
from src.services.MinisterialDiaryService import *
import src.services.Searcher

# pass in the path to the data.db file created by the scrappers
cnx = sqlite3.connect('../data.db')

ministerDataService = MinisterialDiaryDataService(cnx)
diaries_df = ministerDataService.get_diary_entries(state_filter = "NSW")
from src.services.LobbyistService import LobbyistDataService
lobbyistDataService = LobbyistDataService(cnx)
all_lobbyist_employees_df = lobbyistDataService.get_all_lobbyist_employees()
unique_lobbyist_orgs_df = lobbyistDataService.get_unique_lobbyist_abns()
all_lobyist_clients_df = lobbyistDataService.get_all_lobbyist_clients()
from src.services.Cleaners import *
mining_data_df = pd.read_csv('../NSW_Mining_data.csv')
clean_business_name(mining_data_df, 'company')

search = Searcher(all_lobbyist_employees_df, mining_data_df, all_lobyist_clients_df, diaries_df, unique_lobbyist_orgs_df)

# gets a list of company names
mining_company_names = search.get_mining_company_names_clean()

# builds up a list of client associations to mining companies then returns
# a dataframe with mining companies joined to lobbyist clients
client_associations = search.get_client_associations_df()

# goes through the list of mining company associations to ministerial diary
# entries and returns a data from of mining companies joined to ministerial diaries
mining_company_associations = search.get_mining_company_associations_df()

# performs further filtering of the employee associations ensuring
# names a surrounded by word boundries then returns as dataframe
employee_associations = search.get_employee_associations()

# joins the employee associations  with the employee dataframe and diaries dataframe
employee_diary_associations = search.get_associated_employees_df()

# gets a dataframe of mining companies joined to ministerial diaries entries, linked via lobbyist organisation
# of which they are a client
mining_companies_associated_with_diaries_via_lobbyists = search.get_mining_companies_linked_to_diaries_via_lobbyists()

# gets a dataframe of mining companies joined to ministerial diaries directly.
mining_companies_associated_with_diaries = search.get_mining_companies_linked_to_diaries()
```

 

## LinkedIn scraper
The LinkedIn scraper takes an input of the lobbyist employees' name, organisation and linkedin profile urls and scrapes those profiles and persists the data into the database.
#### Instructions to run the LinkedIn scraper
- Locate the `ProfileUrls.xlsx` file in the root directory and open it
- Insert the lobbyist employees' name, organisation name and the linkedin profile url
- Ensure that none of the cells in the excel file is empty
- Open the terminal in the root directory of the project
- Run the following command:
    - ```python3 -m src.linkedin_scraper.LinkedInScraperUsingProfileUrls```
- Once the program has finished running,
    - open the `employees_experience.csv` file to view all the scraped data
    - the data can also be viewed in the database by opening the `data.db` file

#### Changing the credentials of the LinkedIn user with which the data is scraped
- Navigate to the `Variables.py` in the `/src/linkedin_scraper` directory
- Open the file and enter the credentials of the new user in the following variables
    ```python
    my_username = "tsim12345679@gmail.com"
    my_password = "tsim2022."
    ```
- Finally, save the `Variables.py` file


#### Adding keywords with which the scraper looks for government experience
- Navigate to the `Variables.py` in the `/src/linkedin_scraper` directory
- Open the file and add keywords to list of keywords in the following variable:
    ```python
    gov_keywords
    ```
- Finally, save the `Variables.py` file

**Note** - For Mac users, the url format for the ChromeDriver installer has changed (as at 17th October 2022). As a result, the ChromeDriver installer for latest stable updates do not work. A fix has already been implemented but not released yet. For now, it can be fixed by changing few lines of code in the webdriver_manager module by following the instructions below:
- Navigate to `/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/webdriver_manager/drivers/chrome.py` file 
- Change the following bit of code on lines 31-32 from
    ```python
    if is_arch(os_type):
        return f"{os_type.replace('_m1', '')}_m1"
    ```
    to
    ```python
    if is_arch(os_type):
        return "mac_arm64"
    ```
    Source: https://github.com/SergeyPirogov/webdriver_manager/pull/445
    
Another version of the LinkedIn scraper can be run by retrieving the lobbyist employee names and their organisation names using Lobbyist Data Service and then running the LinkedIn scraper. The scraper would at first search for the linkedin profiles of those employees using google search and once found, scrape those profiles to see if they had previous government experience. Below is an example of its usage:
```python
   import sqlite3
   from src.linkedin_scraper.GoogleSearch import GoogleSearchForLinkedInUrls
   from src.services.LobbyistService import LobbyistDataService
   from webdriver_manager.chrome import ChromeDriverManager
   from src.linkedin_scraper.LinkedInScraper import LinkedInScraper
   from selenium import webdriver
   from selenium.webdriver.chrome.service import Service
   from src.services.LinkedInDataService import LinkedInDataService
   
   # Create a database connection by passing the path to the data.db file
   # Ensure the database has data about all the required lobbyist employees from the lobbyist register
   cnx = sqlite3.connect('data.db')
   # Pass the database connection object as an argument
   lobbyistDataService = LobbyistDataService(cnx)
   # Get all the unique Federal lobbyist employees
   unique_federal_employees = lobbyistDataService.get_unique_federal_lobbyist_employees()
   # Get all the lobbyist organisations
   unique_lobbyist_orgs_df = lobbyistDataService.get_unique_lobbyist_abns()
   # Join the lobbyist employees with the lobbyist organsiations to find the organisation names of the lobbyist employees
   federal_employees_org = unique_federal_employees.merge(unique_lobbyist_orgs_df, left_on='lobbyist_abn_clean', right_on='abn_clean')
   # Select only those lobbyists that had disclosed themseleves to be former government representatives
   federal_employees_with_govt_exp = federal_employees_org.query("former_govt_representative=='Yes'")
   # Create an instance of the ChromeWebDriver
   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
   for i in range(len(names_list)):
       # Create an instance of the LinkedInScraper by passing the lobbyist employee names, organisation names and webdriver
       scraper = LinkedInScraper(name_search=names_list[i], company_search=companies_list[i], driver=driver)
       if i == 0:
           # Log in to LinkedIn
           scraper.linkedInLogin()
       # Look for the linkedin profile urls via google search
       googleSearch = GoogleSearchForLinkedInUrls(name_search=names_list[i], company_search=companies_list[i], driver=driver)
       googleSearch.googleQuery()
       # Retrieve the linkedin profile urls
       profile = googleSearch.getlinkedInProfileUrls()
       # Pass the linkedin profile urls to the LinkedInScraper to scrape those profiles
       scraper.scrapeProfileInfo(i=i, file_name=file_name, profile=profile)
   # Create an instance of the LinkedInDataService class by passing the database connection object    
   linkedInDataService = LinkedInDataService(cnx)
   # get all the lobbyist employees along with their work experience scraped from linkedin
   lobbyist_employee_with_experience = linkedInDataService.get_all_lobbyist_employees_with_work_experience()
   # Write to a csv file
   lobbyist_employee_with_experience.to_csv("employees_experience.csv", index=False)
   driver.quit()
```
This particular example retrieves all the federal lobbyists who had disclosed themselves as former government representatives and looks for their linkedin profiles via google search and then scrapes those profiles to retrieve information about their work history.
    
 ## LinkedIn Data Service
The LinkedInDataService class contains all the methods that query the tables containing the LinkedIn data scraped by the LinkedIn scraper. Below is an example of its usage:
```python
   import sqlite3
   from src.services.LinkedInDataService import LinkedInDataService
   # pass the path to data.db file
   cnx = sqlite3.connect('../data.db')
   linkedInDataService = LinkedInDataService(cnx)
   # get all the lobbyist employees along with their work experience scraped from linkedin
   lobbyist_employee_with_experience = linkedInDataService.get_all_lobbyist_employees_with_work_experience()
```
Much like the LobbyistDataService class, the LinkedInDataService class needs to be instantiated with a database connection object. In the above example, a sqlite3 connection is passed to the LinkedInDataService class. The database connection was created beforehand by passing the path to the data.db file. In this case, a relative path was passed as the data.db file was stored in the root directory of the project.

## Political Donations Scraper
The Political Donations scraper scrapes the donations data from the [New South Wales Electoral Commission website](https://searchdecs.elections.nsw.gov.au/search.aspx) and the [Northern Territory Electoral Commission website](https://ntec.nt.gov.au/financial-disclosure/financial-disclosure-returns-legislative-assembly/annual-returns2/2019-2020-annual-returns) and then outputs the data into csv files. Below is an example of how to use the scrapers:
```python
   from scrappers.DonationsNswScraper import *
   # Instatiates the DonationsNswScraper class
   scraper = DonationsNswScraper()
   # Creates a list of all the donors
   scraper.listAllDonors()
   # Retrieves the data about all the donors and outputs it into a csv
   scraper.retrieveInfoAboutDonors()
   # Closes the browser
   scraper.browserClose()
```
The `DonationsScraper.py` file in the `/src` directory contains the code to run the donations scrapers.



## News tool

The News tool takes a mandatory input 'query_keywords ' and allows you to choose additional filters

#### Instructions to run the LinkedIn scraper
- Open the notebook
- Set query term and filters
- Run the whole notebook
- See plots and dataframe.
