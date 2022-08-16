from scrappers.LobbyistNswScrapper import *

import json
scrapper = LobbyistNswScrapper()
lobbyists = scrapper.scrape()

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