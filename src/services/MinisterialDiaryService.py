import pandas as pd
from src.services.Cleaners import *

class MinisterialDiaryDataService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def clean_portfolio_name(self,df):
        remove_phrase = [
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
            'jul', 'aug', 'sept', 'oct', 'nov', 'dec'
        ]
        df['portfolio_clean'] = df['portfolia'].str.replace(r'\d', '')
        df['portfolio_clean'] = df['portfolio_clean'].str.lower()
        for phrase in remove_phrase:
            df['portfolio_clean'] = df['portfolio_clean'].str.replace(r'\b' + phrase + r'\b', '')

    def clean_organisation_individual(self, df):
        df["organisation_individual_clean"] = df["organisation_individual"].str.replace(r'[^\w\s]+', '')
        df["organisation_individual_clean"] = df["organisation_individual_clean"].str.lower()

    def get_diary_entries(self, state_filter = None):
        filter = ''
        if state_filter is not None:
            filter = f"where md.jurisdiction = '{state_filter}'"
        sql = f"""
        select * from ministerial_diary md 
        {filter}
        """
        df = pd.read_sql(sql, self.db_connection)
        clean_portfolio_name(df)
        clean_business_name(df, "organisation_individual")
        df["date"] = pd.to_datetime(df["date"], errors='coerce', format='%d/%m/%Y')
        return df