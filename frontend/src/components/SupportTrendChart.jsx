import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function SupportTrendChart({ data, loading, error, metricKey, title, color }) {
  if (loading) {
    return <div className="chart-loading">Cargando gráfico...</div>
  }

  if (error) {
    return <div className="chart-error">Error: {error}</div>
  }

  if (!data || data.length === 0) {
    return <div className="chart-empty">No hay datos disponibles</div>
  }

  const formattedData = data.map(item => ({
    ...item,
    dateLabel: new Date(item.date).toLocaleDateString('es-ES', { month: '2-digit', day: '2-digit' })
  }))

  return (
    <div className="support-trend-container">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={formattedData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(21, 32, 51, 0.08)" />
          <XAxis 
            dataKey="dateLabel"
            tick={{ fontSize: 12, fill: 'rgba(21, 32, 51, 0.6)' }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fontSize: 12, fill: 'rgba(21, 32, 51, 0.6)' }} />
          <Tooltip 
            contentStyle={{
              background: 'rgba(255, 255, 255, 0.9)',
              border: '1px solid rgba(21, 32, 51, 0.1)',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#152033' }}
          />
          <Legend wrapperStyle={{ paddingTop: '12px' }} iconType="line" />
          <Line 
            type="monotone" 
            dataKey={metricKey} 
            stroke={color || '#4c64d4'} 
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
            name={title}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
