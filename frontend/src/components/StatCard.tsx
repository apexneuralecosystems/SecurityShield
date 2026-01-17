import './StatCard.css'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  color?: string
}

function StatCard({ title, value, subtitle, color = '#0052a3' }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-value" style={{ color }}>
        {value}
      </div>
      <div className="stat-title">{title}</div>
      {subtitle && <div className="stat-subtitle">{subtitle}</div>}
    </div>
  )
}

export default StatCard

