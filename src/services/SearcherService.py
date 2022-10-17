import pandas as pd
import numpy as np
import regex as re
from src.services.Cleaners import *

class Searcher:
    def __init__(self, employees_df, mining_data_df, clients_df, diaries_df, unique_lobbyist_orgs_df):
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
        self.unique_lobbyist_orgs_df = unique_lobbyist_orgs_df

    ##############################################################
    #       Mining Companies
    ##############################################################

    # gets a list of company names
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
            
            mining_companies = mining_companies_df['company_name'].unique().tolist()

            # and from the mining leases data
            [mining_companies.append(name) for name in self.mining_data_df['company_clean'].unique() 
                if name not in mining_companies and 'deceased' not in name]

            self.mining_company_names = pd.DataFrame({ 'company_name': mining_companies})
            clean_business_name(self.mining_company_names, 'company_name')
            self.mining_company_names = self.mining_company_names['company_name_clean'].tolist()

        return self.mining_company_names

    # checks if the string value passed in is a mining company name
    # and builds up a list of client associations
    def _is_client_mining_company(self, client_name):
        mining_companies = self.get_mining_company_names_clean()
        found = [name for name in mining_companies if name in client_name or client_name in name]
        for f in found:
            self.client_associations.append({ 'client_name': client_name, 'mining_company_name': f})
        
        return len(found) > 0

    # builds up a list of client associations to mining companies then returns
    # a dataframe with mining companies joined to lobbyist clients
    def get_client_associations_df(self):
        self.is_client_mining_company(self.clients_df['name_clean'])
        mining_associations_df = pd.DataFrame(self.client_associations).drop_duplicates()
        return mining_associations_df.merge(self.clients_df, left_on = 'client_name', right_on = 'name_clean')

    # checks if the string value passed in contains a mining company name
    # and builds up a list on mining company associations to the ministerial diaries
    def _link_to_mining_company(self, organisation_individual, id):
        mining_companies = self.get_mining_company_names_clean()
        found = [name for name in mining_companies if name in organisation_individual]
        [self.mining_company_associations.append({ 'ministerial_diary_id': id, 'company_name': name, 'organisation_individual': organisation_individual}) 
            for name in found]
        return len(found) > 0

    # goes through the list of mining company associations to ministerial diary
    # entries and returns a data from of mining companies joined to ministerial diaries
    def get_mining_company_associations_df(self):

        # check that the name is surrounded by word boundries
        evaluate = lambda n, o : len(re.findall(r'\b' + n + r'\b', o)) > 0
        for a in self.mining_company_associations:
            a['match'] = evaluate(a['company_name'], a['organisation_individual'])
        
        mining_company_associations_df = pd.DataFrame(self.mining_company_associations).drop_duplicates()
        mining_company_associations_df = mining_company_associations_df[mining_company_associations_df['match'] == True]
        return mining_company_associations_df.merge(self.diaries_df[['id', 'portfolio_clean', 'date']], left_on = 'ministerial_diary_id', right_on = 'id')


    ##############################################################
    #       Lobbyist Employees
    ##############################################################

    # checks if the string value passed in contains the name of a lobbyist employee
    # build up a list of employee associations
    def _link_to_lobbyist_employee_name(self, organisation_individual, id):
        employee_names = self.employees_df['lobbyist_name_clean'].unique()
        found = [name for name in employee_names if name in organisation_individual]
        [self.employee_associations.append({ 'ministerial_diary_id': id, 'lobbyist_name': name, 'organisation_individual': organisation_individual}) 
            for name in found]
        return len(found) > 0

    # performs further filtering of the employee associations ensuring
    # names a surrounded by word boundries then returns as dataframe
    def get_employee_associations(self):  

        # check that the name is surrounded by word boundries
        evaluate = lambda n, o : len(re.findall(r'\b' + n + r'\b', o)) > 0
        for a in self.employee_associations:
            a['match'] = evaluate(a['lobbyist_name'], a['organisation_individual'])

        employee_associations_df = pd.DataFrame(self.employee_associations).drop_duplicates()
        employee_associations_df = employee_associations_df[employee_associations_df['match'] == True]
        return employee_associations_df

    # joins the employee associations  with the employee dataframe and diaries dataframe
    def get_associated_employees_df(self):
        associations_df = self.get_employee_associations()
        local_employees_df = self.employees_df[['title', 'lobbyist_name_clean', 'lobbyist_abn_clean']]
        result_df = associations_df.merge(
            local_employees_df
            , left_on = 'lobbyist_name'
            , right_on = 'lobbyist_name_clean'
        ).merge(self.diaries_df[['id', 'portfolio_clean', 'date']], left_on = 'ministerial_diary_id', right_on = 'id')
        return result_df

    def get_employees_linked_to_diaries(self):
        self.link_to_lobbyist_employee_name(self.diaries_df['organisation_individual_clean'], self.diaries_df['id'])
        associated = self.get_associated_employees_df()
        associated = associated.merge(self.unique_lobbyist_orgs_df, left_on = 'lobbyist_abn_clean', right_on = 'abn_clean')[[
            'ministerial_diary_id', 'lobbyist_name_clean', 'title', 'portfolio_clean', 'lobbyist_org_name', 'lobbyist_abn_clean', 'date']].drop_duplicates()
        return associated

    def get_mining_companies_linked_to_diaries_via_lobbyists(self):
        associated = self.get_employees_linked_to_diaries()
        mining_company_associations = self.get_client_associations_df()
        mining_company_associations = mining_company_associations.merge(self.unique_lobbyist_orgs_df, left_on = 'lobbyist_abn_clean', right_on = 'abn_clean')[[
            'client_name', 'mining_company_name', 'name', 'lobbyist_abn_clean' #, 'lobbyist_org_name'
            ]].drop_duplicates()
        mining_company_associations = mining_company_associations.merge(associated, left_on = 'lobbyist_abn_clean', right_on = 'lobbyist_abn_clean').drop_duplicates()
        return mining_company_associations

    def get_mining_companies_linked_to_diaries(self):
        self.link_to_mining_company(self.diaries_df['organisation_individual_clean'], self.diaries_df['id'])
        mining_associations_df = self.get_mining_company_associations_df()
        return mining_associations_df