import pandas as pd
from sqlalchemy import create_engine

# Configura tu conexión PostgreSQL
engine = create_engine('postgresql+psycopg2://postgres:postgret@localhost:5432/solar_database')
# Ruta a tu archivo .dat
df = pd.read_csv("C:/Users/gabri/Documents/Proyecto tirulacion/datos/CR1000_Table1.dat", sep=',', quotechar='"', skiprows=[0, 2, 3])
# Renombrar columnas si es necesario
df.rename(columns={"TIMESTAMP": "timestamp", "SlrW_Avg": "slrw_avg", "SlrW_2_Avg": "slrw_2_avg"}, inplace=True)

# Convertir columna de tiempo a datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Seleccionar solo las columnas necesarias
df_filtrado = df[["timestamp", "slrw_avg", "slrw_2_avg"]]

# Insertar en PostgreSQL sin reemplazar
df_filtrado.to_sql("solar_data", engine, if_exists="append", index=False)

print("✅ Datos insertados correctamente.")
