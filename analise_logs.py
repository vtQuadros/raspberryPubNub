import sqlite3
import pandas as pd


DB_PATH = '/home/pi/Documents/rasp/teste/logs.db'

def fetch_logs():
    """Obtém os logs do banco de dados."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp ASC", conn)
    return df

def analyze_logs(df):
    """Analisa os logs para calcular acessos por dia e tempo de permanência."""
    
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
   
    acessos_por_dia = df.groupby(df['timestamp'].dt.date)['user'].count()
    
   
    df_acessos = df[df['action'] == 'Access Granted'].copy()
    
    
    df_acessos['entrada'] = df_acessos['timestamp']
    df_acessos['saida'] = df_acessos['entrada'].shift(-1)  
    
    
    df_acessos['saida'] = df_acessos.apply(lambda row: row['saida'] if row['user'] == row['user'] else None, axis=1)
    
    
    df_acessos['tempo_permanencia'] = df_acessos['saida'] - df_acessos['entrada']
    
    
    tempo_por_usuario = df_acessos.groupby('user')['tempo_permanencia'].sum()
    
    return acessos_por_dia, tempo_por_usuario

if __name__ == "__main__":
    df_logs = fetch_logs()
    if df_logs.empty:
        print("Nenhum log encontrado.")
    else:
        acessos_por_dia, tempo_por_usuario = analyze_logs(df_logs)
        print("Acessos por dia:")
        print(acessos_por_dia)
        print("\nTempo total dentro da sala por usuário:")
        print(tempo_por_usuario)
