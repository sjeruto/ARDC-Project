
def clean_person_name(df, column_name):
        df[f"{column_name}_clean"] = df[column_name].str.lower()
        df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace('  ', ' ')
        df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(r'[^\w\s]+', '')

def clean_business_name(df, column_name):
    df[f"{column_name}_clean"] = df[column_name].str.lower()
    df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(r'\(.*\)', ' ')
    df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace('  ', ' ')
    df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(r'[^\w\s]+', ' ')
    remove_phrase = ['pty', 'ltd', 'proprietary', 'limited', 'company', r'\.', 'no1', '&amp;', 'incorporated']
    for phrase in remove_phrase:
        df[f"{column_name}_clean"] = df[f"{column_name}_clean"].str.replace(phrase, '')

def clean_portfolio_name(df):
        remove_phrase = [
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
            'jul', 'aug', 'sept', 'oct', 'nov', 'dec'
        ]
        df['portfolio_clean'] = df['portfolio'].str.replace(r'\d', '')
        df['portfolio_clean'] = df['portfolio_clean'].str.lower()
        for phrase in remove_phrase:
            df['portfolio_clean'] = df['portfolio_clean'].str.replace(r'\b' + phrase + r'\b', '')
