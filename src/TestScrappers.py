from scrappers.LobbyistNswScrapper import *
import json

from scrappers.LobbyistQldScrapper import *

def test_nsw_scrapper():
    scrapper = LobbyistNswScrapper(persist_to_db=False)
    # lobbyists = scrapper.get_lobbyists()
    lobbyists = scrapper.scrape()

    print('Lobbyists:')
    for lobbyist in lobbyists[0:5]:
        print(f"{json.dumps(lobbyist.as_dict())}")

    print('Clients:')
    for client in lobbyists[0].clients:
        print(f"{json.dumps(client.__dict__)}")

    print('Employees:')
    for employee in lobbyists[0].employees:
        print(f"{json.dumps(employee.__dict__)}")

    print('Owners:')
    for owner in lobbyists[0].owners:
        print(f"{json.dumps(owner.__dict__)}")

    scrapper.close()

def test_qld_scrapper():
    scrapper = LobbyistQldScrapper(persist_to_db=True)
    # lobbyists = scrapper.get_lobbyists()
    lobbyists = scrapper.scrape()
    # scrapper.populate_details(lobbyists[3])

    print('Lobbyists:')
    for lobbyist in lobbyists[0:5]:
        print(f"{json.dumps(lobbyist.as_dict())}")
    
    print('Clients:')
    for client in lobbyists[3].clients:
        print(f"{json.dumps(client.as_dict())}")

    print('Employees:')
    for employee in lobbyists[3].employees:
        print(f"{json.dumps(employee.as_dict())}")

    print('Owners:')
    for owner in lobbyists[3].owners:
        print(f"{json.dumps(owner.as_dict())}")

test_qld_scrapper()