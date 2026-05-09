# Sales Dashboard Backend

Backend API desarrollado con FastAPI para el dashboard de ventas PALVI.

## 📋 Requisitos previos

- **Python 3.12+** instalado en tu sistema
- **pip** (incluido con Python)
- Una **API Key de Google Generative AI** (para generar insights con IA)

## 🚀 Instalación y ejecución

### 1. Crear y activar el entorno virtual

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual

# En Linux/macOS:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del backend con el siguiente contenido:

```env
# API de Google Generative AI
API_KEY=tu_api_key_aqui
MODEL=gemini-2.5-flash

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

**Notas importantes:**
- Reemplaza `tu_api_key_aqui` con tu API Key de Google Generative AI
- `MODEL` por defecto es `gemini-2.5-flash`, puedes cambiar a otro modelo disponible
- `ALLOWED_ORIGINS` lista los orígenes desde los que se pueden hacer requests (separados por comas)

### 4. Ejecutar el servidor

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: **http://localhost:8000**

Puedes acceder a la documentación interactiva en: **http://localhost:8000/docs**

## 📡 Endpoints disponibles

### Datos y Datasets

- `GET /api/datasets` — Obtiene lista de datasets disponibles (A, B, C, D)
- `GET /api/data/{dataset}?days=30` — Obtiene datos del dataset especificado

### KPIs de Ventas

- `GET /api/kpis/{dataset}/{fecha}` — KPIs de ventas (deals won, win rate, etc.)
- `GET /api/deal-trend/{dataset}/{day}?days=30` — Tendencia de deals en los últimos N días

### KPIs de Soporte

- `GET /api/support-kpis/{dataset}/{fecha}` — KPIs de customer support
- `GET /api/support-trend/{dataset}/{day}?days=30` — Tendencia de métricas de soporte

### Métricas del Funnel

- `GET /api/funnel/{dataset}/{fecha}` — Métricas del funnel de ventas

### Insights con IA

- `GET /api/insights-advanced/{dataset}/{fecha}` — Análisis con IA generando insights positivos y negativos

**Parámetros comunes:**
- `{dataset}`: A, B, C o D
- `{fecha}`: Formato YYYY-MM-DD (ej: 2025-05-09)
- `{day}`: Fecha de referencia en formato YYYY-MM-DD

## 🔧 Estructura del proyecto

```
backend/
├── main.py              # Punto de entrada, rutas FastAPI
├── data_loader.py       # Carga y procesamiento de datos
├── requirements.txt     # Dependencias de Python
├── .env                 # Variables de entorno (no incluir en git)
├── .venv/               # Entorno virtual
└── README.md            # Este archivo
```

## 📚 Dependencias principales

- **FastAPI** — Framework web moderno y rápido
- **Uvicorn** — Servidor ASGI para ejecutar FastAPI
- **Pydantic** — Validación de datos y esquemas
- **python-dotenv** — Cargar variables de entorno desde .env
- **LangChain Google GenAI** — Integración con Google Generative AI
- **CORS Middleware** — Soporte para requests desde diferentes orígenes

## 🐛 Solución de problemas

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solución:** Asegúrate de que el entorno virtual está activado y las dependencias instaladas:
```bash
pip install -r requirements.txt
```

### Error: "API_KEY no configurada"

**Solución:** Verifica que el archivo `.env` exista en el directorio del backend y contenga `API_KEY`:
```bash
cat .env  # Linux/macOS
type .env # Windows
```

### Error: "Port 8000 already in use"

**Solución:** Usa otro puerto:
```bash
uvicorn main:app --reload --port 8001
```

### Error de CORS

**Solución:** Actualiza `ALLOWED_ORIGINS` en `.env` con la URL correcta del frontend.

## 📝 Notas de desarrollo

- El servidor se reinicia automáticamente con `--reload` cuando cambias código
- La documentación interactiva (Swagger UI) está disponible en `/docs`
- Los logs se muestran en la consola para debugging
- Los datos se cargan desde JSON al iniciar la aplicación

## 🤝 Contribuir

Si necesitas agregar nuevos endpoints o modificar la lógica:

1. Edita `main.py` para nuevas rutas
2. Edita `data_loader.py` para lógica de datos
3. Agrega nuevos modelos Pydantic si necesitas nuevas respuestas
4. Prueba con la documentación interactiva en `/docs`

---

**Última actualización:** Mayo 2025
