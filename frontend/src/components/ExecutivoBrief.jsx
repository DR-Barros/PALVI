import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ExecutivoBrief({ dataset, day }) {
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!dataset || !day) {
      setInsights(null)
      return
    }

    async function loadInsights() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`${API_URL}/api/insights-advanced/${dataset}/${day}`)
        if (!response.ok) throw new Error('Error al cargar insights')
        const data = await response.json()
        setInsights(data)
      } catch (err) {
        setError(err.message)
        console.error('Error cargando insights:', err)
      } finally {
        setLoading(false)
      }
    }

    loadInsights()
  }, [dataset, day])

  return (
    <section className="dashboard-card">
      <h2>Executive Brief</h2>
      <div className="card-content insights-content">
        {loading && <p className="status-message">Generando análisis con IA...</p>}
        {error && <p className="status-message error">Error: {error}</p>}
        {insights && (
          <div className="insights-container">
            {insights.positivos.length > 0 && (
              <div className="insights-group">
                <h3 className="insights-title positive">✓ Insights Positivos</h3>
                {insights.positivos.map((insight, idx) => (
                  <div key={idx} className="insight-item positive">
                    <div className="insight-header">
                      <strong>{insight.metrica}</strong>
                      <span className={`impact-badge impact-${insight.impacto.toLowerCase()}`}>
                        {insight.impacto}
                      </span>
                    </div>
                    <p className="insight-description">{insight.descripcion}</p>
                    <small className="insight-category">{insight.categoria}</small>
                  </div>
                ))}
              </div>
            )}
            {insights.negativos.length > 0 && (
              <div className="insights-group">
                <h3 className="insights-title negative">✗ Áreas de Mejora</h3>
                {insights.negativos.map((insight, idx) => (
                  <div key={idx} className="insight-item negative">
                    <div className="insight-header">
                      <strong>{insight.metrica}</strong>
                      <span className={`impact-badge impact-${insight.impacto.toLowerCase()}`}>
                        {insight.impacto}
                      </span>
                    </div>
                    <p className="insight-description">{insight.descripcion}</p>
                    <small className="insight-category">{insight.categoria}</small>
                  </div>
                ))}
              </div>
            )}
            {insights.positivos.length === 0 && insights.negativos.length === 0 && (
              <p className="status-message">Sin insights disponibles</p>
            )}
          </div>
        )}
        {!loading && !insights && !error && (
          <p className="status-message">Selecciona dataset y fecha para ver análisis</p>
        )}
      </div>
    </section>
  )
}
