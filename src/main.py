import pandas as pd
from conexiones import Conexiones
from procesos import Procesos
from datos_empresas import Datos_Empresas

#Se instancian las clases a utilizar
conexiones = Conexiones()
procesos = Procesos()
datos = Datos_Empresas()

#Se realiza la conexión con la base de datos almacenada
conn = conexiones.connect_database()

periodos = procesos.dates()


#Se extraen las tablas a utilizar las cuales se almancenan en un dataframe
apicall_DF = conexiones.import_tables("SELECT * from apicall")
commerce_DF = conexiones.import_tables("SELECT * from commerce")

#Se extrae el porcentaje de IVA del país a utilizar
iva = procesos.read_iva()

print("\n GENERANDO ESTRUCTURA DE LOS DATOS EMPRESARIALES \n ")
#Se envian las tablas para procesarlas
empresas = datos.estructura_datos(apicall_DF, commerce_DF)

#Se envia el resultado de la estructuración de datos para obtener la cuenta de  las peticiones
success_pet, unsuccess_pet = procesos.generar_cuenta_peticiones(empresas, periodos)

factura, factura2 = procesos.calculate_total(success_pet, periodos, iva)

enviar_correo = procesos.enviar_correos(factura,factura2)
quit()