import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FiLock, FiHome, FiShield, FiZap, FiFileText, FiBell } from 'react-icons/fi'
import { authAPI } from '../services/api'
import './Auth.css'

function Signup() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)
    try {
      await authAPI.signup({
        email: formData.email,
        full_name: formData.name,
        password: formData.password
      })
      // After signup, automatically log in
      await authAPI.login({
        email: formData.email,
        password: formData.password
      })
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Signup failed. Please try again.')
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
            <h2>Start Securing Your Websites Today</h2>
            <p>
              Join ShieldOps and get comprehensive security monitoring, automated 
              vulnerability detection, and real-time alerts for your web applications.
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
                <FiFileText />
                <span>Audit-Ready Compliance Reports</span>
              </li>
              <li>
                <FiBell />
                <span>Automated Alerts via Email & Slack</span>
              </li>
            </ul>
          </div>
        </div>
        <div className="auth-form-section">
          <div className="auth-container">
            <div className="auth-header">
              <h1>
                <FiLock /> Create Your Account
              </h1>
              <p>Start monitoring your websites' security today</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                  placeholder="John Doe"
                />
              </div>

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
                  placeholder="At least 8 characters"
                  minLength={8}
                />
              </div>

              <div className="form-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                  required
                  placeholder="Re-enter your password"
                />
              </div>

              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? 'Creating Account...' : 'Create Account'}
              </button>
            </form>

            <div className="auth-footer">
              <p>Already have an account? <Link to="/login">Sign in</Link></p>
              <p className="terms">
                By signing up, you agree to our Terms of Service and Privacy Policy
              </p>
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

export default Signup

