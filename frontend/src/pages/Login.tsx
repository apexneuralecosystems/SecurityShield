import { useState, useEffect } from 'react'
import { FiHome, FiLock, FiShield, FiZap, FiBarChart2 } from 'react-icons/fi'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { authAPI, securityAPI } from '../services/api'
import './Auth.css'

function Login() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Check if there's a redirect parameter
    const redirect = searchParams.get('redirect')
    const url = searchParams.get('url')
    if (redirect === 'scan' && url) {
      // User was trying to scan, show message
      setError('Please log in to scan websites')
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await authAPI.login({
        email: formData.email,
        password: formData.password
      })
      
      // Check if there's a redirect to scan
      const redirect = searchParams.get('redirect')
      const url = searchParams.get('url')
      
      if (redirect === 'scan' && url) {
        // User was trying to scan, do it now
        try {
          await securityAPI.addWebsiteAndScan(url, 'quick')
          navigate(`/dashboard?scan=${encodeURIComponent(url)}`)
        } catch (scanErr) {
          // If scan fails, just go to dashboard
          navigate('/dashboard')
        }
      } else {
        navigate('/dashboard')
      }
    } catch (err: any) {
      setError(err.message || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-logo">
        <Link to="/">
          <img src="/shieldopsdarkmode.png" alt="ShieldOps" />
        </Link>
      </div>
      <div className="auth-wrapper">
        <div className="auth-info-section">
          <div className="auth-info-content">
            <h2>Welcome Back to ShieldOps</h2>
            <p>
              Continuous security monitoring for your websites. OWASP Top-10 aligned 
              scanning, automated alerts, and comprehensive security reports.
            </p>
            <ul className="auth-features">
              <li>
                <FiShield />
                <span>OWASP Top-10 Aligned Security Scanning</span>
              </li>
              <li>
                <FiZap />
                <span>Instant Security Reports & Analysis</span>
              </li>
              <li>
                <FiBarChart2 />
                <span>24/7 Continuous Monitoring & Alerts</span>
              </li>
            </ul>
          </div>
        </div>
        <div className="auth-form-section">
          <div className="auth-container">
            <div className="auth-header">
              <h1>
                <FiLock /> Welcome Back
              </h1>
              <p>Sign in to your security dashboard</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                  placeholder="you@example.com"
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                  placeholder="Enter your password"
                />
              </div>

              <div className="form-options">
                <Link to="/forgot-password" className="forgot-link">
                  Forgot password?
                </Link>
              </div>

              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="auth-footer">
              <p>Don't have an account? <Link to="/signup">Sign up</Link></p>
              <Link to="/" className="home-link">
                <FiHome /> Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login

