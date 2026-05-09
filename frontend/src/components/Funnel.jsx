import { useEffect, useState } from 'react'
import KPICard from './KPICard'
import FunnelChart from './FunnelChart'
import FunnelInsights from './FunnelInsights'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Funnel({ dataset, day }) {
  const [funnelData, setFunnelData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!dataset || !day) {
      return
    }

    async function loadFunnel() {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`${API_URL}/api/funnel/${dataset}/${day}`)

        if (!response.ok) {
          throw new Error(`Error ${response.status}: Error al cargar funnel`)
        }

        const data = await response.json()
        setFunnelData(data)
      } catch (err) {
        setError(err.message)
        console.error('Error cargando funnel:', err)
      } finally {
        setLoading(false)
      }
    }

    loadFunnel()
  }, [dataset, day])

  const stageCards = funnelData?.stages || []

  return (
    <section className="dashboard-card">
      <h2>Funnel</h2>

      <div className="funnel-shell">
        <div className="funnel-stage-grid">
          {loading && <div className="funnel-state">Cargando KPIs del funnel...</div>}

          {error && <div className="funnel-state error">Error: {error}</div>}

          {!loading && !error && stageCards.length > 0 && stageCards.map((stage) => (
            <KPICard
              key={stage.key}
              title={stage.label}
              value={stage.value}
              previous={stage.previous}
              unit={stage.key === 'traffic' ? ' visits' : ' deals'}
              period="vs 7 days ago"
              icon={stage.key === 'traffic' ? '🌐' : stage.key === 'leads_created' ? '🧲' : stage.key === 'leads_qualified' ? '✅' : stage.key === 'deals_created' ? '💼' : '🏆'}
              isLowerBetter={false}
            />
          ))}
        </div>

        <div className="funnel-visual-grid">
          <FunnelChart stages={stageCards} loading={loading} error={error} />
          <FunnelInsights insights={funnelData?.insights} />
        </div>
      </div>
    </section>
  )
}
