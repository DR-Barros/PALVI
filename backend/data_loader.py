import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

class DataLoader:
    """Carga y gestiona los datos de metrics.json"""
    
    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.data: Dict[str, Any] = {}
        self.load_data()
    
    def load_data(self):
        """Carga el archivo JSON"""
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo: {self.data_file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Error al parsear JSON en: {self.data_file_path}")
    
    def get_datasets(self) -> List[str]:
        """Retorna la lista de datasets disponibles (A, B, C, D)"""
        return list(self.data.keys())
    
    def get_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """Retorna todo el dataset (metadata + todos los days)"""
        if dataset_name not in self.data:
            raise ValueError(f"Dataset '{dataset_name}' no encontrado. Disponibles: {self.get_datasets()}")
        return self.data[dataset_name]
    
    def get_dataset_metadata(self, dataset_name: str) -> Dict[str, Any]:
        """Retorna solo metadata del dataset"""
        dataset = self.get_dataset(dataset_name)
        return dataset.get('metadata', {})
    
    def get_dataset_latest_days(self, dataset_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Retorna los últimos N días del dataset"""
        dataset = self.get_dataset(dataset_name)
        days_data = dataset.get('days', [])
        return days_data[-days:] if days > 0 else days_data
    
    def get_dataset_summary_stats(self, dataset_name: str, days: int = 30) -> Dict[str, Any]:
        """Calcula estadísticas agregadas de los últimos N días"""
        latest_days = self.get_dataset_latest_days(dataset_name, days)
        
        if not latest_days:
            return {}
        
        # Extraer todas las métricas
        all_metrics = latest_days[0]['metrics'].keys()
        stats = {}
        
        for metric_key in all_metrics:
            values = [day['metrics'].get(metric_key, 0) for day in latest_days]
            stats[metric_key] = {
                'current': latest_days[-1]['metrics'].get(metric_key, 0),
                'average': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'total': sum(values)
            }
        
        return stats
    
    def get_all_datasets_summary(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Retorna resumen de todos los datasets"""
        result = {}
        for dataset_name in self.get_datasets():
            result[dataset_name] = {
                'metadata': self.get_dataset_metadata(dataset_name),
                'latest_days': self.get_dataset_latest_days(dataset_name, days),
                'summary': self.get_dataset_summary_stats(dataset_name, days)
            }
        return result
    
    def get_metric_by_date(self, dataset_name: str, target_date: str) -> Dict[str, Any]:
        """Obtiene métricas para una fecha específica"""
        dataset = self.get_dataset(dataset_name)
        days_data = dataset.get('days', [])
        
        for day in days_data:
            if day['date'] == target_date:
                return {'date': target_date, 'metrics': day['metrics']}
        return None
    
    def get_data_for_insights(self, dataset_name: str, target_date: str) -> Dict[str, Any]:
        """Obtiene datos para análisis: hoy, ayer, promedio 7 días, mismo día semana pasada"""
        target = datetime.strptime(target_date, '%Y-%m-%d')
        
        today_data = self.get_metric_by_date(dataset_name, target_date)
        yesterday_date = (target - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_data = self.get_metric_by_date(dataset_name, yesterday_date)
        
        # Promedio últimos 7 días
        last_7_dates = [(target - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
        last_7_data = [self.get_metric_by_date(dataset_name, d) for d in last_7_dates if self.get_metric_by_date(dataset_name, d)]
        
        # Mismo día semana pasada
        week_ago_date = (target - timedelta(days=7)).strftime('%Y-%m-%d')
        week_ago_data = self.get_metric_by_date(dataset_name, week_ago_date)
        
        # Calcular promedio 7 días
        avg_7 = {}
        if last_7_data:
            metric_keys = last_7_data[0]['metrics'].keys()
            for key in metric_keys:
                values = [d['metrics'].get(key, 0) for d in last_7_data]
                avg_7[key] = sum(values) / len(values)
        
        return {
            'today': today_data,
            'yesterday': yesterday_data,
            'avg_last_7_days': avg_7,
            'week_ago_same_day': week_ago_data
        }
    
    def calculate_kpis(self, dataset_name: str, target_date: str) -> Dict[str, Any]:
        """
        Calcula KPIs de ventas para una fecha específica con comparativas.
        
        KPIs:
        - Deals Won: número de deals ganados hoy vs ayer (D-1)
        - Win Rate: (deals_won / (deals_won + deals_lost)) * 100 vs D-7
        - Deal Velocity: deals_created / avg_deal_cycle_days vs D-7
        - Pipeline Risk: (stale_deals / deals_created) * 100 vs D-30
        """
        target = datetime.strptime(target_date, '%Y-%m-%d')
        
        # Obtener datos para hoy
        today_data = self.get_metric_by_date(dataset_name, target_date)
        if not today_data:
            raise ValueError(f"No hay datos para la fecha {target_date}")
        
        today_metrics = today_data['metrics']
        
        # Obtener datos para D-1 (ayer)
        d_minus_1_date = (target - timedelta(days=1)).strftime('%Y-%m-%d')
        d_minus_1_data = self.get_metric_by_date(dataset_name, d_minus_1_date)
        d_minus_1_metrics = d_minus_1_data['metrics'] if d_minus_1_data else None
        
        # Obtener datos para D-7 (hace 7 días)
        d_minus_7_date = (target - timedelta(days=7)).strftime('%Y-%m-%d')
        d_minus_7_data = self.get_metric_by_date(dataset_name, d_minus_7_date)
        d_minus_7_metrics = d_minus_7_data['metrics'] if d_minus_7_data else None
        
        # Obtener datos para D-30 (hace 30 días)
        d_minus_30_date = (target - timedelta(days=30)).strftime('%Y-%m-%d')
        d_minus_30_data = self.get_metric_by_date(dataset_name, d_minus_30_date)
        d_minus_30_metrics = d_minus_30_data['metrics'] if d_minus_30_data else None
        
        # ======================== Deals Won ========================
        deals_won_current = today_metrics.get('deals_won', 0)
        deals_won_previous = d_minus_1_metrics.get('deals_won', 0) if d_minus_1_metrics else 0
        deals_won_change = deals_won_current - deals_won_previous
        deals_won_change_pct = (
            (deals_won_change / deals_won_previous * 100) 
            if deals_won_previous != 0 else 0
        )
        
        # ======================== Win Rate ========================
        # Hoy: (deals_won / (deals_won + deals_lost)) * 100
        deals_won_today = today_metrics.get('deals_won', 0)
        deals_lost_today = today_metrics.get('deals_lost', 0)
        win_rate_current = (
            (deals_won_today / (deals_won_today + deals_lost_today) * 100)
            if (deals_won_today + deals_lost_today) > 0 else 0
        )
        
        # D-7
        if d_minus_7_metrics:
            deals_won_d7 = d_minus_7_metrics.get('deals_won', 0)
            deals_lost_d7 = d_minus_7_metrics.get('deals_lost', 0)
            win_rate_previous = (
                (deals_won_d7 / (deals_won_d7 + deals_lost_d7) * 100)
                if (deals_won_d7 + deals_lost_d7) > 0 else 0
            )
        else:
            win_rate_previous = 0
        
        win_rate_change = win_rate_current - win_rate_previous
        win_rate_change_pct = win_rate_change  # Ya está en porcentaje absoluto
        
        # ======================== Deal Velocity ========================
        # Hoy: deals_created / avg_deal_cycle_days
        deals_created_today = today_metrics.get('deals_created', 0)
        avg_cycle_today = today_metrics.get('avg_deal_cycle_days', 1)
        deal_velocity_current = (
            deals_created_today / avg_cycle_today if avg_cycle_today > 0 else 0
        )
        
        # D-7
        if d_minus_7_metrics:
            deals_created_d7 = d_minus_7_metrics.get('deals_created', 0)
            avg_cycle_d7 = d_minus_7_metrics.get('avg_deal_cycle_days', 1)
            deal_velocity_previous = (
                deals_created_d7 / avg_cycle_d7 if avg_cycle_d7 > 0 else 0
            )
        else:
            deal_velocity_previous = 0
        
        deal_velocity_change = deal_velocity_current - deal_velocity_previous
        deal_velocity_change_pct = (
            (deal_velocity_change / deal_velocity_previous * 100)
            if deal_velocity_previous != 0 else 0
        )
        
        # ======================== Pipeline Risk ========================
        # Hoy: (stale_deals / deals_created) * 100
        stale_deals_today = today_metrics.get('stale_deals', 0)
        deals_created_for_risk = today_metrics.get('deals_created', 1)
        pipeline_risk_current = (
            (stale_deals_today / deals_created_for_risk * 100)
            if deals_created_for_risk > 0 else 0
        )
        
        # D-30
        if d_minus_30_metrics:
            stale_deals_d30 = d_minus_30_metrics.get('stale_deals', 0)
            deals_created_d30 = d_minus_30_metrics.get('deals_created', 1)
            pipeline_risk_previous = (
                (stale_deals_d30 / deals_created_d30 * 100)
                if deals_created_d30 > 0 else 0
            )
        else:
            pipeline_risk_previous = 0
        
        pipeline_risk_change = pipeline_risk_current - pipeline_risk_previous
        pipeline_risk_change_pct = (
            (pipeline_risk_change / pipeline_risk_previous * 100)
            if pipeline_risk_previous != 0 else 0
        )
        
        return {
            'date': target_date,
            'deals_won': {
                'current': deals_won_current,
                'previous': deals_won_previous,
                'change': deals_won_change,
                'change_pct': round(deals_won_change_pct, 2),
                'period_compared': 'vs yesterday'
            },
            'win_rate': {
                'current': round(win_rate_current, 2),
                'previous': round(win_rate_previous, 2),
                'change': round(win_rate_change, 2),
                'change_pct': round(win_rate_change_pct, 2),
                'period_compared': 'vs 7 days ago'
            },
            'deal_velocity': {
                'current': round(deal_velocity_current, 2),
                'previous': round(deal_velocity_previous, 2),
                'change': round(deal_velocity_change, 2),
                'change_pct': round(deal_velocity_change_pct, 2),
                'period_compared': 'vs 7 days ago'
            },
            'pipeline_risk': {
                'current': round(pipeline_risk_current, 2),
                'previous': round(pipeline_risk_previous, 2),
                'change': round(pipeline_risk_change, 2),
                'change_pct': round(pipeline_risk_change_pct, 2),
                'period_compared': 'vs 30 days ago'
            }
        }

    def calculate_support_kpis(self, dataset_name: str, target_date: str) -> Dict[str, Any]:
        """
        Calcula KPIs de Customer Support para una fecha específica.

        KPIs:
        - Response Time: avg_response_time_min vs D-7
        - Resolution Time: support_avg_resolution_hours vs D-7
        - Ticket Volume: support_tickets_opened vs D-1
        - Support Load: support_tickets_opened * support_avg_resolution_hours vs promedio 7 días
        """
        target = datetime.strptime(target_date, '%Y-%m-%d')

        today_data = self.get_metric_by_date(dataset_name, target_date)
        if not today_data:
            raise ValueError(f"No hay datos para la fecha {target_date}")

        today_metrics = today_data['metrics']

        d_minus_1_date = (target - timedelta(days=1)).strftime('%Y-%m-%d')
        d_minus_1_data = self.get_metric_by_date(dataset_name, d_minus_1_date)
        d_minus_1_metrics = d_minus_1_data['metrics'] if d_minus_1_data else None

        d_minus_7_date = (target - timedelta(days=7)).strftime('%Y-%m-%d')
        d_minus_7_data = self.get_metric_by_date(dataset_name, d_minus_7_date)

        last_7_dates = [(target - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
        last_7_data = [self.get_metric_by_date(dataset_name, date) for date in last_7_dates if self.get_metric_by_date(dataset_name, date)]

        def build_kpi(current: float, previous: float, period_compared: str) -> Dict[str, Any]:
            change = current - previous
            change_pct = (change / previous * 100) if previous != 0 else 0
            return {
                'current': round(current, 2),
                'previous': round(previous, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'period_compared': period_compared,
            }

        response_time_current = today_metrics.get('avg_response_time_min', 0)
        response_time_previous = (
            d_minus_7_data['metrics'].get('avg_response_time_min', 0)
            if d_minus_7_data else 0
        )

        resolution_time_current = today_metrics.get('support_avg_resolution_hours', 0)
        resolution_time_previous = (
            d_minus_7_data['metrics'].get('support_avg_resolution_hours', 0)
            if d_minus_7_data else 0
        )

        ticket_volume_current = today_metrics.get('support_tickets_opened', 0)
        ticket_volume_previous = d_minus_1_metrics.get('support_tickets_opened', 0) if d_minus_1_metrics else 0

        support_load_current = today_metrics.get('support_tickets_opened', 0) * today_metrics.get('support_avg_resolution_hours', 0)
        support_load_previous_values = [
            day['metrics'].get('support_tickets_opened', 0) * day['metrics'].get('support_avg_resolution_hours', 0)
            for day in last_7_data
        ]
        support_load_previous = (
            sum(support_load_previous_values) / len(support_load_previous_values)
            if support_load_previous_values else 0
        )

        return {
            'date': target_date,
            'response_time': build_kpi(response_time_current, response_time_previous, 'vs 7 days ago'),
            'resolution_time': build_kpi(resolution_time_current, resolution_time_previous, 'vs 7 days ago'),
            'ticket_volume': build_kpi(ticket_volume_current, ticket_volume_previous, 'vs yesterday'),
            'support_load': build_kpi(support_load_current, support_load_previous, 'vs 7-day average'),
        }
    
    def get_deal_trend(self, dataset_name: str, days: int = 30, reference_day: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene tendencia de deals para los últimos N días.
        Retorna: lista de {date, deals_created, deals_won, deals_lost}
        """
        if reference_day:
            # Si se especifica un día de referencia, obtener los N días anteriores a ese día
            ref_date = datetime.strptime(reference_day, '%Y-%m-%d')
            start_date = (ref_date - timedelta(days=days)).strftime('%Y-%m-%d')
            latest_days = [day for day in self.get_dataset(dataset_name).get('days', []) 
                           if start_date <= day['date'] <= reference_day]
        else:
            latest_days = self.get_dataset_latest_days(dataset_name, days)
        
        trend_data = []
        for day in latest_days:
            trend_data.append({
                'date': day['date'],
                'deals_created': day['metrics'].get('deals_created', 0),
                'deals_won': day['metrics'].get('deals_won', 0),
                'deals_lost': day['metrics'].get('deals_lost', 0)
            })
        
        return trend_data

    def get_support_trend(self, dataset_name: str, days: int = 30, reference_day: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene tendencia de métricas de soporte para los últimos N días.
        Retorna: lista de {date, support_tickets_opened, support_avg_resolution_hours, avg_response_time_min}
        """
        if reference_day:
            # Si se especifica un día de referencia, obtener los N días anteriores a ese día
            ref_date = datetime.strptime(reference_day, '%Y-%m-%d')
            start_date = (ref_date - timedelta(days=days)).strftime('%Y-%m-%d')
            latest_days = [day for day in self.get_dataset(dataset_name).get('days', []) 
                           if start_date <= day['date'] <= reference_day]
        else:
            latest_days = self.get_dataset_latest_days(dataset_name, days)

        trend_data = []
        for day in latest_days:
            trend_data.append({
                'date': day['date'],
                'support_tickets_opened': day['metrics'].get('support_tickets_opened', 0),
                'support_avg_resolution_hours': day['metrics'].get('support_avg_resolution_hours', 0),
                'avg_response_time_min': day['metrics'].get('avg_response_time_min', 0)
            })

        return trend_data

    def calculate_funnel_metrics(self, dataset_name: str, target_date: str) -> Dict[str, Any]:
        """
        Calcula métricas del funnel de ventas para una fecha específica.

        Stages:
        Traffic -> Leads Created -> Leads Qualified -> Deals Created -> Deals Won
        Comparación: vs 7 días atrás (D-7)
        """
        target = datetime.strptime(target_date, '%Y-%m-%d')

        today_data = self.get_metric_by_date(dataset_name, target_date)
        if not today_data:
            raise ValueError(f"No hay datos para la fecha {target_date}")

        today_metrics = today_data['metrics']

        d_minus_7_date = (target - timedelta(days=7)).strftime('%Y-%m-%d')
        d_minus_7_data = self.get_metric_by_date(dataset_name, d_minus_7_date)
        d_minus_7_metrics = d_minus_7_data['metrics'] if d_minus_7_data else None

        def safe_ratio(numerator: float, denominator: float) -> float:
            return (numerator / denominator * 100) if denominator > 0 else 0

        def stage_change(current: float, previous: float) -> Dict[str, Any]:
            change = current - previous
            change_pct = (change / previous * 100) if previous != 0 else 0
            return {
                'previous': round(previous, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
            }

        traffic_current = today_metrics.get('traffic', 0)
        leads_created_current = today_metrics.get('leads_created', 0)
        leads_qualified_current = today_metrics.get('leads_qualified', 0)
        deals_created_current = today_metrics.get('deals_created', 0)
        deals_won_current = today_metrics.get('deals_won', 0)

        traffic_previous = d_minus_7_metrics.get('traffic', 0) if d_minus_7_metrics else 0
        leads_created_previous = d_minus_7_metrics.get('leads_created', 0) if d_minus_7_metrics else 0
        leads_qualified_previous = d_minus_7_metrics.get('leads_qualified', 0) if d_minus_7_metrics else 0
        deals_created_previous = d_minus_7_metrics.get('deals_created', 0) if d_minus_7_metrics else 0
        deals_won_previous = d_minus_7_metrics.get('deals_won', 0) if d_minus_7_metrics else 0

        stage_1_current = safe_ratio(leads_created_current, traffic_current)
        stage_1_previous = safe_ratio(leads_created_previous, traffic_previous)
        stage_2_current = safe_ratio(leads_qualified_current, leads_created_current)
        stage_2_previous = safe_ratio(leads_qualified_previous, leads_created_previous)
        stage_3_current = safe_ratio(deals_created_current, leads_qualified_current)
        stage_3_previous = safe_ratio(deals_created_previous, leads_qualified_previous)
        stage_4_current = safe_ratio(deals_won_current, deals_created_current)
        stage_4_previous = safe_ratio(deals_won_previous, deals_created_previous)

        funnel_stages = [
            {
                'key': 'traffic',
                'label': 'Traffic',
                'value': traffic_current,
                'previous': traffic_previous,
                **stage_change(traffic_current, traffic_previous),
            },
            {
                'key': 'leads_created',
                'label': 'Leads Created',
                'value': leads_created_current,
                'previous': leads_created_previous,
                **stage_change(leads_created_current, leads_created_previous),
                'conversion_rate': round(stage_1_current, 2),
                'previous_conversion_rate': round(stage_1_previous, 2),
                'conversion_change': round(stage_1_current - stage_1_previous, 2),
                'conversion_change_pct': round(((stage_1_current - stage_1_previous) / stage_1_previous * 100), 2) if stage_1_previous != 0 else 0,
                'transition': 'Traffic -> Leads Created'
            },
            {
                'key': 'leads_qualified',
                'label': 'Leads Qualified',
                'value': leads_qualified_current,
                'previous': leads_qualified_previous,
                **stage_change(leads_qualified_current, leads_qualified_previous),
                'conversion_rate': round(stage_2_current, 2),
                'previous_conversion_rate': round(stage_2_previous, 2),
                'conversion_change': round(stage_2_current - stage_2_previous, 2),
                'conversion_change_pct': round(((stage_2_current - stage_2_previous) / stage_2_previous * 100), 2) if stage_2_previous != 0 else 0,
                'transition': 'Leads Created -> Leads Qualified'
            },
            {
                'key': 'deals_created',
                'label': 'Deals Created',
                'value': deals_created_current,
                'previous': deals_created_previous,
                **stage_change(deals_created_current, deals_created_previous),
                'conversion_rate': round(stage_3_current, 2),
                'previous_conversion_rate': round(stage_3_previous, 2),
                'conversion_change': round(stage_3_current - stage_3_previous, 2),
                'conversion_change_pct': round(((stage_3_current - stage_3_previous) / stage_3_previous * 100), 2) if stage_3_previous != 0 else 0,
                'transition': 'Leads Qualified -> Deals Created'
            },
            {
                'key': 'deals_won',
                'label': 'Deals Won',
                'value': deals_won_current,
                'previous': deals_won_previous,
                **stage_change(deals_won_current, deals_won_previous),
                'conversion_rate': round(stage_4_current, 2),
                'previous_conversion_rate': round(stage_4_previous, 2),
                'conversion_change': round(stage_4_current - stage_4_previous, 2),
                'conversion_change_pct': round(((stage_4_current - stage_4_previous) / stage_4_previous * 100), 2) if stage_4_previous != 0 else 0,
                'transition': 'Deals Created -> Deals Won'
            },
        ]

        conversion_stages = [
            {
                'key': 'leads_created',
                'label': 'Traffic -> Leads Created',
                'conversion_rate': round(stage_1_current, 2),
                'previous_conversion_rate': round(stage_1_previous, 2),
                'conversion_change': round(stage_1_current - stage_1_previous, 2),
                'dropoff_pct': round(max(0, 100 - stage_1_current), 2)
            },
            {
                'key': 'leads_qualified',
                'label': 'Leads Created -> Leads Qualified',
                'conversion_rate': round(stage_2_current, 2),
                'previous_conversion_rate': round(stage_2_previous, 2),
                'conversion_change': round(stage_2_current - stage_2_previous, 2),
                'dropoff_pct': round(max(0, 100 - stage_2_current), 2)
            },
            {
                'key': 'deals_created',
                'label': 'Leads Qualified -> Deals Created',
                'conversion_rate': round(stage_3_current, 2),
                'previous_conversion_rate': round(stage_3_previous, 2),
                'conversion_change': round(stage_3_current - stage_3_previous, 2),
                'dropoff_pct': round(max(0, 100 - stage_3_current), 2)
            },
            {
                'key': 'deals_won',
                'label': 'Deals Created -> Deals Won',
                'conversion_rate': round(stage_4_current, 2),
                'previous_conversion_rate': round(stage_4_previous, 2),
                'conversion_change': round(stage_4_current - stage_4_previous, 2),
                'dropoff_pct': round(max(0, 100 - stage_4_current), 2)
            },
        ]

        best_stage = max(conversion_stages, key=lambda item: item['conversion_rate']) if conversion_stages else None
        weakest_stage = min(conversion_stages, key=lambda item: item['conversion_rate']) if conversion_stages else None
        bottleneck_stage = max(conversion_stages, key=lambda item: item['dropoff_pct']) if conversion_stages else None

        return {
            'date': target_date,
            'stages': funnel_stages,
            'insights': {
                'best_stage': best_stage,
                'weakest_stage': weakest_stage,
                'bottleneck': bottleneck_stage,
            }
        }

# Inicializar al módulo importarse
def get_data_loader():
    """Factory function para obtener instancia de DataLoader"""
    # Buscar metrics.json en la raíz del proyecto
    base_path = Path(__file__).parent
    data_file = base_path / "metrics.json"
    
    if not data_file.exists():
        raise FileNotFoundError(f"metrics.json no encontrado en {base_path}")
    
    return DataLoader(str(data_file))
