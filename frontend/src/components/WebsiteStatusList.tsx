import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiX, FiChevronRight, FiCopy, FiCheck } from 'react-icons/fi'
import { useDebouncedCallback } from '../utils/debounce'
import './WebsiteStatusList.css'
import { securityAPI } from '../services/api'

interface Website {
  url: string
  status: string
  issue_count: number
  high_issues: number
  medium_issues: number
  low_issues?: number
  last_scan?: string
  error?: string
}

interface WebsiteStatusListProps {
  websites?: Website[]
  onRemove?: ((url: string) => void) | null
}

function WebsiteStatusList({ websites = [], onRemove = null }: WebsiteStatusListProps) {
  const navigate = useNavigate()
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null)
  const isRemovingRef = useRef<string | null>(null)

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'secure':
        return '#27ae60'
      case 'needs_attention':
        return '#e74c3c'
      case 'scan_failed':
        return '#b8c5d1'
      default:
        return '#0052a3'
    }
  }

  const getStatusLabel = (status: string): string => {
    switch (status) {
      case 'secure':
        return 'Secure'
      case 'needs_attention':
        return 'Needs Attention'
      case 'scan_failed':
        return 'Scan Failed'
      default:
        return status
    }
  }

  const copyUrlToClipboard = async (url: string) => {
    if (copiedUrl === url) return // Prevent multiple rapid copies
    
    try {
      await navigator.clipboard.writeText(url)
      setCopiedUrl(url)
      setTimeout(() => setCopiedUrl(null), 2000)
    } catch (err) {
      console.error('Failed to copy URL:', err)
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = url
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.select()
      try {
        document.execCommand('copy')
        setCopiedUrl(url)
        setTimeout(() => setCopiedUrl(null), 2000)
      } catch (fallbackErr) {
        console.error('Fallback copy failed:', fallbackErr)
      }
      document.body.removeChild(textArea)
    }
  }

  const debouncedCopyUrl = useDebouncedCallback(copyUrlToClipboard, 200)

  const handleRemove = async (url: string) => {
    if (isRemovingRef.current === url) return // Prevent double-clicks
    
    isRemovingRef.current = url
    if (onRemove) {
      await onRemove(url)
    }
    setTimeout(() => {
      isRemovingRef.current = null
    }, 1000)
  }

  const handleWebsiteClick = async (site: Website) => {
    try {
      // Get website by URL to find the ID
      const allWebsites = await securityAPI.getWebsites()
      const website = allWebsites.find(
        w => w.url === site.url || 
             w.url === site.url + '/' || 
             w.url === site.url.replace(/\/$/, '')
      )
      
      if (website) {
        navigate(`/website/${website.id}`)
      } else {
        console.error('Website not found in database')
      }
    } catch (err) {
      console.error('Error navigating to website details:', err)
    }
  }

  return (
    <div className="website-status-list">
      <h2>Website Status ({websites.length} websites monitored)</h2>
      <div className="website-grid">
        {websites.map((site, index) => (
          <div
            key={index}
            className={`website-item ${site.status} clickable`}
            style={{ borderLeftColor: getStatusColor(site.status) }}
            onClick={() => handleWebsiteClick(site)}
            title="Click to view detailed issues"
          >
            <div className="website-url-with-copy">
              <h3 className="website-url-display">{site.url}</h3>
              <button
                className={`copy-url-btn-small ${copiedUrl === site.url ? 'copied' : ''}`}
                onClick={(e) => {
                  e.stopPropagation()
                  debouncedCopyUrl(site.url)
                }}
                title="Copy URL to clipboard"
                aria-label="Copy URL"
              >
                {copiedUrl === site.url ? <FiCheck /> : <FiCopy />}
              </button>
            </div>
            <div className="website-meta">
              <span className="status-badge" style={{ background: getStatusColor(site.status) }}>
                {getStatusLabel(site.status)}
              </span>
              <span className="issues-count">Issues: {site.issue_count}</span>
              {site.high_issues > 0 && (
                <span className="high-issues">High: {site.high_issues}</span>
              )}
              {site.medium_issues > 0 && (
                <span className="medium-issues">Medium: {site.medium_issues}</span>
              )}
              {site.low_issues !== undefined && site.low_issues > 0 && (
                <span className="low-issues">Low: {site.low_issues}</span>
              )}
            </div>
            {site.last_scan && (
              <div className="last-scan">
                Last scanned: {new Date(site.last_scan).toLocaleString()}
              </div>
            )}
            {site.error && (
              <div className="error-message">
                <small>Error: {site.error.substring(0, 100)}...</small>
              </div>
            )}
            <div className="website-actions">
              {onRemove ? (
                <button 
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRemove(site.url)
                  }}
                  className="btn-remove"
                  title="Remove website"
                  disabled={isRemovingRef.current === site.url}
                >
                  <FiX /> Remove
                </button>
              ) : (
                <span></span>
              )}
              <span className="view-details-hint">
                Click to view details <FiChevronRight />
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default WebsiteStatusList

