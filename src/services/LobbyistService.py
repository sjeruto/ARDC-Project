import pandas as pd
from src.services.Cleaners import *
class LobbyistDataService():
    def __init__(self, db_connection):
        self.db_connection = db_connection

    # returns a dataframe of all lobbyist employees
    def get_all_lobbyist_employees(self):
        sql = """
        with lobbyist_abns as (
            select t.abn 
            from (
                select lf.abn
                from lobbyist_federal lf
                where lf.abn is not null
                union
                select lnsw.abn 
                from lobbyist_nsw lnsw
                where lnsw.abn is not null
                    and trim(lnsw.abn) != ''
                union
                select lq.abn 
                from lobbyist_qld lq
                where lq.abn is not null
                    and trim(lq.abn) != ''
                union
                select ls.abn 
                from lobbyist_sa ls 
                where ls.abn is not null
                    and trim(ls.abn) != ''
            ) t
            group by t.abn
        ), lobbyist_employees as (
            select abns.abn, lfe.lobbyists_name lobbyist_name, lfe.job_title title from lobbyist_abns abns
                inner join lobbyist_federal lf2 
                    on lf2.abn = abns.abn
                    and lf2.abn is not null
                inner join lobbyist_federal_employee lfe 
                    on lfe.organisations_abn is not null
                    and lfe.organisations_abn = abns.abn
            union
            select abns.abn, lne.name, lne.postion from lobbyist_nsw ln2 
                inner join lobbyist_abns abns
                    on ln2.abn = abns.abn
                inner join lobbyist_nsw_employee lne 
                    on lne.lobbyist_nsw_id = ln2.id
            union
            select abns.abn, lqe.name, lqe.position from lobbyist_abns abns
                inner join lobbyist_qld lq2 
                    on lq2.abn = abns.abn
                inner join lobbyist_qld_employee lqe 
                    on lqe.lobbyist_qld_id = lq2.id
            union
            select abns.abn, le.employee_name, le.employee_position  from lobbyist_sa_employee le
                inner join lobbyist_abns abns
                    on le.lobbyist_abn  = abns.abn
        )
        select le.abn lobbyist_abn, le.lobbyist_name, le.title
        from lobbyist_employees le
        group by le.abn, le.lobbyist_name, le.title
        """
        df = pd.read_sql(sql, self.db_connection)
        clean_person_name(df, 'lobbyist_name')
        clean_abn(df, 'lobbyist_abn')
        return df

    # returns a dataframe with all the uniqe lobbyist abn's
    def get_unique_lobbyist_abns(self):
        sql = """
        select t.abn 
        from (
            select lf.abn
            from lobbyist_federal lf
            where lf.abn is not null
            union
            select lnsw.abn 
            from lobbyist_nsw lnsw
            where lnsw.abn is not null
                and trim(lnsw.abn) != ''
            union
            select lq.abn 
            from lobbyist_qld lq
            where lq.abn is not null
                and trim(lq.abn) != ''
            union
            select ls.abn 
            from lobbyist_sa ls 
            where ls.abn is not null
                and trim(ls.abn) != ''
        ) t
        group by t.abn
        """
        return pd.read_sql(sql, self.db_connection)

    # returns a dataframe with all lobbyist clients
    def get_all_lobbyist_clients(self):
        sql = """
        with lobbyist_abns as (
            select t.abn 
            from (
                select lf.abn
                from lobbyist_federal lf
                where lf.abn is not null
                union
                select lnsw.abn 
                from lobbyist_nsw lnsw
                where lnsw.abn is not null
                    and trim(lnsw.abn) != ''
                union
                select lq.abn 
                from lobbyist_qld lq
                where lq.abn is not null
                    and trim(lq.abn) != ''
                union
                select ls.abn 
                from lobbyist_sa ls 
                where ls.abn is not null
                    and trim(ls.abn) != ''
            ) t
            group by t.abn
        ), lobbyist_clients as (
            select abns.abn, lfc.clients_name name from lobbyist_abns abns
                inner join lobbyist_federal_client lfc 
                    on lfc.organisations_abn is not null
                    and lfc.organisations_abn = abns.abn
            union
            select abns.abn, lnc.name from lobbyist_nsw ln2 
                inner join lobbyist_abns abns
                    on ln2.abn = abns.abn
                inner join lobbyist_nsw_client lnc  
                    on lnc.lobbyist_nsw_id = ln2.id
            union
            select abns.abn, lqc.name from lobbyist_abns abns
                inner join lobbyist_qld lq2 
                    on lq2.abn = abns.abn
                inner join lobbyist_qld_client lqc
                    on lqc.lobbyist_qld_id = lq2.id
            union
            select abns.abn, lc.client_name  from lobbyist_sa_client lc
                inner join lobbyist_abns abns
                    on lc.lobbyist_abn  = abns.abn
        )
        select lc.abn lobbyist_abn, lc.name from lobbyist_clients lc
        group by lc.abn, lc.name
        """
        df = pd.read_sql(sql, self.db_connection)
        clean_business_name(df, 'name')
        clean_abn(df, 'lobbyist_abn')
        return df

    
