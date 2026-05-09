import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DealTrendChart({ data, loading, error }) {
  if (loading) {
    return <div className="chart-loading">Cargando gráfico...</div>
  }

  if (error) {
    return <div className="chart-error">Error: {error}</div>
  }

  if (!data || data.length === 0) {
    return <div className="chart-empty">No hay datos disponibles</div>
  }

  // Formatear fechas para mostrar MM-DD en el gráfico
  const formattedData = data.map(item => ({
    ...item,
    dateLabel: new Date(item.date).toLocaleDateString('es-ES', { month: '2-digit', day: '2-digit' })
  }))

  return (
    <div className="deal-trend-container">
      <h3>Deal Trend (Last 30 Days)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(21, 32, 51, 0.08)" />
          <XAxis 
            dataKey="dateLabel"
            tick={{ fontSize: 12, fill: 'rgba(21, 32, 51, 0.6)' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            tick={{ fontSize: 12, fill: 'rgba(21, 32, 51, 0.6)' }}
          />
          <Tooltip 
            contentStyle={{
              background: 'rgba(255, 255, 255, 0.9)',
              border: '1px solid rgba(21, 32, 51, 0.1)',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#152033' }}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          <Line 
            type="monotone" 
            dataKey="deals_created" 
            stroke="#4c64d4" 
            strokeWidth={2}
            dot={{ fill: '#4c64d4', r: 4 }}
            activeDot={{ r: 6 }}
            name="Deals Created"
          />
          <Line 
            type="monotone" 
            dataKey="deals_won" 
            stroke="#4caf50" 
            strokeWidth={2}
            dot={{ fill: '#4caf50', r: 4 }}
            activeDot={{ r: 6 }}
            name="Deals Won"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
