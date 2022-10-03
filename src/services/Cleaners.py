
import pandas as pd
def clean_person_name(df, column_name):
        df[f"{column_name}_clean"] = df[column_name].str.lower()
        df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(r'[^\w\s]+', '', regex = True)
        df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.strip()
        df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(' +', ' ', regex = True)

def clean_business_name(df, column_name):
    df[f"{column_name}_clean"] = df[column_name].str.lower()
    df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(r'\(.*\)', ' ', regex = True)
    remove_phrase = [
        ('pty', False), ('ltd', False), ('proprietary', False), ('limited', False), ('company', False), 
        (r'\.', True), ('no1', False), (r'\&amp;', True), ('incorporated', False)]

    for phrase in remove_phrase:
        df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(phrase[0], '', regex=phrase[1])

    df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(r'[^\w\s]+', ' ', regex = True)
    df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.strip()
    df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(' +', ' ', regex = True)


def clean_portfolio_name(df):
        remove_phrase = [
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
            'jul', 'aug', 'sept', 'oct', 'nov', 'dec', 'disclosure summary'
        ]
        df['portfolio_clean'] = df['portfolio'].str.replace(r'\d', '', regex = True)
        df['portfolio_clean'] = df['portfolio_clean'].str.lower()
        
        for phrase in remove_phrase:
            df['portfolio_clean'] = df['portfolio_clean'].str.replace(r'\b' + phrase + r'\b', '', regex = True)
        
        df['portfolio_clean'] = df['portfolio_clean'].str.replace(' +', ' ', regex = True)
        df['portfolio_clean'] = df['portfolio_clean'].str.replace('new south wales', 'nsw', regex = False)
        df['portfolio_clean'] = df['portfolio_clean'].str.strip()
        df.loc[df['portfolio_clean'].isin(['minister for industry resources and energy', 'minister for industry resources energy'])] = 'minister for resources energy'

def clean_abn(df, column_name):
    df[f'{column_name}_clean'] = df[column_name].astype(str)
    df[f'{column_name}_clean'] = df[f'{column_name}_clean'].str.replace('ABN', '')
    df[f'{column_name}_clean'] = df[f'{column_name}_clean'].str.replace('ACN', '')
    df[f'{column_name}_clean'] = df[f'{column_name}_clean'].str.split(',').str[0]
    df[f'{column_name}_clean'] = df[f'{column_name}_clean'].str.split('.').str[0]
    df[f'{column_name}_clean'] = pd.to_numeric(df[f'{column_name}_clean']).astype('Int64')