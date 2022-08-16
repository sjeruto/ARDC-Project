from scrappers.LobbyistNswScrapper import *

import json
scrapper = LobbyistNswScrapper()
lobbyists = scrapper.get_lobbyists()

scrapper.populate_details(lobbyists[0])

for client in lobbyists[0].clients:
    print(f"{json.dumps(client.__dict__)}")


scrapper.close()