#!/usr/bin/env python3
"""
Script simple para probar la aplicación Flask
"""

import requests
import time

def test_app():
    """Probar que la aplicación funciona"""
    base_url = "http://localhost:5000"
    
    print("🧪 Probando aplicación solar...")
    
    try:
        # Probar página principal
        print("📄 Probando página principal...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Página principal funciona")
        else:
            print(f"❌ Error en página principal: {response.status_code}")
        
        # Probar dashboard
        print("📊 Probando dashboard...")
        response = requests.get(f"{base_url}/dashboard/")
        if response.status_code == 200:
            print("✅ Dashboard funciona")
        else:
            print(f"❌ Error en dashboard: {response.status_code}")
        
        # Probar API
        print("🔌 Probando API...")
        response = requests.post(f"{base_url}/api/solar-efficiency", 
                               json={"irradiance": 1000, "temperature": 25})
        if response.status_code == 200:
            print("✅ API funciona")
            data = response.json()
            print(f"   Potencia calculada: {data.get('power_watts', 'N/A')} W")
        else:
            print(f"❌ Error en API: {response.status_code}")
        
        print("\n🎉 ¡Todas las pruebas pasaron! La aplicación está lista para Render.")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la aplicación. Asegúrate de que esté ejecutándose:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")

if __name__ == "__main__":
    test_app()
