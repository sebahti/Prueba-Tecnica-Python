import sqlite3
import pandas as pd
class Conexiones:
    def __init__(self) -> None:
        pass
    
    
    def connect_database(database):
            database = 'database'
            conexion = sqlite3.connect(f'database/{database}.sqlite')
            return conexion

    def import_tables(self, query):
            function = lambda table, conn: pd.read_sql(table, conn)
            tabla = function(query, self.connect_database())
            return pd.DataFrame(tabla)