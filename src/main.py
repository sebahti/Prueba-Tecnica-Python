import pandas as pd
from conexiones import Conexiones
from procesos import Procesos

#Se instancian las clases a utilizar
conexiones = Conexiones()
procesos = Procesos()

#Se realiza la conexión con la base de datos almacenada
conn = conexiones.connect_database()

#Se extraen las tablas a utilizar las cuales se almancenan en un dataframe
apicall_DF = conexiones.import_tables("SELECT * from apicall")
commerce_DF = conexiones.import_tables("SELECT * from commerce")


#Se extrae el porcentaje de IVA del país a utilizar
iva = procesos.read_iva()

print(".")