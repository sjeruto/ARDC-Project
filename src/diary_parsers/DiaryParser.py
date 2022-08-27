import camelot.io as camelot
import pandas as pd
import numpy as np
import glob
import ntpath
import regex as re

from model.models import *

# class NswMinisterialDiaryEntry:
#     __tablename__ = "ministerial_diary_nsw"
#     def __init__(self, date, portfolio, organisation_individual, purpose_of_meeting):
#         self.date = date
#         self.portfolio = portfolio
#         self.organisation_individual = organisation_individual
#         self.purpose_of_meeting = purpose_of_meeting

    

class MinisterialDiaryParser:
    def __init__(self, directory_path, jurisdiction, persist_to_db = True):
        self.entries = []
        self.directory_path = directory_path
        self.errors = []
        self.jurisdiction = jurisdiction
        self.persist_to_db = persist_to_db

        if self.persist_to_db:
            self.db_session = Session(engine)
            Base.metadata.create_all(engine)
    
    def extract_data(self):
        pdf_files = glob.glob(f"{self.directory_path}/*.pdf")
        for file_path in pdf_files:
            path, file_name = ntpath.split(file_path)
            print(f'parsing {file_name}...')
            portfolio = self.get_portfolio(file_name)
            try:
                entries = self.extract_tables(file_path, portfolio, file_name)
                if self.persist_to_db:
                    self.db_session.add_all(entries)
                    self.db_session.commit()
                self.entries = self.entries + entries
            except Exception as ex:
                self.errors.append(f'{file_name}, {str(ex)}\n')
                continue


    def get_portfolio(self, file_name):
        file_name_parts = re.split("-|_", file_name)
        months =  ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        portfolio = ""
        for prt in file_name_parts:
            if isinstance(prt, int) or prt in months or "pdf" in prt:
                pass
            else:
                portfolio += prt +" "
        return portfolio

    def extract_tables(self, file, portfolio, file_name):
        tables = camelot.read_pdf(file, pages='all')
        next_purpose = ""
        next_date = ""
        entries = []
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

                        entry = MinisterialDiaryEntry(
                            date = date,
                            portfolio = portfolio,
                            organisation_individual = org,
                            purpose_of_meeting = purpose,
                            jurisdiction = self.jurisdiction,
                            import_file_name = file_name
                        )
                        entries.append(entry)
        return entries