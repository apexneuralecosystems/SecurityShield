import { useEffect, useState, useRef } from 'react'
import { useDebouncedCallback } from '../utils/debounce'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { securityAPI } from '../services/api'
import { 
  FiLock, 
  FiShield, 
  FiRefreshCw, 
  FiCheckCircle, 
  FiAlertCircle, 
  FiAlertTriangle, 
  FiInfo,
  FiArrowLeft,
  FiX,
  FiZap,
  FiCopy,
  FiCheck
} from 'react-icons/fi'
import './WebsiteDetails.css'

interface Website {
  id: number
  url: string
  name?: string
  description?: string
}

interface Issue {
  id: number
  impact?: string
  issue_type: string
  description: string
  status?: string
  reported_at?: string
}

interface ZapScanResult {
  success: boolean
  error?: string
  total_alerts: number
  summary: {
    high: number
    medium: number
    low: number
    informational: number
  }
  alerts?: Array<{
    risk: string
    risk_lower: string
    name: string
    description: string
    solution?: string
    url?: string
  }>
  scan_time?: string
}

interface Scan {
  id: number
  website_id: number
  scan_type?: string
  status?: string
  scan_time?: string
  total_issues?: number
  high_issues?: number
  medium_issues?: number
  low_issues?: number
  security_score?: number | null
  owasp_aligned?: boolean
  error_message?: string
  zap_results?: ZapScanResult
  issues?: Issue[]
}

interface GroupedIssues {
  HIGH: Issue[]
  MEDIUM: Issue[]
  LOW: Issue[]
}

function WebsiteDetails() {
  const { websiteId } = useParams<{ websiteId: string }>()
  const navigate = useNavigate()
  const [website, setWebsite] = useState<Website | null>(null)
  const [scan, setScan] = useState<Scan | null>(null)
  const [issues, setIssues] = useState<Issue[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scanType, setScanType] = useState<'quick' | 'deep'>('quick')
  const [isScanning, setIsScanning] = useState(false)
  const [zapStatus, setZapStatus] = useState<{ available: boolean; version: string | null } | null>(null)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [urlCopied, setUrlCopied] = useState(false)
  const isScanningRef = useRef(false)

  useEffect(() => {
    loadWebsiteDetails()
    checkZapStatus()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [websiteId])

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

  const copyUrlToClipboard = async (url: string) => {
    if (urlCopied) return // Prevent multiple rapid copies
    
    try {
      await navigator.clipboard.writeText(url)
      setUrlCopied(true)
      setTimeout(() => setUrlCopied(false), 2000)
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
        setUrlCopied(true)
        setTimeout(() => setUrlCopied(false), 2000)
      } catch (fallbackErr) {
        console.error('Fallback copy failed:', fallbackErr)
      }
      document.body.removeChild(textArea)
    }
  }

  const debouncedCopyUrl = useDebouncedCallback(copyUrlToClipboard, 200)

  const loadWebsiteDetails = async () => {
    if (!websiteId) return
    
    try {
      setLoading(true)
      setError(null)

      // Get website details
      const websiteData = await securityAPI.getWebsite(parseInt(websiteId))
      setWebsite(websiteData)

      // Get latest scan with issues
      try {
        const latestScan = await securityAPI.getLatestScan(parseInt(websiteId))
        setScan(latestScan)
        setIssues(latestScan.issues || [])
      } catch (err) {
        // If no scan found, try to get issues directly
        try {
          const issuesData = await securityAPI.getIssues({ scan_id: null })
          // Filter by website if needed
          setIssues([])
        } catch (issuesErr) {
          setIssues([])
        }
      }
    } catch (err: any) {
      console.error('Error loading website details:', err)
      setError(err.message || 'Failed to load website details')
    } finally {
      setLoading(false)
    }
  }

  const getImpactColor = (impact?: string): string => {
    switch (impact?.toUpperCase()) {
      case 'HIGH':
        return '#e74c3c'
      case 'MEDIUM':
        return '#f39c12'
      case 'LOW':
        return '#95a5a6'
      default:
        return '#0052a3'
    }
  }

  const getImpactBadge = (impact?: string) => {
    const color = getImpactColor(impact)
    return (
      <span className="impact-badge" style={{ background: color }}>
        {impact?.toUpperCase() || 'UNKNOWN'}
      </span>
    )
  }

  const groupIssuesByImpact = (issues: Issue[]): GroupedIssues => {
    const grouped: GroupedIssues = {
      HIGH: [],
      MEDIUM: [],
      LOW: []
    }
    issues.forEach(issue => {
      const impact = issue.impact?.toUpperCase() || 'LOW'
      if (impact === 'HIGH' || impact === 'MEDIUM' || impact === 'LOW') {
        grouped[impact].push(issue)
      } else {
        grouped.LOW.push(issue)
      }
    })
    return grouped
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading">Loading website details...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-banner">
          <strong>Error:</strong> {error}
          <Link to="/dashboard" className="btn-back">← Back to Dashboard</Link>
        </div>
      </div>
    )
  }

  if (!website) {
    return (
      <div className="page-container">
        <div className="error-banner">
          <strong>Website not found</strong>
          <Link to="/dashboard" className="btn-back">← Back to Dashboard</Link>
        </div>
      </div>
    )
  }

  const groupedIssues = groupIssuesByImpact(issues)
  const totalIssues = issues.length
  const highIssues = groupedIssues.HIGH.length
  const mediumIssues = groupedIssues.MEDIUM.length
  const lowIssues = groupedIssues.LOW.length

  return (
    <div className="website-details">
      <div className="page-container">
        <div className="details-header">
          <div>
            <Link to="/dashboard" className="btn-back">
              <FiArrowLeft /> Back to Dashboard
            </Link>
            <h1 className="website-url-header">
              <FiLock /> Security Details: 
            </h1>
            <div className="website-url-container">
              <span 
                className="website-url-text" 
                title={website.url}
                onMouseEnter={() => setUrlCopied(false)}
              >
                {website.url}
              </span>
              <button
                className={`copy-url-btn ${urlCopied ? 'copied' : ''}`}
                onClick={(e) => {
                  e.stopPropagation()
                  debouncedCopyUrl(website.url)
                }}
                title="Copy URL to clipboard"
                aria-label="Copy URL"
              >
                {urlCopied ? <FiCheck /> : <FiCopy />}
              </button>
            </div>
            {website.name && <p className="website-name">{website.name}</p>}
            <div className="scan-type-badge">
              <span className="owasp-badge">
                <FiShield /> OWASP Top-10 Aligned Security Scanning
              </span>
              {scan && (
                <span className={`scan-type ${scan.scan_type === 'deep' ? 'deep-scan' : 'quick-scan'}`}>
                  {scan.scan_type === 'deep' ? (
                    <>
                      <FiZap /> Deep Scan (OWASP ZAP)
                    </>
                  ) : (
                    <>
                      <FiShield /> Quick Scan
                    </>
                  )}
                </span>
              )}
            </div>
          </div>
          <button 
            onClick={() => {
              if (!loading) {
                loadWebsiteDetails()
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
                <FiRefreshCw /> Refresh
              </>
            )}
          </button>
        </div>

        {/* Scan Summary */}
        {scan && (
          <div className="scan-summary">
            <div className="summary-grid">
              <div className="summary-card">
                <div className="summary-value">{totalIssues}</div>
                <div className="summary-label">Total Issues</div>
              </div>
              <div className="summary-card high">
                <div className="summary-value">{highIssues}</div>
                <div className="summary-label">High Priority</div>
              </div>
              <div className="summary-card medium">
                <div className="summary-value">{mediumIssues}</div>
                <div className="summary-label">Medium Priority</div>
              </div>
              <div className="summary-card low">
                <div className="summary-value">{lowIssues}</div>
                <div className="summary-label">Low Priority</div>
              </div>
            </div>
            <div className="scan-meta">
              <p>
                <strong>Scan Type:</strong> 
                {scan.scan_type === 'deep' ? (
                  <span className="scan-type-meta deep">
                    <FiZap /> Deep Scan (OWASP ZAP) 
                    {scan.zap_results?.success && (
                      <span className="zap-success"> • ZAP Scan Completed</span>
                    )}
                    {scan.zap_results && !scan.zap_results.success && (
                      <span className="zap-error"> • ZAP Scan Failed: {scan.zap_results.error}</span>
                    )}
                  </span>
                ) : (
                  <span className="scan-type-meta quick">
                    <FiShield /> Quick Scan
                  </span>
                )}
                {scan.owasp_aligned && <span className="owasp-indicator"> • OWASP Top-10 Aligned</span>}
              </p>
              <p>
                <strong>Scan Time:</strong> {scan.scan_time ? new Date(scan.scan_time).toLocaleString() : 'N/A'}
              </p>
              <p>
                <strong>Status:</strong> <span className={`status-${scan.status}`}>{scan.status?.toUpperCase() || 'UNKNOWN'}</span>
              </p>
              {scan.security_score !== null && scan.security_score !== undefined && (
                <p>
                  <strong>Security Score:</strong> {scan.security_score}%
                  <small className="score-disclaimer">
                    {' '}• Score reflects current configuration posture and does not guarantee absence of vulnerabilities
                  </small>
                </p>
              )}
            </div>
          </div>
        )}

        {/* Message Display */}
        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
            <button onClick={() => setMessage(null)} className="message-close">
              <FiX />
            </button>
          </div>
        )}

        {/* Error Message */}
        {scan?.error_message && (
          <div className="error-banner">
            <strong>Scan Error:</strong> {scan.error_message}
          </div>
        )}

        {/* Issues List */}
        {totalIssues === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <FiCheckCircle />
            </div>
            <h2>No Issues Found</h2>
            <p>This website has no security issues detected. Great job!</p>
          </div>
        ) : (
          <div className="issues-section">
            <div className="issues-header">
              <h2>Security Issues Detected</h2>
              <p className="issues-subtitle">
                These findings are detected through <strong>OWASP Top-10 aligned automated security scanning</strong>, 
                including checks for HTTPS/TLS enforcement, secure HTTP headers (CSP, HSTS, XFO, X-XSS-Protection, Referrer-Policy), 
                cookie security, and server disclosure vulnerabilities. 
                <em>Findings are categorized by risk level based on security best practices and OWASP guidance.</em>
              </p>
            </div>
            
            {/* High Priority Issues */}
            {groupedIssues.HIGH.length > 0 && (
              <div className="issues-group high-priority">
                <h3 className="group-header high">
                  <FiAlertCircle className="header-icon" />
                  High Priority Issues ({groupedIssues.HIGH.length})
                  <span className="priority-note">High-Risk Security Findings (OWASP-aligned)</span>
                </h3>
                <div className="issues-list">
                  {groupedIssues.HIGH.map((issue) => (
                    <div key={issue.id} className="issue-card high">
                      <div className="issue-header">
                        {getImpactBadge(issue.impact)}
                        <h4>{issue.issue_type}</h4>
                      </div>
                      <p className="issue-description">{issue.description}</p>
                      <div className="issue-meta">
                        <span>Status: {issue.status || 'open'}</span>
                        {issue.reported_at && (
                          <span>Reported: {new Date(issue.reported_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Medium Priority Issues */}
            {groupedIssues.MEDIUM.length > 0 && (
              <div className="issues-group medium-priority">
                <h3 className="group-header medium">
                  <FiAlertTriangle className="header-icon" />
                  Medium Priority Issues ({groupedIssues.MEDIUM.length})
                  <span className="priority-note">Security Best Practices (OWASP-aligned)</span>
                </h3>
                <div className="issues-list">
                  {groupedIssues.MEDIUM.map((issue) => (
                    <div key={issue.id} className="issue-card medium">
                      <div className="issue-header">
                        {getImpactBadge(issue.impact)}
                        <h4>{issue.issue_type}</h4>
                      </div>
                      <p className="issue-description">{issue.description}</p>
                      <div className="issue-meta">
                        <span>Status: {issue.status || 'open'}</span>
                        {issue.reported_at && (
                          <span>Reported: {new Date(issue.reported_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Low Priority Issues */}
            {groupedIssues.LOW.length > 0 && (
              <div className="issues-group low-priority">
                <h3 className="group-header low">
                  <FiInfo className="header-icon" />
                  Low Priority Issues ({groupedIssues.LOW.length})
                  <span className="priority-note">Informational Findings (OWASP-aligned)</span>
                </h3>
                <div className="issues-list">
                  {groupedIssues.LOW.map((issue) => (
                    <div key={issue.id} className="issue-card low">
                      <div className="issue-header">
                        {getImpactBadge(issue.impact)}
                        <h4>{issue.issue_type}</h4>
                      </div>
                      <p className="issue-description">{issue.description}</p>
                      <div className="issue-meta">
                        <span>Status: {issue.status || 'open'}</span>
                        {issue.reported_at && (
                          <span>Reported: {new Date(issue.reported_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ZAP Results Section */}
        {scan?.zap_results && scan.scan_type === 'deep' && (
          <div className="zap-results-section">
            <h2>
              <FiZap /> OWASP ZAP Deep Scan Results
            </h2>
            {scan.zap_results.success ? (
              <div className="zap-results-content">
                <div className="zap-summary-grid">
                  <div className="zap-summary-card high">
                    <div className="zap-summary-value">{scan.zap_results.summary.high}</div>
                    <div className="zap-summary-label">High Risk</div>
                  </div>
                  <div className="zap-summary-card medium">
                    <div className="zap-summary-value">{scan.zap_results.summary.medium}</div>
                    <div className="zap-summary-label">Medium Risk</div>
                  </div>
                  <div className="zap-summary-card low">
                    <div className="zap-summary-value">{scan.zap_results.summary.low}</div>
                    <div className="zap-summary-label">Low Risk</div>
                  </div>
                  <div className="zap-summary-card info">
                    <div className="zap-summary-value">{scan.zap_results.summary.informational}</div>
                    <div className="zap-summary-label">Informational</div>
                  </div>
                </div>
                <p className="zap-note">
                  <strong>Total ZAP Alerts:</strong> {scan.zap_results.total_alerts} vulnerabilities detected through automated spider crawling and active scanning.
                </p>
                {scan.zap_results.alerts && scan.zap_results.alerts.length > 0 && (
                  <div className="zap-alerts-preview">
                    <h3>Sample ZAP Findings:</h3>
                    <div className="zap-alerts-list">
                      {scan.zap_results.alerts.slice(0, 5).map((alert, idx) => (
                        <div key={idx} className={`zap-alert-card ${alert.risk_lower}`}>
                          <div className="zap-alert-header">
                            <span className={`zap-risk-badge ${alert.risk_lower}`}>
                              {alert.risk}
                            </span>
                            <h4>{alert.name}</h4>
                          </div>
                          <p className="zap-alert-description">{alert.description}</p>
                          {alert.solution && (
                            <p className="zap-alert-solution">
                              <strong>Solution:</strong> {alert.solution}
                            </p>
                          )}
                        </div>
                      ))}
                      {scan.zap_results.alerts.length > 5 && (
                        <p className="zap-more-alerts">
                          + {scan.zap_results.alerts.length - 5} more alerts (see Issues section above for all findings)
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="zap-error-message">
                <p><strong>ZAP Scan Failed:</strong> {scan.zap_results.error}</p>
                <p className="zap-error-note">
                  Quick scan results are still available above. Ensure OWASP ZAP is running for deep scans.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="details-actions">
          <div className="scan-actions-group">
            <div className="scan-type-selector-inline">
              <label className="scan-type-label-inline">
                <input
                  type="radio"
                  name="scanTypeDetails"
                  value="quick"
                  checked={scanType === 'quick'}
                  onChange={(e) => setScanType(e.target.value as 'quick' | 'deep')}
                  disabled={isScanning}
                />
                <span className="scan-type-option-inline">
                  <FiShield /> Quick
                </span>
              </label>
              <label className="scan-type-label-inline">
                <input
                  type="radio"
                  name="scanTypeDetails"
                  value="deep"
                  checked={scanType === 'deep'}
                  onChange={(e) => setScanType(e.target.value as 'quick' | 'deep')}
                  disabled={isScanning}
                />
                <span className={`scan-type-option-inline ${!zapStatus?.available ? 'disabled' : ''}`}>
                  <FiZap /> Deep {zapStatus?.available ? `(ZAP v${zapStatus.version})` : '(ZAP Required)'}
                </span>
              </label>
            </div>
            <button 
              onClick={async () => {
                if (website && !isScanningRef.current) {
                  if (scanType === 'deep' && zapStatus && !zapStatus.available) {
                    setError('Deep scan requires OWASP ZAP to be running. Please start ZAP or use Quick Scan.')
                    return
                  }
                  
                  isScanningRef.current = true
                  setIsScanning(true)
                  setError(null)
                  try {
                    await securityAPI.createScan({ website_id: website.id, scan_type: scanType })
                    setMessage({
                      type: 'success',
                      text: `${scanType === 'deep' ? 'Deep scan' : 'Quick scan'} initiated! ${scanType === 'deep' ? 'This may take 2-5 minutes.' : 'Results will appear shortly.'}`
                    })
                    // Wait longer for deep scans
                    setTimeout(() => {
                      loadWebsiteDetails()
                      setIsScanning(false)
                      setTimeout(() => {
                        isScanningRef.current = false
                      }, 1000)
                    }, scanType === 'deep' ? 10000 : 3000)
                  } catch (err: any) {
                    setError(err.message || 'Failed to start scan')
                    setIsScanning(false)
                    isScanningRef.current = false
                  }
                }
              }}
              className="btn-primary"
              disabled={loading || isScanning}
            >
              {isScanning ? (
                <>
                  <FiRefreshCw className="spinning" /> Scanning...
                </>
              ) : (
                <>
                  <FiRefreshCw /> Run {scanType === 'deep' ? 'Deep' : 'Quick'} Scan
                </>
              )}
            </button>
          </div>
          <Link to="/dashboard" className="btn-secondary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

export default WebsiteDetails

