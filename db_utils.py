# db_utils.py

from sqlalchemy import create_engine, text
import pandas as pd
import os
import sqlite3
from datetime import datetime, timedelta
import math

# Usar SQLite para Render (más simple)
DB_PATH = os.getenv("DATABASE_URL", "solar_data.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    """Inicializar la base de datos SQLite con datos de ejemplo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solar_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            slrw_avg REAL,
            slrw_2_avg REAL
        )
    ''')
    
    # Insertar datos de ejemplo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM solar_data")
    if cursor.fetchone()[0] == 0:
        # Generar datos de ejemplo para las últimas 30 horas
        base_time = datetime.now() - timedelta(hours=30)
        sample_data = []
        
        for i in range(180):  # 30 horas * 6 registros por hora
            timestamp = base_time + timedelta(minutes=10*i)
            # Simular irradiancia solar (mayor durante el día)
            hour = timestamp.hour
            if 6 <= hour <= 18:  # Día
                irradiance = 800 + 400 * abs(math.sin((hour - 6) * math.pi / 12)) + (i % 50)
            else:  # Noche
                irradiance = 50 + (i % 20)
            
            sample_data.append((timestamp, irradiance, irradiance * 0.95))
        
        cursor.executemany(
            "INSERT INTO solar_data (timestamp, slrw_avg, slrw_2_avg) VALUES (?, ?, ?)",
            sample_data
        )
        
        conn.commit()
        print(f"Base de datos inicializada con {len(sample_data)} registros de ejemplo")
    
    conn.close()

# Función para obtener datos entre dos fechas y columna
def get_solar_data(start_date=None, end_date=None, column="slrw_avg"):
    try:
        with engine.connect() as conn:
            if start_date and end_date:
                query = text(f'''
                    SELECT timestamp, {column}
                    FROM solar_data
                    WHERE timestamp BETWEEN :start AND :end
                    ORDER BY timestamp
                ''')
                df = pd.read_sql(query, conn, params={"start": start_date, "end": end_date})
            else:
                query = text(f'''
                    SELECT timestamp, {column}
                    FROM solar_data
                    ORDER BY timestamp
                ''')
                df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        # Retornar DataFrame vacío en caso de error
        return pd.DataFrame(columns=['timestamp', column])

# Inicializar la base de datos al importar el módulo
init_db()
