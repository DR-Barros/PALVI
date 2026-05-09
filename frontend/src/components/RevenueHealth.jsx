import { useState, useEffect } from 'react'
import KPICard from './KPICard'
import DealTrendChart from './DealTrendChart'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function RevenueHealth({ dataset, day }) {
  const [kpis, setKpis] = useState(null)
  const [trendData, setTrendData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [trendLoading, setTrendLoading] = useState(false)
  const [error, setError] = useState(null)
  const [trendError, setTrendError] = useState(null)

  useEffect(() => {
    if (!dataset || !day) return

    async function loadKPIs() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`${API_URL}/api/kpis/${dataset}/${day}`)
        if (!response.ok) {
          throw new Error(`Error ${response.status}: Error al cargar KPIs`)
        }
        const data = await response.json()
        setKpis(data)
      } catch (err) {
        setError(err.message)
        console.error('Error cargando KPIs:', err)
      } finally {
        setLoading(false)
      }
    }

    loadKPIs()
  }, [dataset, day])

  useEffect(() => {
    if (!dataset || !day) return

    async function loadTrend() {
      setTrendLoading(true)
      setTrendError(null)
      try {
        const response = await fetch(`${API_URL}/api/deal-trend/${dataset}/${day}?days=30`)
        if (!response.ok) {
          throw new Error(`Error ${response.status}: Error al cargar tendencia`)
        }
        const data = await response.json()
        setTrendData(data.data)
      } catch (err) {
        setTrendError(err.message)
        console.error('Error cargando deal trend:', err)
      } finally {
        setTrendLoading(false)
      }
    }

    loadTrend()
  }, [dataset, day])

  return (
    <section className="dashboard-card">
      <h2>Revenue Health</h2>
      <div className="card-content">
        {loading && (
          <div className="kpi-loading">Cargando KPIs...</div>
        )}
        
        {error && (
          <div className="kpi-error">
            Error: {error}
          </div>
        )}
        
        {kpis && !loading && !error && (
          <div className="kpi-grid">
            <KPICard
              title="Deals Won"
              value={kpis.deals_won.current}
              previous={kpis.deals_won.previous}
              unit=" deals"
              period={kpis.deals_won.period_compared}
              icon="📊"
              isLowerBetter={false}
            />
            <KPICard
              title="Win Rate"
              value={kpis.win_rate.current}
              previous={kpis.win_rate.previous}
              unit="%"
              period={kpis.win_rate.period_compared}
              icon="🎯"
              isLowerBetter={false}
            />
            <KPICard
              title="Deal Velocity"
              value={kpis.deal_velocity.current}
              previous={kpis.deal_velocity.previous}
              unit=" deals/day"
              period={kpis.deal_velocity.period_compared}
              icon="⚡"
              isLowerBetter={false}
            />
            <KPICard
              title="Pipeline Risk"
              value={kpis.pipeline_risk.current}
              previous={kpis.pipeline_risk.previous}
              unit="%"
              period={kpis.pipeline_risk.period_compared}
              icon="⚠️"
              isLowerBetter={true}
            />
          </div>
        )}
      </div>

      {/* Deal Trend Chart */}
      <div className="card-content chart-section">
        <DealTrendChart 
          data={trendData} 
          loading={trendLoading} 
          error={trendError}
        />
      </div>
    </section>
  )
}
