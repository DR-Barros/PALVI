export default function FunnelInsights({ insights }) {
  if (!insights) {
    return null
  }

  const cards = [
    {
      title: 'Best Stage',
      tone: 'good',
      icon: '▲',
      item: insights.best_stage,
      detail: `${insights.best_stage.conversion_rate}% conversion`
    },
    {
      title: 'Weakest Stage',
      tone: 'warning',
      icon: '●',
      item: insights.weakest_stage,
      detail: `${insights.weakest_stage.conversion_rate}% conversion`
    },
    {
      title: 'Bottleneck',
      tone: 'danger',
      icon: '⚠',
      item: insights.bottleneck,
      detail: `${insights.bottleneck.dropoff_pct}% drop-off`
    }
  ]

  return (
    <div className="funnel-insights">
      <h3>Funnel Insights</h3>
      <div className="funnel-insight-grid">
        {cards.map((card) => (
          <article key={card.title} className={`funnel-insight-card ${card.tone}`}>
            <div className="funnel-insight-icon">{card.icon}</div>
            <div className="funnel-insight-copy">
              <div className="funnel-insight-title">{card.title}</div>
              <div className="funnel-insight-stage">{card.item.label}</div>
              <div className="funnel-insight-detail">{card.detail}</div>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}