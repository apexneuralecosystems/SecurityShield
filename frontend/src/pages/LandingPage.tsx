import { useEffect, useState, useRef } from 'react'
import { useDebouncedCallback } from '../utils/debounce'
import {
    FiAlertCircle,
    FiAlertTriangle,
    FiBarChart2,
    FiBell,
    FiCheck,
    FiFileText,
    FiGlobe,
    FiInfo,
    FiLock,
    FiSearch,
    FiShield,
    FiX,
    FiZap
} from 'react-icons/fi'
import { Link, useNavigate } from 'react-router-dom'
import SecurityBadge from '../components/SecurityBadge'
import { authAPI, securityAPI } from '../services/api'
import './LandingPage.css'

interface DemoIssue {
  impact: string
  issue_type: string
  description: string
}

interface DemoScanResponse {
  scan_time: string
  status: string
  error_message?: string
  total_issues: number
  high_issues: number
  medium_issues: number
  low_issues: number
  security_score?: number
  owasp_aligned: boolean
  issues: DemoIssue[]
  scan_type: string
  is_demo: boolean
}

interface GroupedIssues {
  HIGH: DemoIssue[]
  MEDIUM: DemoIssue[]
  LOW: DemoIssue[]
}

function LandingPage() {
  const [url, setUrl] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [demoResults, setDemoResults] = useState<DemoScanResponse | null>(null)
  const [showResults, setShowResults] = useState(false)
  const navigate = useNavigate()
  const isSubmittingRef = useRef(false)

  useEffect(() => {
    // Check if user is authenticated
    setIsAuthenticated(authAPI.isAuthenticated())
  }, [])

  const handleQuickCheck = async (urlToScan: string) => {
    if (!urlToScan || isSubmittingRef.current) return
    
    isSubmittingRef.current = true
    setIsScanning(true)
    setError(null)
    setDemoResults(null)
    
    try {
      // If user is authenticated, use regular scan flow
      if (authAPI.isAuthenticated()) {
        await securityAPI.addWebsiteAndScan(urlToScan, 'quick')
        navigate(`/dashboard?scan=${encodeURIComponent(urlToScan)}`)
        return
      }
      
      // For non-authenticated users, use demo scan
      const result = await securityAPI.demoScan(urlToScan)
      
      if (result.status === 'failed') {
        setError(result.error_message || 'Failed to scan website. Please try again.')
        setIsScanning(false)
        isSubmittingRef.current = false
        return
      }
      
      // Show demo results
      setDemoResults(result)
      setShowResults(true)
      setIsScanning(false)
    } catch (err: any) {
      setError(err.message || 'Failed to scan website. Please try again.')
      setIsScanning(false)
    } finally {
      setTimeout(() => {
        isSubmittingRef.current = false
      }, 1000)
    }
  }

  const debouncedHandleQuickCheck = useDebouncedCallback(handleQuickCheck, 300)

  const handleQuickCheckSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url) return
    await debouncedHandleQuickCheck(url)
  }

  const groupIssuesByImpact = (issues: DemoIssue[]): GroupedIssues => {
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

  const getImpactBadge = (impact: string) => {
    const colorMap: Record<string, string> = {
      'HIGH': '#e74c3c',
      'MEDIUM': '#f39c12',
      'LOW': '#95a5a6'
    }
    const color = colorMap[impact?.toUpperCase()] || '#0052a3'
    return (
      <span className="demo-impact-badge" style={{ background: color }}>
        {impact?.toUpperCase() || 'UNKNOWN'}
      </span>
    )
  }

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-logo">
            <img src="/shieldopsdarkmode.png" alt="ShieldOps" className="hero-logo-img" />
          </h1>
          <p className="hero-subtitle">
            Continuous security monitoring for your websites. OWASP Top-10 aligned 
            scanning, automated alerts, and comprehensive security reports.
          </p>
          
          {/* Quick Check Form */}
          <div className="quick-check-section">
            <h2>Check Your Website Security</h2>
            <form onSubmit={handleQuickCheckSubmit} className="quick-check-form">
              <input
                type="url"
                placeholder="https://yourwebsite.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="url-input"
                required
                disabled={isScanning}
              />
              <button type="submit" className="btn-scan" disabled={isScanning}>
                {isScanning ? (
                  'Scanning...'
                ) : (
                  <>
                    <FiSearch /> Scan Now
                  </>
                )}
              </button>
            </form>
            {error && (
              <div className="quick-check-error">
                {error}
              </div>
            )}
            <p className="quick-check-note">
              {isAuthenticated 
                ? 'Free instant security scan. Your websites will be saved to your account.'
                : 'Free instant security scan. Try it now - no signup required! Sign up to save your results.'}
            </p>
          </div>

          {/* Demo Results Modal */}
          {showResults && demoResults && (
            <div className="demo-results-modal-overlay" onClick={() => setShowResults(false)}>
              <div className="demo-results-modal" onClick={(e) => e.stopPropagation()}>
                <div className="demo-results-header">
                  <h2>
                    <FiLock /> Security Scan Results
                  </h2>
                  <button 
                    className="demo-results-close" 
                    onClick={() => setShowResults(false)}
                    aria-label="Close"
                  >
                    <FiX />
                  </button>
                </div>
                
                <div className="demo-results-content">
                  <div className="demo-scan-info">
                    <p className="demo-scan-url">Scanned: <strong>{url}</strong></p>
                    <p className="demo-scan-time">
                      Scanned at: {new Date(demoResults.scan_time).toLocaleString()}
                    </p>
                    <div className="demo-security-score">
                      <span className="demo-score-label">Security Score:</span>
                      <span className="demo-score-value" style={{
                        color: demoResults.security_score && demoResults.security_score >= 80 ? '#27ae60' : 
                               demoResults.security_score && demoResults.security_score >= 60 ? '#f39c12' : '#e74c3c'
                      }}>
                        {demoResults.security_score || 0}%
                      </span>
                    </div>
                  </div>

                  <div className="demo-summary-cards">
                    <div className="demo-summary-card">
                      <div className="demo-summary-value">{demoResults.total_issues}</div>
                      <div className="demo-summary-label">Total Issues</div>
                    </div>
                    <div className="demo-summary-card high">
                      <div className="demo-summary-value">{demoResults.high_issues}</div>
                      <div className="demo-summary-label">High Priority</div>
                    </div>
                    <div className="demo-summary-card medium">
                      <div className="demo-summary-value">{demoResults.medium_issues}</div>
                      <div className="demo-summary-label">Medium Priority</div>
                    </div>
                    <div className="demo-summary-card low">
                      <div className="demo-summary-value">{demoResults.low_issues}</div>
                      <div className="demo-summary-label">Low Priority</div>
                    </div>
                  </div>

                  {demoResults.issues && demoResults.issues.length > 0 ? (
                    <div className="demo-issues-section">
                      {(() => {
                        const grouped = groupIssuesByImpact(demoResults.issues)
                        return (
                          <>
                            {grouped.HIGH.length > 0 && (
                              <div className="demo-issues-group">
                                <h3 className="demo-group-header high">
                                  <FiAlertCircle /> High Priority Issues ({grouped.HIGH.length})
                                </h3>
                                <div className="demo-issues-list">
                                  {grouped.HIGH.map((issue, idx) => (
                                    <div key={idx} className="demo-issue-card high">
                                      <div className="demo-issue-header">
                                        {getImpactBadge(issue.impact)}
                                        <h4>{issue.issue_type}</h4>
                                      </div>
                                      <p className="demo-issue-description">{issue.description}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {grouped.MEDIUM.length > 0 && (
                              <div className="demo-issues-group">
                                <h3 className="demo-group-header medium">
                                  <FiAlertTriangle /> Medium Priority Issues ({grouped.MEDIUM.length})
                                </h3>
                                <div className="demo-issues-list">
                                  {grouped.MEDIUM.map((issue, idx) => (
                                    <div key={idx} className="demo-issue-card medium">
                                      <div className="demo-issue-header">
                                        {getImpactBadge(issue.impact)}
                                        <h4>{issue.issue_type}</h4>
                                      </div>
                                      <p className="demo-issue-description">{issue.description}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {grouped.LOW.length > 0 && (
                              <div className="demo-issues-group">
                                <h3 className="demo-group-header low">
                                  <FiInfo /> Low Priority Issues ({grouped.LOW.length})
                                </h3>
                                <div className="demo-issues-list">
                                  {grouped.LOW.map((issue, idx) => (
                                    <div key={idx} className="demo-issue-card low">
                                      <div className="demo-issue-header">
                                        {getImpactBadge(issue.impact)}
                                        <h4>{issue.issue_type}</h4>
                                      </div>
                                      <p className="demo-issue-description">{issue.description}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </>
                        )
                      })()}
                    </div>
                  ) : (
                    <div className="demo-no-issues">
                      <FiCheck className="demo-success-icon" />
                      <h3>No Security Issues Found!</h3>
                      <p>Great job! This website appears to be secure.</p>
                    </div>
                  )}

                  <div className="demo-cta-section">
                    <p className="demo-cta-text">
                      <strong>Want to save these results and monitor your website continuously?</strong>
                    </p>
                    <div className="demo-cta-buttons">
                      <Link to="/signup" className="btn btn-primary" onClick={() => setShowResults(false)}>
                        Sign Up Free
                      </Link>
                      <Link to="/login" className="btn btn-secondary" onClick={() => setShowResults(false)}>
                        Sign In
                      </Link>
                    </div>
                    <p className="demo-note">
                      Demo results are not saved. Sign up to track security over time and get alerts.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="hero-cta">
            <Link to="/signup" className="btn btn-primary">
              Get Started Free
            </Link>
            <Link to="/login" className="btn btn-secondary">
              Sign In
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="page-container">
        <div className="features-section">
          <h2>Why Choose ShieldOps?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <FiShield />
              </div>
              <h3>OWASP Top-10 Aligned</h3>
              <p>
                Automated security scanning aligned with OWASP Top-10 standards. 
                Detect vulnerabilities before they become threats.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <FiZap />
              </div>
              <h3>Quick & Deep Scanning</h3>
              <p>
                Quick scans provide instant results in seconds. Deep scans (OWASP ZAP) 
                offer comprehensive analysis with spider crawling and active testing.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <FiBarChart2 />
              </div>
              <h3>Continuous Monitoring</h3>
              <p>
                Monitor multiple websites 24/7. Get automated alerts when 
                security issues are detected.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <FiFileText />
              </div>
              <h3>Audit-Ready Reports</h3>
              <p>
                Generate comprehensive security reports for compliance, 
                audits, and stakeholder reviews.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <FiBell />
              </div>
              <h3>Automated Alerts</h3>
              <p>
                Receive instant notifications via Slack and email when 
                high-priority security issues are detected.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <FiGlobe />
              </div>
              <h3>Multi-Environment</h3>
              <p>
                Monitor production, staging, and development environments. 
                Track security across your entire infrastructure.
              </p>
            </div>
          </div>
        </div>

        {/* What We Check */}
        <div className="checks-section">
          <h2>What We Check</h2>
          <div className="scan-types-intro">
            <p>
              We offer two types of security scans to meet different needs:
            </p>
          </div>
          <div className="scan-types-comparison">
            <div className="scan-type-comparison-card">
              <h3>
                <FiShield /> Quick Scan
              </h3>
              <p className="scan-duration">~10-30 seconds</p>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>HTTPS & TLS Encryption</strong>
                  <p>TLS version, certificate validity, weak ciphers</p>
                </div>
              </div>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>Security Headers</strong>
                  <p>CSP, HSTS, X-Frame-Options, X-XSS-Protection, and more</p>
                </div>
              </div>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>Cookie Security</strong>
                  <p>HttpOnly, Secure, SameSite attributes</p>
                </div>
              </div>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>Server Configuration</strong>
                  <p>Server disclosure, information leakage</p>
                </div>
              </div>
            </div>
            <div className="scan-type-comparison-card deep">
              <h3>
                <FiZap /> Deep Scan (OWASP ZAP)
              </h3>
              <p className="scan-duration">~2-5 minutes</p>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>Everything in Quick Scan, plus:</strong>
                </div>
              </div>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>Spider Crawling</strong>
                  <p>Discovers all pages, endpoints, and links</p>
                </div>
              </div>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>Active Vulnerability Testing</strong>
                  <p>OWASP Top-10 aligned security testing on all discovered pages</p>
                </div>
              </div>
              <div className="check-item">
                <span className="check-icon">
                  <FiCheck />
                </span>
                <div>
                  <strong>Comprehensive Coverage</strong>
                  <p>Tests entire application, not just the homepage</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="how-it-works">
          <h2>How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Add Your Website</h3>
              <p>Enter your website URL. No installation required.</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Choose Scan Type</h3>
              <p>Select Quick Scan for instant results or Deep Scan (OWASP ZAP) for comprehensive analysis.</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Get Results</h3>
              <p>View detailed security report with prioritized issues.</p>
            </div>
            <div className="step">
              <div className="step-number">4</div>
              <h3>Monitor & Alert</h3>
              <p>Set up continuous monitoring and get alerts on new issues.</p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="cta-section">
          <h2>Ready to Secure Your Websites?</h2>
          <p>Join thousands of companies monitoring their security with our platform.</p>
          <div className="cta-buttons">
            <Link to="/signup" className="btn btn-primary btn-large">
              Start Free Trial
            </Link>
            <Link to="/dashboard" className="btn btn-secondary btn-large">
              View Demo
            </Link>
          </div>
          <SecurityBadge />
        </div>
      </div>
    </div>
  )
}

export default LandingPage

