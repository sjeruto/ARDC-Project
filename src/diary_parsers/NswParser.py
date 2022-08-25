import camelot.io as camelot
import pandas as pd
import numpy as np
import glob
import ntpath

class NswMinisterialDiaryEntry:
    def __init__(self, date, portfolio, organisation_individual, purpose_of_meeting):
        self.date = date
        self.portfolio = portfolio
        self.organisation_individual = organisation_individual
        self.purpose_of_meeting = purpose_of_meeting

class NswParser:
    def __init__(self, directory_path):
        self.entries = []
        self.directory_path = directory_path
        self.errors = []
    
    def extract_data(self):
        pdf_files = glob.glob(f"{self.directory_path}/*.pdf")
        for file_path in pdf_files:
            path, file_name = ntpath.split(file_path)
            print(f'parsing {file_name}...')
            portfolio = self.get_portfolio(file_name)
            try:
                self.extract_tables(file_path, portfolio)
            except Exception as ex:
                self.errors.append(f'{file_name}, {str(ex)}')
                continue


    def get_portfolio(self, file_name):
        file_name_parts = file_name.split("-")
        months =  ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        portfolio = ""
        for prt in file_name_parts:
            if isinstance(prt, int) or prt in months or "pdf" in prt:
                pass
            else:
                portfolio += prt +" "
        return portfolio

    def extract_tables(self, file, portfolio):
        tables = camelot.read_pdf(file, pages='all')

        for table in tables:
            for idx, row in table.df.iterrows():
                if row[0] == "":
                    date = next_date
                else:
                    date = row[0]
                
                purpose = row[2]
                if purpose == "":
                        purpose = next_purpose  #if the next page does not have date or purpose take it from previous page
                        
                if "Date" not in row[0] and "ate" not in row[0]:
                    orgs = row[1].split("\n")
                    next_date = date
                    next_purpose = purpose #if the next page does not have date or purpose take it from previous page
                    for org in orgs:
                        org = org.replace("¬†", " ")

                        entry = NswMinisterialDiaryEntry(
                            date = date,
                            portfolio = portfolio,
                            organisation_individual = org,
                            purpose_of_meeting = purpose
                        )
                        self.entries.append(entry)