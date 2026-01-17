import { Link } from 'react-router-dom'
import { FiShield } from 'react-icons/fi'
import './SecurityBadge.css'

interface SecurityBadgeProps {
  variant?: 'standard' | 'compact' | 'large'
  compact?: boolean
}

function SecurityBadge({ variant = 'standard', compact = false }: SecurityBadgeProps) {
  const className = `security-badge ${variant} ${compact ? 'compact' : ''}`
  
  return (
    <Link to="/security" className={className}>
      <span className="badge-icon">
        <FiShield />
      </span>
      <span className="badge-text">
        <span className="badge-main">OWASP-Aligned</span>
        {!compact && <span className="badge-sub">Continuously Monitored</span>}
      </span>
    </Link>
  )
}

export default SecurityBadge

