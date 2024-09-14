import pandas as pd
from conexiones import Conexiones

#Se instancian las clases a utilizar
conexiones = Conexiones()


#Se realiza la conexión con la base de datos almacenada
conn = conexiones.connect_database()

#Se extraen las tablas a utilizar las cuales se almancenan en un dataframe
apicall_DF = conexiones.import_tables("SELECT * from apicall")
commerce_DF = conexiones.import_tables("SELECT * from commerce")

print(".")