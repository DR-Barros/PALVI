from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import os
from dotenv import load_dotenv
from data_loader import get_data_loader
import logging
import json
from langchain_google_genai import ChatGoogleGenerativeAI

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Sales Dashboard API",
    description="Backend API para dashboard de ventas",
    version="1.0.0"
)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar datos
try:
    data_loader = get_data_loader()
    logger.info(f"✓ Datos cargados exitosamente. Datasets: {data_loader.get_datasets()}")
except Exception as e:
    logger.error(f"✗ Error al cargar datos: {str(e)}")
    data_loader = None

# ==================== Modelos Pydantic ====================

class DatasetInfo(BaseModel):
    name: str
    metadata: Dict[str, Any]

class DayMetrics(BaseModel):
    date: str
    metrics: Dict[str, float]

class DatasetResponse(BaseModel):
    metadata: Dict[str, Any]
    latest_days: List[DayMetrics]
    summary: Dict[str, Any]

class InsightResponse(BaseModel):
    dataset: str
    insights: str
    key_metrics: Dict[str, Any]

class Insight(BaseModel):
    categoria: str
    metrica: str
    descripcion: str
    tipo: str  # "positivo" o "negativo"
    impacto: str

class AdvancedInsightResponse(BaseModel):
    positivos: List[Insight]
    negativos: List[Insight]

class KPIValue(BaseModel):
    current: float
    previous: float
    change: float
    change_pct: float
    period_compared: str

class KPIsResponse(BaseModel):
    date: str
    deals_won: KPIValue
    win_rate: KPIValue
    deal_velocity: KPIValue
    pipeline_risk: KPIValue

class SupportKPIsResponse(BaseModel):
    date: str
    response_time: KPIValue
    resolution_time: KPIValue
    ticket_volume: KPIValue
    support_load: KPIValue

class FunnelStage(BaseModel):
    key: str
    label: str
    value: float
    previous: float
    change: float
    change_pct: float
    conversion_rate: Optional[float] = None
    previous_conversion_rate: Optional[float] = None
    conversion_change: Optional[float] = None
    conversion_change_pct: Optional[float] = None
    transition: Optional[str] = None

class FunnelInsightItem(BaseModel):
    key: str
    label: str
    conversion_rate: float
    previous_conversion_rate: Optional[float] = None
    conversion_change: Optional[float] = None
    dropoff_pct: Optional[float] = None

class FunnelInsights(BaseModel):
    best_stage: FunnelInsightItem
    weakest_stage: FunnelInsightItem
    bottleneck: FunnelInsightItem

class FunnelResponse(BaseModel):
    date: str
    stages: List[FunnelStage]
    insights: FunnelInsights

# ==================== Rutas ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sales Dashboard Backend API",
        "docs": "/docs",
        "datasets_available": data_loader.get_datasets() if data_loader else []
    }

@app.get("/api/datasets", response_model=List[str])
async def get_datasets():
    """Obtiene lista de datasets disponibles (A, B, C, D)"""
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    try:
        return data_loader.get_datasets()
    except Exception as e:
        logger.error(f"Error en get_datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/{dataset}", response_model=DatasetResponse)
async def get_dataset_data(dataset: str, days: int = 30):
    """
    Obtiene datos del dataset especificado
    
    - **dataset**: A, B, C, o D
    - **days**: Número de últimos días a retornar (default: 30)
    """
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    try:
        metadata = data_loader.get_dataset_metadata(dataset)
        latest_days = data_loader.get_dataset_latest_days(dataset, days)
        summary = data_loader.get_dataset_summary_stats(dataset, days)
        
        return DatasetResponse(
            metadata=metadata,
            latest_days=latest_days,
            summary=summary
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_dataset_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/kpis/{dataset}/{fecha}", response_model=KPIsResponse)
async def get_kpis(dataset: str, fecha: str):
    """
    Obtiene KPIs de ventas para una fecha específica
    
    - **dataset**: A, B, C, o D
    - **fecha**: Fecha en formato YYYY-MM-DD
    
    KPIs incluidos:
    - Deals Won: comparado con ayer (D-1)
    - Win Rate: comparado con hace 7 días (D-7)
    - Deal Velocity: comparado con hace 7 días (D-7)
    - Pipeline Risk: comparado con hace 30 días (D-30)
    """
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    try:
        kpis = data_loader.calculate_kpis(dataset, fecha)
        return KPIsResponse(**kpis)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_kpis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/support-kpis/{dataset}/{fecha}", response_model=SupportKPIsResponse)
async def get_support_kpis(dataset: str, fecha: str):
    """
    Obtiene KPIs de Customer Support para una fecha específica

    - **dataset**: A, B, C, o D
    - **fecha**: Fecha en formato YYYY-MM-DD
    """
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")

    try:
        support_kpis = data_loader.calculate_support_kpis(dataset, fecha)
        return SupportKPIsResponse(**support_kpis)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_support_kpis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/funnel/{dataset}/{fecha}", response_model=FunnelResponse)
async def get_funnel(dataset: str, fecha: str):
    """
    Obtiene métricas del funnel de ventas para una fecha específica
    
    - **dataset**: A, B, C, o D
    - **fecha**: Fecha en formato YYYY-MM-DD
    """
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")

    try:
        funnel = data_loader.calculate_funnel_metrics(dataset, fecha)
        return FunnelResponse(**funnel)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_funnel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deal-trend/{dataset}/{day}")
async def get_deal_trend(dataset: str, day: str, days: int = 30):
    """
    Obtiene datos de tendencia de deals para los últimos N días
    
    - **dataset**: A, B, C, o D
    - **days**: Número de últimos días (default: 30)
    """
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    try:
        trend_data = data_loader.get_deal_trend(dataset, days, reference_day=day)
        return {"dataset": dataset, "days": days, "data": trend_data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_deal_trend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/support-trend/{dataset}/{day}")
async def get_support_trend(dataset: str, day: str, days: int = 30):
    """
    Obtiene series temporales de métricas de soporte para los últimos N días

    - **dataset**: A, B, C, o D
    - **day**: Fecha de referencia en formato YYYY-MM-DD
    """
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")

    try:
        trend_data = data_loader.get_support_trend(dataset, days, reference_day=day)
        return {"dataset": dataset, "days": days, "data": trend_data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_support_trend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights-advanced/{dataset}/{fecha}", response_model=AdvancedInsightResponse)
async def get_advanced_insights(dataset: str, fecha: str):
    """
    Genera análisis avanzado con LangChain + NVIDIA
    
    - **dataset**: A, B, C, o D
    - **fecha**: Fecha en formato YYYY-MM-DD
    """
    if not data_loader:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    try:
        # Obtener datos para análisis
        analysis_data = data_loader.get_data_for_insights(dataset, fecha)
        
        if not analysis_data['today']:
            raise HTTPException(status_code=404, detail=f"No hay datos para la fecha {fecha}")
        
        # Inicializar LangChain con NVIDIA
        api_key = os.getenv("API_KEY")
        model_name = os.getenv("MODEL", "gemini-2.5-flash")
        
        if not api_key:
            raise HTTPException(status_code=500, detail="API_KEY no configurada")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,
            google_api_key=api_key
        )
        structured_llm =llm.with_structured_output(AdvancedInsightResponse)
        # Crear prompt para análisis
        prompt = f"""Eres un analista senior de revenue operations y business intelligence B2B SaaS.

Tu tarea es analizar métricas comerciales, operacionales y de soporte para detectar insights relevantes, accionables y explicativos.

# CONTEXTO DE NEGOCIO

Las métricas pertenecen a un funnel comercial B2B:

- traffic: visitas o usuarios entrantes
- leads_created: leads generados
- leads_qualified: leads calificados por ventas
- deals_created: oportunidades creadas
- deals_won: negocios cerrados exitosamente
- deals_lost: negocios perdidos

Métricas operacionales:
- avg_response_time_min: tiempo promedio de respuesta comercial
- avg_deal_cycle_days: duración promedio del ciclo comercial
- stale_deals: oportunidades estancadas
- support_tickets_opened: tickets de soporte creados
- support_avg_resolution_hours: tiempo promedio de resolución

# OBJETIVO DEL ANÁLISIS

Detecta:
- mejoras relevantes,
- deterioros importantes,
- anomalías,
- cuellos de botella,
- problemas de conversión,
- eficiencia operacional,
- calidad del tráfico,
- inconsistencias del funnel.

# PUEDES CREAR MÉTRICAS DERIVADAS

Si es útil, calcula y razona usando métricas compuestas como:

- lead conversion rate
- qualification rate
- deal creation rate
- deal win rate
- loss rate
- traffic-to-win conversion
- response efficiency
- pipeline health
- support efficiency
- stale deal ratio

También puedes:
- comparar contra ayer,
- comparar contra promedio semanal,
- comparar contra mismo día semana pasada,
- detectar cambios porcentuales,
- detectar tendencias contradictorias.

# REGLAS IMPORTANTES

- Prioriza insights con impacto real de negocio.
- Evita repetir el mismo insight con wording distinto.
- Un insight debe explicar CAUSA o CONSECUENCIA.
- Insights positivos y negativos deben estar balanceados.
- Usa métricas derivadas si aportan valor.
- Sé específico y cuantitativo.
- Impacto:
  - alto → afecta revenue/funnel principal
  - medio → afecta eficiencia importante
  - bajo → señal secundaria

# DATOS
        
Hoy: {analysis_data['today']['metrics']}
Ayer: {analysis_data['yesterday']['metrics'] if analysis_data['yesterday'] else 'N/A'}
Promedio últimos 7 días: {analysis_data['avg_last_7_days']}
Mismo día semana pasada: {analysis_data['week_ago_same_day']['metrics'] if analysis_data['week_ago_same_day'] else 'N/A'}

Por favor, identifica exactamente 3 insights positivos y 3 negativos más relevantes.
Para cada uno, incluye: categoría, métrica afectada, descripción clara del insight, y el tipo (positivo/negativo).

Responde SOLO en JSON válido con esta estructura exacta:
{{
    "positivos": [
    {{"categoria": "...", "metrica": "...", "descripcion": "...", "tipo": "positivo", "impacto": "alto/medio/bajo"}},
    {{"categoria": "...", "metrica": "...", "descripcion": "...", "tipo": "positivo", "impacto": "alto/medio/bajo"}},
    {{"categoria": "...", "metrica": "...", "descripcion": "...", "tipo": "positivo", "impacto": "alto/medio/bajo"}}
    ],
    "negativos": [
    {{"categoria": "...", "metrica": "...", "descripcion": "...", "tipo": "negativo", "impacto": "alto/medio/bajo"}},
    {{"categoria": "...", "metrica": "...", "descripcion": "...", "tipo": "negativo", "impacto": "alto/medio/bajo"}},
    {{"categoria": "...", "metrica": "...", "descripcion": "...", "tipo": "negativo", "impacto": "alto/medio/bajo"}}
    ]
}}
"""
        logger.info(f"Enviando prompt a NVIDIA: {prompt}")
        response = await asyncio.to_thread(structured_llm.invoke, prompt)
        logger.info(f"Respuesta de NVIDIA: {response}")
        
        return AdvancedInsightResponse(
            positivos=response.positivos,
            negativos=response.negativos
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_advanced_insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))