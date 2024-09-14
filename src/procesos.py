import os
import pandas as pd

class Procesos:
    
    def __init__(self) -> None:
        pass
    
    
    def read_iva(self):
        """
        Función que realiza la consulta de los porcentaje de iva que tiene cada país en tiempo real dependiendo de la necesidad, se usará por defecto el 19% en dado caso de presentarse un error.

        Parametros: No requiere parametros

        Retorna:
        float: Porcentaje del IVA

        """
        pais_a_consultar = None
        try:
            #Se realiza la lectura de la página Wikipedia para obtener la lista de los paises y su % de IVA
            iva_paises_df = pd.read_html('https://es.wikipedia.org/wiki/Impuesto_al_valor_agregado#Tipo_de_gravamen')
            
            print("\n¿Desea seguir la operación con un país diferente a Colombia? 1: Si 2: No")
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
                return
            
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
                #Realiza la generación del archivo con el listado de los Paises
                iva_paises_df['País'].to_excel('Recursos/lista_paises.xlsx', index=False)
                
            else:
                #Extrae el porcentaje de IVA tomando la primer fila y la tercer columna.
                porcentaje_iva = extraer_pais.iloc[0,2]
                
                #Convierte el entero en un float.
                porcentaje_iva = float(porcentaje_iva) / 100
                print(f"\n El porcentaje IVA de {pais_a_consultar} es: {porcentaje_iva}%")
                return porcentaje_iva

                
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            porcentaje_iva = 19 / 100
            print(f"\nEl porcentaje de IVA se estableció en {porcentaje_iva}%")
            return porcentaje_iva