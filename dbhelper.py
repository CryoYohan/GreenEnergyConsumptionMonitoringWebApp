import mysql.connector as mariadb
from sqlite3 import connect, Row
class Databasehelper:
    def __init__(self)->None:
        # self.host = 'localhost'
        # self.user = 'root'
        # self.password = ''
        # self.database_old = 'energreen'
        self.database = 'energreen.db'

    def getdb_connection(self):
        # connection = mariadb.connect(
        #     host= self.host,
        #     user= self.user,
        #     password= self.password,
        #     database= self.database
        # )
        # return connection 
        connection = connect(self.database)
        return connection
    
    def getprocess(self,sql:str):
        connection = self.getdb_connection()
        cursor = connection.cursor()    
        cursor.execute(sql)
        cursor.row_factory = Row
        data:list = cursor.fetchall()  # Convert rows to dictionaries
        cursor.close()
        connection.close()
        return data 

    def postprocess(self,sql:str):
        connection = self.getdb_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close() 

    def getall_users(self, table:str)->list:
        query = f"SELECT * FROM {table}"
        users:list = self.getprocess(query)
        return users
    
    def getall_inventory(self, table:str,email:str)->list:
        query = f"SELECT * FROM {table} WHERE `email` = '{email}'"
        inventory:list = self.getprocess(query)
        return inventory

    def getall_joinedrecords(self):
        query = "SELECT DISTINCT u.email, u.fullname, i.panelname, i.panel_quantity, i.tariffcompany, i.tariffrate, i.tarifftype FROM user u INNER JOIN inventory i ON u.id = i.userid ORDER BY u.id"
        joinedrecords:list = self.getprocess(query)
        return joinedrecords

    def getall_tariffcompanystats(self,column,tariffcompany):
        query = f"select distinct email from inventory where {column}='{tariffcompany}'"
        tariffcompanystats:list = self.getprocess(query)
        return tariffcompanystats

    def getall_prevweeklygreendata(self, table: str, userid: int):
        query = f"""
            SELECT DISTINCT weeklygreendata 
            FROM {table} 
            WHERE userid = {userid} AND weeklygreendata IS NOT NULL
        """
        prevweeklydata = self.getprocess(query)
        return prevweeklydata


    def find_user(self,email:str, table:str):
        sql:str = f"SELECT * FROM {table} WHERE `email` = '{email}'"
        return self.getprocess(sql)
    
    def find_panel(self,panelname:str, table:str):
        sql:str = f"SELECT * FROM {table} WHERE `panelname` = '{panelname}'"
        return self.getprocess(sql)

    def find_simrecord(self,userid:int, table:str):
        sql:str = f"SELECT * FROM {table} WHERE `userid` = {userid}"
        return self.getprocess(sql)
    
    def add_user(self,table,**kwargs):
        keys:list = kwargs.keys()
        values:list=kwargs.values()
        columns:str = ",".join(keys)
        formatted_values = ",".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values])
        sql:str = f"INSERT INTO {table} ({columns}) VALUES({formatted_values})"
        return self.postprocess(sql)
    
    def update_user(self,table,**kwargs):
        keys:list = list(kwargs.keys())
        values:list = list(kwargs.values())
        flds:list = []
        # join both keys and values as an element in a list
        for i in range(1, len(keys)):
            flds.append(f"`{keys[i]}` = '{values[i]}'")
        #transform the list of string with "," as delimiter
        fld:str = ",".join(flds)
        #create sql statement
        sql:str = f"UPDATE `{table}` SET {fld} WHERE `{keys[0]}`= '{values[0]}'"
        return self.postprocess(sql)

    def delete_user(self, table, id):
        query = f"DELETE FROM `{table}` WHERE userid = {id}"
        return self.postprocess(query)    
    def delete_userid(self, table, id):
        query = f"DELETE FROM `{table}` WHERE id = {id}"
        return self.postprocess(query) 
    

