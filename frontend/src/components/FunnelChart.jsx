import {
  FunnelChart as RechartsFunnelChart,
  Funnel,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from 'recharts'

export default function FunnelChart({ stages, loading, error }) {
  if (loading) {
    return <div className="funnel-state">Cargando funnel...</div>
  }

  if (error) {
    return <div className="funnel-state error">Error: {error}</div>
  }

  if (!stages || stages.length === 0) {
    return <div className="funnel-state">No hay datos disponibles</div>
  }

  const chartData = stages.map((stage, index) => ({
    name: stage.label,
    value: stage.value,
    conversionRate: stage.conversion_rate,
    fill: ['#4c64d4', '#5b7ee8', '#67a6f0', '#7bc48f', '#4caf50'][index] || '#4c64d4'
  }))

  return (
    <div className="funnel-chart-container">
      <div className="funnel-chart-header">
        <h3>Sales Funnel</h3>
        <span className="funnel-chart-subtitle">Traffic to Deals Won</span>
      </div>

      <ResponsiveContainer width="100%" height={360}>
        <RechartsFunnelChart>
          <Tooltip
            formatter={(value, name, props) => {
              if (name === 'value') {
                return [value, props.payload.name]
              }
              return [value, name]
            }}
            contentStyle={{
              background: 'rgba(255, 255, 255, 0.96)',
              border: '1px solid rgba(21, 32, 51, 0.1)',
              borderRadius: '10px',
              boxShadow: '0 12px 30px rgba(21, 32, 51, 0.12)'
            }}
          />
          <Funnel dataKey="value" data={chartData} isAnimationActive>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
            <LabelList position="right" fill="#152033" stroke="none" dataKey="name" />
          </Funnel>
        </RechartsFunnelChart>
      </ResponsiveContainer>

      <div className="funnel-conversion-list">
        {stages
          .filter((stage) => stage.conversion_rate !== null && stage.conversion_rate !== undefined)
          .map((stage) => (
            <div key={stage.key} className="funnel-conversion-item">
              <div>
                <div className="funnel-conversion-label">{stage.transition}</div>
                <div className="funnel-conversion-change">
                  {stage.conversion_change >= 0 ? '+' : ''}{stage.conversion_change}% vs D-7
                </div>
              </div>
              <div className="funnel-conversion-value">{stage.conversion_rate}%</div>
            </div>
          ))}
      </div>
    </div>
  )
}