from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime
import numpy as np

# Configuración de conexión
engine = create_engine("postgresql://postgres:postgret@localhost/solar_database")

# Área del panel solar en m²
AREA_PANEL = 2
MINUTOS_INTERVALO = 10
HORAS_INTERVALO = MINUTOS_INTERVALO / 60

def tabla_irradiancia_existe():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'irradiancia_calculada'
            )
        """))
        return result.scalar()

def obtener_ultima_fecha():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(fecha) FROM irradiancia_calculada"))
        return result.scalar()

# Leer solo los datos nuevos o todos si la tabla no existe
tabla_existe = tabla_irradiancia_existe()
if tabla_existe:
    ultima_fecha = obtener_ultima_fecha()
    if ultima_fecha is not None:
        filtro_fecha = f"WHERE \"timestamp\" > '{ultima_fecha}'"
    else:
        filtro_fecha = ""
else:
    filtro_fecha = ""

with engine.connect() as conn:
    query = text(f"""
        SELECT "timestamp", "slrw_avg"
        FROM solar_data
        WHERE "slrw_avg" IS NOT NULL {f'AND {filtro_fecha[6:]}' if filtro_fecha else ''}
    """)
    df = pd.read_sql(query, conn)

if df.empty:
    print("No hay datos nuevos para procesar.")
    exit(0)

# Convertir a datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["fecha"] = df["timestamp"].dt.date

# Calcular Wh por muestra
df["wh_muestra"] = df["slrw_avg"] * AREA_PANEL * HORAS_INTERVALO

# Agrupar por día
diario = df.groupby("fecha")["wh_muestra"].sum().to_frame(name="irradiancia_wh")

diario["irradiancia_kwh"] = diario["irradiancia_wh"] / 1000
diario = diario.reset_index()
diario["fecha"] = pd.to_datetime(diario["fecha"])
diario["mes"] = diario["fecha"].dt.month
diario["año"] = diario["fecha"].dt.year

# Promedios mensuales y anuales
mensual = diario.groupby(["año", "mes"])["irradiancia_kwh"].mean().reset_index()
anual = diario.groupby(["año"])["irradiancia_kwh"].mean().reset_index()

# Mapear promedios al diario
diario = diario.merge(mensual, on=["año", "mes"], suffixes=("", "_prom_mensual"))
diario = diario.merge(anual, on="año", suffixes=("", "_prom_anual"))

# Crear tabla si no existe
def crear_tabla():
with engine.connect() as conn:
    conn.execute(text("""
            CREATE TABLE IF NOT EXISTS irradiancia_calculada (
            fecha DATE PRIMARY KEY,
            irradiancia_wh REAL,
            irradiancia_kwh REAL,
            promedio_mensual_kwh REAL,
            promedio_anual_kwh REAL
        );
    """))

crear_tabla()

# Insertar solo los días nuevos
with engine.connect() as conn:
    diario_nuevo = diario.copy()
    if tabla_existe and ultima_fecha is not None:
        diario_nuevo = diario_nuevo[diario_nuevo["fecha"] > ultima_fecha]
    if not diario_nuevo.empty:
        columnas = [
            "fecha",
            "irradiancia_wh",
            "irradiancia_kwh",
            "irradiancia_kwh_prom_mensual",
            "irradiancia_kwh_prom_anual"
        ]
        # Asegurarse de que las columnas existen en el DataFrame
        columnas_existentes = [col for col in columnas if col in diario_nuevo.columns]
        diario_nuevo.loc[:, columnas_existentes].to_sql(
        "irradiancia_calculada", engine, if_exists="append", index=False
    )
        print(f"Se agregaron {len(diario_nuevo)} días nuevos a irradiancia_calculada.")
    else:
        print("No hay días nuevos para agregar.")
