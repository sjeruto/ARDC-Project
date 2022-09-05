import os
import sys
import pandas as pd
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import sqlite3
cnx = sqlite3.connect('data.db')
import numpy as np
import regex as re

from src.services.MinisterialDiaryService import *

from src.services.LobbyistService import LobbyistDataService
lobbyistDataService = LobbyistDataService(cnx)
all_lobbyist_employees_df = lobbyistDataService.get_all_lobbyist_employees()
all_lobbyist_clients_df = lobbyistDataService.get_all_lobbyist_clients()

ministerDataService = MinisterialDiaryDataService(cnx)
diaries_df = ministerDataService.get_diary_entries(state_filter = "NSW")

from src.services.Cleaners import *
mining_data_df = pd.read_csv('NSW_Mining_data.csv')
clean_business_name(mining_data_df, 'company')

class Searcher:
    def __init__(self, employees_df, mining_data_df, clients_df, diaries_df):
        self.employee_associations = []
        self.client_associations = []
        self.mining_company_associations = []
        self.employees_df = employees_df
        self.clients_df = clients_df
        self.mining_data_df = mining_data_df
        self.link_to_lobbyist_employee_name = np.vectorize(self._link_to_lobbyist_employee_name)
        self.is_client_mining_company = np.vectorize(self._is_client_mining_company)
        self.mining_company_names = []
        self.link_to_mining_company = np.vectorize(self._link_to_mining_company)
        self.diaries_df = diaries_df

    ##############################################################
    #       Mining Companies
    ##############################################################

    def get_mining_company_names_clean(self):
        if len(self.mining_company_names) == 0:
            # a manual list of mining companies 
            mining_companies = [
                # http://iminco.net/queensland-mining-companies/
                'Adani Mining', 'Anglo Coal', 'BHP Billiton', 'Caledon Coal', 'Carabella Resources', 'Citigold', 'Ensham Resources',
                'Ernest Henry Mining', 'Jellinbah Group', 'New Hope Coal','Newlands Coal', 'Oaky Creek Coal','Opal Horizon','Peabody Energy',
                'Perilya Mines', 'Qcoal','Rio Tinto','Yancoal',
                # http://iminco.net/mining-companies-australia/
                'Bechtel', 'Cuesta Coal', 'Fortescue Metals','GLOUCESTER COAL','GVK Industries',
                'Hancock Prospecting', 'Tinkler', 'Newmont Corporation','OZ MINERALS' ,'Xstrata','NSW Minerals Council'
            ]
            
            mining_companies_df = pd.DataFrame({ 'company_name': mining_companies })
            clean_business_name(mining_companies_df, 'company_name')
            mining_companies = mining_companies_df['company_name'].unique().tolist()

            # and from the mining leases data
            [mining_companies.append(name) for name in self.mining_data_df['company_clean'].unique() 
                if name not in mining_companies and 'deceased' not in name]

            self.mining_company_names = mining_companies

        return self.mining_company_names

    def _is_client_mining_company(self, client_name):
        mining_companies = self.get_mining_company_names_clean()
        found = [name for name in mining_companies if name in client_name or client_name in name]
        for f in found:
            self.client_associations.append({ 'client_name': client_name, 'mining_company_name': f})
        
        return len(found) > 0

    def get_client_associations_df(self):
        self.is_client_mining_company(self.clients_df['name_clean'])
        mining_associations_df = pd.DataFrame(self.client_associations)
        return mining_associations_df.merge(self.clients_df, left_on = 'client_name', right_on = 'name_clean')

    def _link_to_mining_company(self, organisation_individual, id):
        mining_companies = self.get_mining_company_names_clean()
        found = [name for name in mining_companies if name in organisation_individual]
        [self.mining_company_associations.append({ 'ministerial_diary_id': id, 'company_name': name, 'organisation_individual': organisation_individual}) 
            for name in found]
        return len(found) > 0

    def get_mining_company_associations_df(self):
        evaluate = lambda n, o : len(re.findall(r'\b' + n + r'\b', o)) > 0
        for a in self.mining_company_associations:
            a['match'] = evaluate(a['company_name'], a['organisation_individual'])
        
        mining_company_associations_df = pd.DataFrame(self.mining_company_associations)
        mining_company_associations_df = mining_company_associations_df[mining_company_associations_df['match'] == True]
        return mining_company_associations_df.merge(self.diaries_df[['id', 'portfolio_clean']], left_on = 'ministerial_diary_id', right_on = 'id')


    ##############################################################
    #       Lobbyist Employees
    ##############################################################

    def _link_to_lobbyist_employee_name(self, organisation_individual, id):
        employee_names = self.employees_df['lobbyist_name_clean'].unique()
        found = [name for name in employee_names if name in organisation_individual]
        [self.employee_associations.append({ 'ministerial_diary_id': id, 'lobbyist_name': name, 'organisation_individual': organisation_individual}) 
            for name in found]
        return len(found) > 0

    def get_employee_associations(self):  
        evaluate = lambda n, o : len(re.findall(r'\b' + n + r'\b', o)) > 0
        for a in self.employee_associations:
            a['match'] = evaluate(a['lobbyist_name'], a['organisation_individual'])

        employee_associations_df = pd.DataFrame(self.employee_associations)
        employee_associations_df = employee_associations_df[employee_associations_df['match'] == True]
        return employee_associations_df

    def get_associated_employees_df(self):
        associations_df = self.get_employee_associations()
        local_employees_df = self.employees_df[['title', 'lobbyist_name_clean', 'lobbyist_abn_clean']]
        result_df = associations_df.merge(
            local_employees_df
            , left_on = 'lobbyist_name'
            , right_on = 'lobbyist_name_clean'
        ).merge(self.diaries_df[['id', 'portfolio_clean']], left_on = 'ministerial_diary_id', right_on = 'id')
        return result_df
    

    
search = Searcher(all_lobbyist_employees_df, mining_data_df, all_lobbyist_clients_df, diaries_df)
# search.link_to_lobbyist_employee_name(diaries_df['organisation_individual_clean'], diaries_df['id'])
# print(search.employee_associations)
search.link_to_mining_company(diaries_df['organisation_individual_clean'], diaries_df['id'])
mining_associations_df = search.get_mining_company_associations_df()
print(mining_associations_df)