import { useEffect, useState } from 'react'
import KPICard from './KPICard'
import SupportTrendChart from './SupportTrendChart'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function CustomerSupport({ dataset, day }) {
  const [kpis, setKpis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [supportTrend, setSupportTrend] = useState(null)
  const [loadingTrend, setLoadingTrend] = useState(false)
  const [errorTrend, setErrorTrend] = useState(null)

  useEffect(() => {
    if (!dataset || !day) return

    async function loadSupportKPIs() {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`${API_URL}/api/support-kpis/${dataset}/${day}`)
        if (!response.ok) {
          throw new Error(`Error ${response.status}: Error al cargar KPIs de soporte`)
        }

        const data = await response.json()
        setKpis(data)
      } catch (err) {
        setError(err.message)
        console.error('Error cargando Customer Support KPIs:', err)
      } finally {
        setLoading(false)
      }
    }

    loadSupportKPIs()
  }, [dataset, day])

  useEffect(() => {
    if (!dataset || !day) return

    async function loadSupportTrend() {
      setLoadingTrend(true)
      setErrorTrend(null)

      try {
        const response = await fetch(`${API_URL}/api/support-trend/${dataset}/${day}?days=30`)
        if (!response.ok) {
          throw new Error(`Error ${response.status}: Error al cargar tendencia de soporte`)
        }

        const json = await response.json()
        setSupportTrend(json.data)
      } catch (err) {
        setErrorTrend(err.message)
        console.error('Error cargando Support Trend:', err)
      } finally {
        setLoadingTrend(false)
      }
    }

    loadSupportTrend()
  }, [dataset, day])

  return (
    <section className="dashboard-card customer-support-card">
      <h2>Customer Support</h2>
      <div className="card-content">
        {loading && <div className="kpi-loading">Cargando KPIs de soporte...</div>}

        {error && (
          <div className="kpi-error">
            Error: {error}
          </div>
        )}

        {kpis && !loading && !error && (
          <div className="kpi-grid">
            <KPICard
              title="Response Time"
              value={kpis.response_time.current}
              previous={kpis.response_time.previous}
              unit=" min"
              period={kpis.response_time.period_compared}
              icon="⏱️"
              isLowerBetter={true}
            />
            <KPICard
              title="Resolution Time"
              value={kpis.resolution_time.current}
              previous={kpis.resolution_time.previous}
              unit=" hrs"
              period={kpis.resolution_time.period_compared}
              icon="🛠️"
              isLowerBetter={true}
            />
            <KPICard
              title="Ticket Volume"
              value={kpis.ticket_volume.current}
              previous={kpis.ticket_volume.previous}
              unit=" tickets"
              period={kpis.ticket_volume.period_compared}
              icon="🎫"
              isLowerBetter={true}
            />
            <KPICard
              title="Support Load"
              value={kpis.support_load.current}
              previous={kpis.support_load.previous}
              unit=" index"
              period={kpis.support_load.period_compared}
              icon="📈"
              isLowerBetter={true}
            />
          </div>
        )}

        {/* Charts */}
        <div className="support-charts">
          {loadingTrend && <div className="chart-loading">Cargando gráficos de soporte...</div>}

          {errorTrend && (
            <div className="chart-error">Error: {errorTrend}</div>
          )}

          {supportTrend && !loadingTrend && !errorTrend && (
            <div className="charts-grid">
              <SupportTrendChart
                data={supportTrend}
                loading={loadingTrend}
                error={errorTrend}
                metricKey="support_avg_resolution_hours"
                title="Response Time Trend (hours)"
                color="#ff9800"
              />

              <SupportTrendChart
                data={supportTrend}
                loading={loadingTrend}
                error={errorTrend}
                metricKey="support_tickets_opened"
                title="Support Lead — Tickets Created"
                color="#4caf50"
              />
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
