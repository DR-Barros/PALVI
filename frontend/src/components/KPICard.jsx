export default function KPICard({
  title,
  value,
  previous,
  unit = '',
  period = 'vs yesterday',
  icon = null,
  isLowerBetter = false
}) {
  const change = value - previous
  const changePct = previous !== 0 ? ((change / previous) * 100).toFixed(2) : 0

  let indicator = '→'
  let indicatorColor = '#7e8a9a'

  if (change > 0) {
    indicator = '▲'
    indicatorColor = isLowerBetter ? '#ef6c6c' : '#4caf50'
  } else if (change < 0) {
    indicator = '▼'
    indicatorColor = isLowerBetter ? '#4caf50' : '#ef6c6c'
  }

  const formatValue = (num) => {
    if (typeof num !== 'number') return num
    return num % 1 !== 0 ? num.toFixed(2) : Math.round(num)
  }

  return (
    <div className="kpi-card">
      <div className="kpi-header">
        {icon && <span className="kpi-icon">{icon}</span>}
        <h3 className="kpi-title">{title}</h3>
      </div>

      <div className="kpi-value-container">
        <div className="kpi-main-value">
          {formatValue(value)}
          <span className="kpi-unit">{unit}</span>
        </div>
      </div>

      <div className="kpi-comparison">
        <div className="kpi-change">
          <span className="kpi-indicator" style={{ color: indicatorColor }}>
            {indicator}
          </span>
          <span className="kpi-change-value">
            {change >= 0 ? '+' : ''}{formatValue(change)}{unit}
          </span>
          <span className="kpi-change-pct">({changePct}%)</span>
        </div>
        <div className="kpi-period">{period}</div>
      </div>

      <div className="kpi-previous">
        Previous: {formatValue(previous)}{unit}
      </div>
    </div>
  )
}
