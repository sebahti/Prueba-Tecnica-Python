import os
import pandas as pd
from datetime import datetime
import dateutil
from tqdm import tqdm
import win32com.client as win32

class Procesos:
    
    def __init__(self) -> None:
        pass
    
    def dates(self):
        """
        Función para generar el periodo actual, anterior y mes antepasado
        
        Args:
        No recibe
        
        Return:
        
        Dataframe: con las fechas.
        
        """
        #Se extrae la fecha actual con la libreria date y se divide en dia, mes y año
        date =  datetime.now()
        dia = date.strftime('%d')
        anno = date.strftime('%Y')
        mes = date.strftime('%m')
        periodo_actual = date
        
        #Se aplica un lambda para generar los meses anteriores
        generate_months = lambda month: date - dateutil.relativedelta.relativedelta(months=month)
        mes_anterior = generate_months(1)
        mes_antepasado = generate_months(2)
        
        #Se definen los valores para crear el DataFrame con las fechas
        periodos = ["periodo_actual", "periodo_anterior", "periodo_antepasado"]
        valor = [periodo_actual, mes_anterior, mes_antepasado] 
        
        #Se crea el Dataframe y se le pasan los valores definids
        fechas = pd.DataFrame({'periodos': periodos,'valor': valor})
        #Se da formato de tipo Fecha para los valores y se convierte en AñoMes
        fechas['valor'] = pd.to_datetime(fechas['valor'])
        fechas['valor'] = fechas['valor'].dt.strftime("%Y%m")
        
        return fechas
    
    def read_iva(self):
        """
        Función que realiza la consulta de los porcentaje de iva que tiene cada país en tiempo real dependiendo de la necesidad, se usará por defecto el 19% en dado caso de presentarse un error.

        Parametros: 
        No requiere parametros

        Retorna:
        float: Porcentaje del IVA

        """
        pais_a_consultar = None
        try:
            #Se realiza la lectura de la página Wikipedia para obtener la lista de los paises y su % de IVA
            iva_paises_df = pd.read_html('https://es.wikipedia.org/wiki/Impuesto_al_valor_agregado#Tipo_de_gravamen')
            
            print("\n ¿Desea seguir la operación con un país diferente a Colombia? 1: Si 2: No")
            try:
                #Se crea la entrada de texto para capturar la opción anterior
                elegir_pais = int(input('\nIngrese la opción: '))
                
                #Se condiciona ambas opciones para realizar la consulta con un pais diferente o con Colombia por defecto
                if elegir_pais == 1:
                    nuevo_pais = input(str("\nIngrese el nuevo país para la consulta: "))
                    pais_a_consultar = nuevo_pais.capitalize()
                elif elegir_pais == 2:
                    pais_a_consultar = "Colombia"  
                    #print(f"\nSe hará la consulta con {pais_a_consultar} por defecto ")    
                
                else:
                    print("\nSe ingresó una opción inválida, intentelo nuevamente")
                    quit()
            except ValueError:
                print("Error: No se puede ingresar texto")
                quit()
            
            #Se selecciona el primer indice de la tabla para obtener el listado de los paises 
            iva_paises_df = pd.DataFrame(iva_paises_df[0])
            
            #Se convierte la columna "País" en Texto - string.
            iva_paises_df['País'] = iva_paises_df['País'].astype(str)
            
            #Se realiza el filtro de los datos de las columnas para eliminar el sobrante y obtener los % de iva.
            iva_paises_df['País'] = iva_paises_df['País'].str.split('[').str[0]
            iva_paises_df['Tasa normal'] = iva_paises_df['Tasa normal'].astype(str)
            iva_paises_df['Tasa normal'] = iva_paises_df['Tasa normal'].str.replace("%", "")
            iva_paises_df['Tasa normal'] = iva_paises_df['Tasa normal'].str.replace(",", ".")
            iva_paises_df['Tasa normal'] = iva_paises_df['Tasa normal'].str.split('[').str[0]
            iva_paises_df['Tasa normal'] = iva_paises_df['Tasa normal'].str.split('(').str[0]
            
            #Se extrae el valor del IVA del país seleccionado.
            extraer_pais = iva_paises_df[(iva_paises_df['País'] == pais_a_consultar)]
            
            #Se condiciona la consulta al momento de extraer el País, en dado caso de no encontrar coincidencias genera un archivo con el listado de los Paises.
            if len(extraer_pais) == 0:
                print("\nEl país ingresado es incorrecto o no está disponible,\nse generó un listado con los paises en la carpeta 'Recursos' \n")
                
                #Si la carpeta no existe, la crea, de lo contrario solo agrega el archivo generado.
                if not os.path.exists("Recursos"):
                    os.mkdir("Recursos")
                if not os.path.exists("Recursos/Paises"):
                    os.mkdir("Recursos/Paises")
                #Realiza la generación del archivo con el listado de los Paises
                iva_paises_df['País'].to_excel('Recursos/paises/lista_paises.xlsx', index=False)
                quit()
                
            else:
                #Extrae el porcentaje de IVA tomando la primer fila y la tercer columna.
                porcentaje_iva = extraer_pais.iloc[0,2]
                
                #Convierte el entero en un float.
                porcentaje_iva = float(porcentaje_iva) / 100
                print(f"El IVA de {pais_a_consultar} es: {porcentaje_iva}%\n")
                return porcentaje_iva

                
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            porcentaje_iva = 19 / 100
            print(f"\nEl porcentaje de IVA se estableció en {porcentaje_iva}%")
            return porcentaje_iva
    
    
    def generar_cuenta_peticiones(self, DF, Fechas):
        """
        Función que se encarga de filtrar y sacar la sumatoria de las peticiones Exitosas y Fallidas totales del mes
        
        Args:
        DF: Dataframe con la unión de ambas tablas commerce y api_call
        Fechas: Dataframe con los periodos actual, anterior y antepasado
        
        Retorna: 
        total_pet_exitosas: Dataframe con la cantidad total de peticiones exitosas por comercio en mes anterior y antepasado (202407 y 20208)
        
        total_pet_fallidas: Dataframe con la cantidad total de peticiones fallidas por comercio en mes anterior y antepasado (202407 y 20208)
        """

        #Se da formato de Dataframe a los Arg 
        Fechas = pd.DataFrame(Fechas)
        
        count_exitosa = []
        count_fallida = []
        
        
        count_pet_fallida_DF = pd.DataFrame()
        table = pd.DataFrame(DF)
        
        #Se instancia un Dataframe nuevo
        total_peticiones = pd.DataFrame()
        
        #Se extraen los dos meses anteriores partiendo del mes actual
        mes_anterior = Fechas.loc[Fechas['periodos'] == 'periodo_anterior', 'valor'].values[0]
        mes_antepasado=  Fechas.loc[Fechas['periodos'] == 'periodo_antepasado', 'valor'].values[0]
        
        #Se realiza el filtro de los comercios por las fechas y el status "Activo"
        total_peticiones = table[(table['fecha_formateada'] >= f'{mes_antepasado}')& (table['fecha_formateada'] <= f'{mes_anterior}')   & (table['commerce_status'] == "Active" )][['fecha_formateada', 'commerce_id', 'ask_status', 'commerce_nit', 'commerce_name', 'commerce_email']]

        print("Filtrando peticiones exitosas y no exitosas\n")
        for i, row in tqdm(total_peticiones.iterrows(), total=len(total_peticiones)):
            #Se condiciona que el status es 1 es exitosa, se guarda en una lista
            if row['ask_status'] == 1:
                
                filas_exitosas = {
                    'commerce_id': row['commerce_id'],
                    'date': row['fecha_formateada'],
                    'ask_status': row['ask_status'],
                    'commerce_nit': row['commerce_nit'],
                    'commerce_name': row['commerce_name'],
                    'commerce_email': row['commerce_email'],
                    
                }
                count_exitosa.append(filas_exitosas)
             #Se condiciona que el status es 0 es fallida, se guarda en una lista   
             
            elif row['ask_status'] == 0:
                filas_fallidas = {
                    'commerce_id': row['commerce_id'],
                    'date': row['fecha_formateada'],
                    'ask_status': row['ask_status'],
                    'commerce_nit': row['commerce_nit'],
                    'commerce_name': row['commerce_name'],
                    'commerce_email': row['commerce_email'],
                    
                }
                count_fallida.append(filas_fallidas)
        #Se crea un dataframe con la cantidad de peticiones exitosas        
        count_pet_exitosa_DF = pd.DataFrame(count_exitosa)
        #Se crea un dataframe con la cantidad de peticiones fallidas 
        count_pet_fallida_DF = pd.DataFrame(count_fallida)
        #Se resetea los indices del dataframe y se renombra la columna Date
        count_pet_exitosa_DF.reset_index(drop=True, inplace=True)
        count_pet_exitosa_DF.rename(columns={'date': 'date_temp'}, inplace=True)
        
        #Se agrupa el dataframe de peticiones exitosas por el id del comercio y la fecha
        total_pet_exitosas = count_pet_exitosa_DF.groupby(['commerce_id', 'date_temp']).agg(
            ask_status_success=('ask_status', 'count'),
            commerce_id=('commerce_id', 'first'),
            date=('date_temp', 'first'),
            commerce_name=('commerce_name', 'first'),
            commerce_nit=('commerce_nit', 'first'),
            commerce_email=('commerce_email', 'first'),
        )
        #Se reseta el indice nuevamente
        total_pet_exitosas.reset_index(drop=True, inplace=True)
        
         #Se agrupa el dataframe de peticiones  fallidas por el id del comercio y la fecha
        total_pet_fallidas = count_pet_fallida_DF.groupby(['commerce_id', 'date']).agg(
            ask_status_unsuccess=('ask_status', 'count'),
            date=('date', 'first'),
            commerce_name=('commerce_name', 'first'),
            commerce_nit=('commerce_nit', 'first'),
            commerce_email=('commerce_email', 'first'),
        )
        
       
        

        return total_pet_exitosas, total_pet_fallidas     
    
        
        
    def calculate_total(self, Data, Dates, iva):
        valores_exitosas_anterior_list = []
        valores_exitosas_antepasado_list = []
        iva = iva
        comision = 0
        Fechas = pd.DataFrame(Dates)
        
        #Se extraen los dos meses anteriores partiendo del mes actual
        mes_anterior = Fechas.loc[Fechas['periodos'] == 'periodo_anterior', 'valor'].values[0]
        mes_antepasado=  Fechas.loc[Fechas['periodos'] == 'periodo_antepasado', 'valor'].values[0]
        
        #Se realiza la lectura de los contratos desde el archivo en la ruta principal
        contratos = pd.read_excel('comisiones.xlsx')
        #Se convierte a un dataframe
        contratos_DF = pd.DataFrame(contratos)
        
        #Se filtra el dataframe con las peticiones para el mes anterior
        mes_anterior_DF = Data[(Data['date'] == f"{mes_anterior}")][['commerce_id', 'date', 'commerce_name', 'commerce_nit', 'commerce_email', 'ask_status_success']]
        mes_anterior_DF_2 = pd.merge(mes_anterior_DF, contratos_DF, on="commerce_id")
        mes_anterior_DF_2[['min_asks_1', 'max_asks_1', 'min_asks_2', 'max_asks_2',  'min_asks_3', 'max_asks_3', ]] =  mes_anterior_DF_2[['min_asks_1', 'max_asks_1', 'min_asks_2', 'max_asks_2',  'min_asks_3', 'max_asks_3' ]].astype(int)
        
        #Se filtra el dataframe con las peticiones para el mes antepasado
        mes_antepasado_DF = Data[(Data['date'] == f"{mes_antepasado}")][['commerce_id', 'date', 'commerce_name', 'commerce_nit', 'commerce_email', 'ask_status_success']]
        mes_antepasado_DF_2 = pd.merge(mes_antepasado_DF, contratos_DF, on="commerce_id")
        mes_antepasado_DF_2[['min_asks_1', 'max_asks_1', 'min_asks_2', 'max_asks_2',  'min_asks_3', 'max_asks_3', ]] =  mes_antepasado_DF_2[['min_asks_1', 'max_asks_1', 'min_asks_2', 'max_asks_2',  'min_asks_3', 'max_asks_3' ]].astype(int)
        
       
        
        #Se itera sobre las peticiones exitosas para el mes anterior
        print(f"Consolidando tabla total para {mes_anterior}")
        for i, row in tqdm(mes_anterior_DF_2.iterrows(), total=len(mes_anterior_DF)):
            
            if row['ask_status_success'] in range(row['min_asks_1'], row['max_asks_1']):
                comision = row['comision_1']
                
            elif row['ask_status_success'] in range(row['min_asks_2'], row['max_asks_2']):
                
                if row['min_asks_2']  == 0 and  row['max_asks_2'] == 0:
                 comision = row['comision_1']
                else:
                 comision = row['comision_2']
                 
            elif row['ask_status_success'] in range(row['min_asks_3'], row['max_asks_3']):
                if row['min_asks_3']  == 0 and  row['max_asks_3'] == 0:
                 comision = row['comision_1']
                else:
                 comision = row['comision_3']
                 
            total_con_comision = row['ask_status_success'] * comision
            total_iva = total_con_comision * iva
            total_con_iva = total_con_comision + total_iva
            
            tabla_pago = {
                            "Fecha-Mes": row['date'],
                            "Nombre": row['commerce_name_x'],
                            "Nit": row['commerce_nit'],
                            "Valor_comision": comision,
                            #"Valor_con_comision": total_con_comision,
                            "Valor_iva": total_iva,
                            "Valor_total": total_con_iva,
                            "Correo": row['commerce_email']
                        }
            valores_exitosas_anterior_list.append(tabla_pago) 
        tabla_final_mes_anterior = pd.DataFrame(valores_exitosas_anterior_list)

        
        
        #Se itera sobre las peticiones exitosas para el mes antepasado
        print(f"Consolidando tabla total para {mes_antepasado}")
        for i, row in tqdm(mes_antepasado_DF_2.iterrows(), total=len(mes_antepasado_DF_2)):
            
            if row['ask_status_success'] in range(row['min_asks_1'], row['max_asks_1']):
                comision = row['comision_1']
                
            elif row['ask_status_success'] in range(row['min_asks_2'], row['max_asks_2']):
                
                if row['min_asks_2']  == 0 and  row['max_asks_2'] == 0:
                 comision = row['comision_1']
                else:
                 comision = row['comision_2']
                 
            elif row['ask_status_success'] in range(row['min_asks_3'], row['max_asks_3']):
                if row['min_asks_3']  == 0 and  row['max_asks_3'] == 0:
                 comision = row['comision_1']
                else:
                 comision = row['comision_3']
                 
            total_con_comision = row['ask_status_success'] * comision
            total_iva = total_con_comision * iva
            total_con_iva = total_con_comision + total_iva
            
            tabla_pago = {
                            "Fecha-Mes": row['date'],
                            "Nombre": row['commerce_name_x'],
                            "Nit": row['commerce_nit'],
                            "Valor_comision": comision,
                            #"Valor_con_comision": total_con_comision,
                            "Valor_iva": total_iva,
                            "Valor_total": total_con_iva,
                            "Correo": row['commerce_email']
                        }
            valores_exitosas_antepasado_list.append(tabla_pago)
        
        tabla_final_mes_antepasado = pd.DataFrame(valores_exitosas_antepasado_list)
        
        if not os.path.exists("Recursos"):
            os.mkdir("Recursos")
            if not os.path.exists("Recursos/Facturas"):
               os.mkdir("Recursos/Facturas")
                #Realiza la generación del archivo con el listado de los Paises
        print("Exportando las facturas en Recursos/Facturas")
        
        tabla_final_mes_anterior.to_excel(f'Recursos/Facturas/factura{mes_anterior}.xlsx', index=False)
        tabla_final_mes_antepasado.to_excel(f'Recursos/Facturas/factura{mes_antepasado}.xlsx', index=False)
        
        
        return  tabla_final_mes_anterior , tabla_final_mes_antepasado
        
        
    def enviar_correos (self, factura, factura2):
     factura = pd.DataFrame(factura)
     factura2 = pd.DataFrame(factura2)
     Outlook = win32.Dispatch("Outlook.Application")
     # Se convierten los Dataframe a HTML
     factura_html = factura.to_html(index=False)  
     factura2_html = factura2.to_html(index=False)
     mail = Outlook.CreateItem(0)
        
     for i, row in factura2.iterrows():
        mail.To = f"{row['Correo']}"
        mail.Subject = "Factura"
        mail.HTMLBody = f"""
    <html>
    <body>
        <p>Estimado,</p>
        <p>A continuación, se adjuntan las facturas correspondientes a los dos meses anteriores :</p>
        
        <p><b>Factura 1:</b></p>
        {factura_html}
        
        <p><b>Factura 2:</b></p>
        {factura2_html}
        
        <p>Saludos,</p>
    </body>
    </html>
    """
     mail.Send()
     print("CORREO ENVIADO.")
        
        
        
    print(".")
      
  

 

