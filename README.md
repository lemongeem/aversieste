# 🌞 Sistema de Monitoreo Solar - Proyecto Hidrógeno

Sistema web completo para el análisis y cálculo energético de sistemas fotovoltaicos, desarrollado con Flask y Dash.

## 🚀 Características Principales

### 📊 Dashboard Interactivo
- **Visualización en tiempo real** de datos solares
- **Gráficos interactivos** con Plotly
- **Análisis de tendencias** históricas
- **Métricas dinámicas** con actualización automática

### 🧮 Calculadora de Eficiencia Solar
- **Cálculo de eficiencia** considerando temperatura
- **Conversiones de unidades** (W/m², kWh, etc.)
- **Ángulo óptimo** de instalación por estación
- **Estimación de producción** energética

### 🌤️ Simulación Climática
- **Análisis bajo diferentes condiciones** climáticas
- **Comparación de rendimiento** por escenario
- **Predicciones de producción** según clima

### 📈 Análisis Avanzado
- **Método del trapecio** para cálculo preciso de energía
- **Procesamiento incremental** de datos
- **Exportación a CSV** para análisis externo
- **Tendencias y predicciones** automáticas

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos principal
- **NumPy & Pandas** - Procesamiento de datos

### Frontend
- **Dash** - Framework de visualización
- **Plotly** - Gráficos interactivos
- **Bootstrap** - Diseño responsive
- **JavaScript** - Interactividad

## 📦 Instalación

### Prerrequisitos
- Python 3.8+
- PostgreSQL
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd sistema-solar
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
# Crear base de datos PostgreSQL
createdb solar_database

# Configurar credenciales en db_utils.py
# o usar variables de entorno:
export DATABASE_URL="postgresql://usuario:password@localhost/solar_database"
```

5. **Ejecutar el sistema**
```bash
python app.py
```

6. **Acceder al sistema**
- Página principal: http://localhost:5000
- Dashboard: http://localhost:5000/dashboard/
- Cálculos: http://localhost:5000/calculations

## 📁 Estructura del Proyecto

```
sistema-solar/
├── app.py                 # Aplicación principal (Flask + Dash)
├── db_utils.py           # Utilidades de base de datos
├── calculos_irradiacion.py # Cálculos incrementales
├── import_data.py        # Importación de datos
├── templates/            # Plantillas HTML
│   ├── base.html        # Plantilla base
│   ├── home.html        # Página de inicio
│   └── calculations.html # Página de cálculos
├── assets/              # Archivos estáticos
│   └── logo.png         # Logo del proyecto
├── requirements.txt     # Dependencias
└── README.md           # Documentación
```

## 🔧 Configuración

### Variables de Entorno
```bash
export DATABASE_URL="postgresql://usuario:password@localhost/solar_database"
export FLASK_ENV="development"
export FLASK_DEBUG="True"
```

### Configuración de Base de Datos
El sistema utiliza PostgreSQL con las siguientes tablas:
- `solar_data` - Datos de irradiancia solar
- `irradiancia_calculada` - Resultados de cálculos

## 📊 Uso del Sistema

### 1. Página de Inicio
- **Métricas en tiempo real** de irradiancia y energía
- **Información del proyecto** y tecnologías utilizadas
- **Enlaces rápidos** a funcionalidades principales

### 2. Dashboard Interactivo
- **Selección de fechas** para análisis específico
- **Gráficos de irradiancia** con marcadores interactivos
- **Análisis de tendencias** con predicciones
- **Cálculo de energía** por método del trapecio
- **Simulación climática** con comparaciones
- **Exportación de datos** a CSV

### 3. Calculadora de Eficiencia
- **Cálculo de eficiencia** considerando temperatura
- **Conversiones de unidades** automáticas
- **Ángulo óptimo** de instalación
- **Estimación de producción** energética

## 🔍 API Endpoints

### Cálculos de Eficiencia
```http
POST /api/solar-efficiency
Content-Type: application/json

{
    "irradiance": 1000,
    "temperature": 25,
    "panel_area": 2,
    "panel_efficiency": 0.15
}
```

### Simulación Climática
```http
POST /api/climate-simulation
Content-Type: application/json

{
    "type": "clear"  // clear, cloudy, rainy, optimal
}
```

### Análisis de Tendencias
```http
GET /api/trends-analysis
```

## 📈 Características Técnicas

### Optimizaciones Implementadas
- ✅ **Procesamiento incremental** de datos
- ✅ **Índices SQL** para consultas rápidas
- ✅ **Caché de conexiones** a base de datos
- ✅ **Cálculos en tiempo real** con Dash
- ✅ **Exportación eficiente** de datos

### Ventajas sobre Sistemas Comerciales
- 🚀 **Interfaz interactiva** vs. exportaciones estáticas
- 📊 **Visualización avanzada** con gráficos dinámicos
- 🧮 **Cálculos automáticos** de eficiencia
- 🌤️ **Simulación climática** integrada
- 📈 **Análisis de tendencias** predictivo

## 🧪 Testing

```bash
# Ejecutar tests básicos
python -m pytest tests/

# Verificar integridad de datos
python tests/test_integridad_datos.py
```

## 📝 Contribución

1. Fork el proyecto
2. Crear rama para nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Desarrollador Principal** - [Tu Nombre]
- **Proyecto** - Sistema Solar para Producción de Hidrógeno

## 🙏 Agradecimientos

- Datos proporcionados por LoggerNet
- Comunidad de desarrollo de Flask y Dash
- Contribuidores del proyecto

## 📞 Soporte

Para soporte técnico o preguntas:
- 📧 Email: [tu-email@ejemplo.com]
- 📱 WhatsApp: [tu-número]
- 🌐 Sitio web: [tu-sitio-web]

---

**¡Disfruta analizando la energía solar de manera eficiente y profesional!** 🌞⚡




