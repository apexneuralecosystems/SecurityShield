import { useEffect, useState, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import StatCard from '../components/StatCard'
import WebsiteStatusList from '../components/WebsiteStatusList'
import { securityAPI } from '../services/api'
import { FiLock, FiRefreshCw, FiArrowLeft, FiGlobe, FiX, FiZap, FiShield } from 'react-icons/fi'
import { useDebouncedCallback } from '../utils/debounce'
import './Dashboard.css'

interface Website {
  url: string
  status: string
  issue_count: number
  high_issues: number
  medium_issues: number
  last_scan?: string
  error?: string
}

interface Summary {
  total_websites: number
  secure_websites: number
  successfully_scanned: number
  high_priority_issues: number
  total_issues: number
  medium_priority_issues: number
  security_score_percentage: number | null
}

interface LandingPageData {
  summary?: Summary
  websites?: Website[]
}

interface Message {
  type: 'success' | 'error'
  text: string
}

function Dashboard() {
  const [searchParams] = useSearchParams()
  const [data, setData] = useState<LandingPageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [websites, setWebsites] = useState<Website[]>([])
  const [newWebsite, setNewWebsite] = useState('')
  const [scanType, setScanType] = useState<'quick' | 'deep'>('quick')
  const [isAdding, setIsAdding] = useState(false)
  const [message, setMessage] = useState<Message | null>(null)
  const [zapStatus, setZapStatus] = useState<{ available: boolean; version: string | null } | null>(null)

  useEffect(() => {
    loadData()
    checkZapStatus()
    const scanUrl = searchParams.get('scan')
    if (scanUrl) {
      setNewWebsite(scanUrl)
      handleQuickScan(scanUrl)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  const checkZapStatus = async () => {
    try {
      const status = await securityAPI.getZapStatus()
      setZapStatus({
        available: status.available,
        version: status.version
      })
    } catch (err) {
      console.error('Failed to check ZAP status:', err)
      setZapStatus({ available: false, version: null })
    }
  }

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load landing page data which includes websites
      const response = await securityAPI.getLandingPageData()
      setData(response)
      setWebsites(response.websites || [])
    } catch (err: any) {
      console.error('Error loading data:', err)
      setError(err.message)
      // Fallback to empty state
      setWebsites([])
    } finally {
      setLoading(false)
    }
  }

  const isSubmittingRef = useRef(false)

  const handleQuickScan = async (url: string, type: 'quick' | 'deep' = 'quick') => {
    if (!url || isSubmittingRef.current) return
    
    isSubmittingRef.current = true
    setIsAdding(true)
    setMessage(null)
    
    try {
      const result = await securityAPI.addWebsiteAndScan(url, type)
      const scanTypeText = type === 'deep' ? 'Deep Scan (with OWASP ZAP)' : 'Quick Scan'
      setMessage({
        type: 'success',
        text: `Website added and ${scanTypeText} initiated! Scan ID: ${result.scan.id}${type === 'deep' ? ' (This may take 2-5 minutes)' : ''}`
      })
      setNewWebsite('')
      // Reload data after a delay (longer for deep scans)
      setTimeout(() => {
        loadData()
      }, type === 'deep' ? 5000 : 2000)
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.message || 'Failed to add website. Please try again.'
      })
    } finally {
      setIsAdding(false)
      // Reset after a delay to prevent rapid clicks
      setTimeout(() => {
        isSubmittingRef.current = false
      }, 1000)
    }
  }

  const debouncedHandleQuickScan = useDebouncedCallback(handleQuickScan, 300)
  const debouncedLoadData = useDebouncedCallback(loadData, 500)

  const handleAddWebsite = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newWebsite.trim() || isSubmittingRef.current) return
    
    // Warn if deep scan selected but ZAP not available
    if (scanType === 'deep' && zapStatus && !zapStatus.available) {
      setMessage({
        type: 'error',
        text: 'Deep scan requires OWASP ZAP to be running. Please start ZAP or use Quick Scan instead.'
      })
      return
    }
    
    await debouncedHandleQuickScan(newWebsite.trim(), scanType)
  }

  const handleRemoveWebsite = async (url: string) => {
    try {
      // Find website by URL
      const allWebsites = await securityAPI.getWebsites()
      const website = allWebsites.find(w => w.url === url || w.url === url + '/')
      
      if (website) {
        await securityAPI.deleteWebsite(website.id)
        setMessage({
          type: 'success',
          text: 'Website removed successfully'
        })
        loadData()
      } else {
        // If not found in API, just remove from local state
        const updated = websites.filter(w => w.url !== url)
        setWebsites(updated)
      }
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.message || 'Failed to remove website'
      })
    }
  }

  if (loading && !data) {
    return (
      <div className="page-container">
        <div className="loading">Loading your security dashboard...</div>
      </div>
    )
  }

  const summary: Summary = data?.summary || {
    total_websites: websites.length,
    secure_websites: websites.filter(w => w.status === 'secure').length,
    successfully_scanned: websites.filter(w => w.status !== 'scan_failed' && w.status !== 'not_scanned').length,
    high_priority_issues: websites.reduce((sum, w) => sum + (w.high_issues || 0), 0),
    total_issues: websites.reduce((sum, w) => sum + (w.issue_count || 0), 0),
    medium_priority_issues: websites.reduce((sum, w) => sum + (w.medium_issues || 0), 0),
    security_score_percentage: null
  }

  return (
    <div className="dashboard">
      <div className="page-container">
        <div className="dashboard-header">
          <div>
            <h1>
              <FiLock /> Your Security Dashboard
            </h1>
            <p>Monitor and manage security for all your websites</p>
          </div>
          <Link to="/" className="btn-back">
            <FiArrowLeft /> Back to Home
          </Link>
        </div>

        {/* Message Display */}
        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
            <button onClick={() => setMessage(null)} className="message-close">
              <FiX />
            </button>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
            <button onClick={() => setError(null)} className="error-close">
              <FiX />
            </button>
          </div>
        )}

        {/* Add Website Section */}
        <div className="add-website-section">
          <h2>Add a Website to Monitor</h2>
          <form onSubmit={handleAddWebsite} className="add-website-form">
            <div className="form-row">
              <input
                type="text"
                placeholder="https://yourwebsite.com"
                value={newWebsite}
                onChange={(e) => setNewWebsite(e.target.value)}
                className="website-input"
                required
                disabled={isAdding}
              />
              <div className="scan-type-selector">
                <label className="scan-type-label">
                  <input
                    type="radio"
                    name="scanType"
                    value="quick"
                    checked={scanType === 'quick'}
                    onChange={(e) => setScanType(e.target.value as 'quick' | 'deep')}
                    disabled={isAdding}
                  />
                  <span className="scan-type-option">
                    <FiShield /> Quick Scan
                  </span>
                </label>
                <label className="scan-type-label">
                  <input
                    type="radio"
                    name="scanType"
                    value="deep"
                    checked={scanType === 'deep'}
                    onChange={(e) => setScanType(e.target.value as 'quick' | 'deep')}
                    disabled={isAdding}
                  />
                  <span className={`scan-type-option ${!zapStatus?.available ? 'disabled' : ''}`}>
                    <FiZap /> Deep Scan {zapStatus?.available ? `(ZAP v${zapStatus.version})` : '(ZAP Required)'}
                  </span>
                </label>
              </div>
              <button type="submit" className="btn-add" disabled={isAdding}>
                {isAdding ? (
                  scanType === 'deep' ? 'Adding & Deep Scanning...' : 'Adding & Scanning...'
                ) : (
                  <>
                    <span>+</span> Add & {scanType === 'deep' ? 'Deep Scan' : 'Scan'}
                  </>
                )}
              </button>
            </div>
          </form>
          <div className="add-note-container">
            <p className="add-note">
              {scanType === 'deep' ? (
                <>
                  <strong>Deep Scan:</strong> Comprehensive OWASP ZAP analysis including spider crawling and active vulnerability testing (2-5 minutes). 
                  {!zapStatus?.available && (
                    <span className="zap-warning"> ⚠️ OWASP ZAP must be running for deep scans.</span>
                  )}
                </>
              ) : (
                <>
                  <strong>Quick Scan:</strong> Fast HTTPS/TLS, headers, and cookie security check (~10 seconds).
                </>
              )}
            </p>
            {zapStatus && (
              <div className={`zap-status-indicator ${zapStatus.available ? 'available' : 'unavailable'}`}>
                <FiZap /> ZAP: {zapStatus.available ? `Available (v${zapStatus.version})` : 'Not Available'}
              </div>
            )}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <StatCard
            title="Websites Monitored"
            value={summary.total_websites}
            subtitle={summary.successfully_scanned !== undefined ? `${summary.successfully_scanned} successfully scanned` : `${websites.filter(w => w.status !== 'scan_failed' && w.status !== 'not_scanned').length} successfully scanned`}
            color="#0052a3"
          />
          <StatCard
            title="Secure Websites"
            value={summary.secure_websites}
            subtitle={`${summary.total_websites > 0 ? Math.round((summary.secure_websites / summary.total_websites) * 100) : 0}% of total`}
            color="#27ae60"
          />
          <StatCard
            title="High Priority Issues"
            value={summary.high_priority_issues}
            subtitle="Requiring immediate attention"
            color="#e74c3c"
          />
          <StatCard
            title="Total Issues"
            value={summary.total_issues}
            subtitle={`${summary.medium_priority_issues || 0} medium priority`}
            color="#f39c12"
          />
        </div>

        {/* Websites List */}
        {websites.length > 0 ? (
          <WebsiteStatusList websites={websites} onRemove={handleRemoveWebsite} />
        ) : (
          <div className="empty-state">
            <div className="empty-icon">
              <FiGlobe />
            </div>
            <h2>No Websites Added Yet</h2>
            <p>Add your first website above to start monitoring its security.</p>
          </div>
        )}

        {/* Actions */}
        <div className="dashboard-actions">
          <button 
            onClick={() => {
              if (!loading) {
                debouncedLoadData()
              }
            }} 
            className="btn-refresh" 
            disabled={loading}
          >
            {loading ? (
              <>
                <FiRefreshCw className="spinning" /> Refreshing...
              </>
            ) : (
              <>
                <FiRefreshCw /> Refresh All Scans
              </>
            )}
          </button>
          <Link to="/security" className="btn-secondary">
            Learn About Security Features
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

