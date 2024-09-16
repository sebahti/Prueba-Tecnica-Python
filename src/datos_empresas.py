import pandas as pd
from tqdm import tqdm
class Datos_Empresas:
    def __init__(self) -> None:
        pass
    
    def estructura_datos(self, DF1, DF2):
        """
        Función que se encarga de leer las dos tablas y realizar el merge basado en el ID del comercio
        Args: 
        DF1: Tabla o Dataframe de ApiCall
        DF2: Tabla o Dataframe de Commerce
        
        Retorna:
        Dataframe con la unión de ambas tablas
        
        """
        api_call_df = pd.DataFrame(DF1)
        commerce = pd.DataFrame(DF2)
        
        #Se realiza la conversión del campo "Date_Api_Call" para asegurar de que sea de tipo fecha
        api_call_df['date_api_call'] = pd.to_datetime(api_call_df['date_api_call'])
        api_call_df['fecha_formateada'] = api_call_df['date_api_call'].dt.strftime('%Y%m')
        pd.set_option('future.no_silent_downcasting', True)
        api_call_df['ask_status'] = api_call_df['ask_status'].replace('Successful', 1)
        api_call_df['ask_status'] = api_call_df['ask_status'].replace('Unsuccessful', 0)
        
        #Se realiza el cruce de ambos Dataframe basandose en el id del comercio y se filtran los vacios para asignarles el valor 0
        merged_dfs = pd.merge(api_call_df, commerce, on="commerce_id").fillna(0)
        
        return pd.DataFrame(merged_dfs)
    
    
    
       
    