import mysql.connector as mariadb
class Databasehelper:
    def __init__(self)->None:
        self.host = 'localhost'
        self.user = 'root'
        self.password = ''
        self.database = 'energreen'

    def getdb_connection(self):
        connection = mariadb.connect(
            host= self.host,
            user= self.user,
            password= self.password,
            database= self.database
        )
        return connection
    
    def getprocess(self,sql:str):
        connection = self.getdb_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql)
        data:list = cursor.fetchall()
        cursor.close()
        connection.close()
        return data

    def postprocess(self,sql:str):
        connection = self.getdb_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close() 

    def getall_users(self, table:str)->list:
        query = f"SELECT * FROM {table}"
        users:list = self.getprocess(query)
        return users
    
    def find_user(self,email:str, table:str):
        sql:str = f"SELECT * FROM {table} WHERE `email` = '{email}'"
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
