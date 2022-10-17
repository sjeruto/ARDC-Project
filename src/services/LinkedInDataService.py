import pandas as pd

class LinkedInDataService():
    def __init__(self, db_connection):
        self.db_connection = db_connection

    # returns a dataframe of all lobbyist employees with their work experience
    def get_all_lobbyist_employees_with_work_experience(self):
        sql = """
        SELECT lp1.name, lp1.current_company, lp1.profile_title,lp1.sub_title, lp1.university, lp2.company_name, 
        lp2.role, lp2.duration, lp2.location, lp2.government_experience, lp3.correct_name, lp3.correct_company, lp3.worked_for_gov
        FROM linkedin_profile_info lp1
        INNER join linkedin_user_work_experience  lp2 on lp1.id = lp2.profile_id
        INNER join linkedin_user_profile_identification lp3 on lp1.id = lp3.profile_id
        """
        df = pd.read_sql(sql, self.db_connection)
        return df

    # returns a dataframe of all lobbyist employees with their profile identification stats
    def get_all_lobbyist_employees_with_profile_identification_stats(self):
        sql = """
        SELECT  lp1.name, lp1.current_company, lp1.profile_title,lp1.sub_title, lp1.university,  
        lp2.correct_name, lp2.correct_company, lp2.worked_for_gov
        FROM linkedin_profile_info lp1
        INNER JOIN linkedin_user_profile_identification lp2 on lp1.id = lp2.profile_id
        """
        df = pd.read_sql(sql, self.db_connection)
        return df