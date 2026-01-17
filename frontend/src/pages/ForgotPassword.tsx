import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { FiLock, FiMail, FiHome, FiShield, FiZap, FiRefreshCw, FiCheckCircle } from 'react-icons/fi'
import { authAPI } from '../services/api'
import './Auth.css'

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [resendCountdown, setResendCountdown] = useState(0)
  const countdownIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Cleanup countdown interval on unmount
  useEffect(() => {
    return () => {
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current)
      }
    }
  }, [])

  // Countdown timer
  useEffect(() => {
    if (resendCountdown > 0) {
      countdownIntervalRef.current = setInterval(() => {
        setResendCountdown((prev) => {
          if (prev <= 1) {
            if (countdownIntervalRef.current) {
              clearInterval(countdownIntervalRef.current)
            }
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } else {
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current)
      }
    }

    return () => {
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current)
      }
    }
  }, [resendCountdown])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setLoading(true)

    try {
      const response = await authAPI.forgotPassword(email)
      setSuccess(true)
      // Start 60 second countdown for resend
      setResendCountdown(60)
    } catch (err: any) {
      setError(err.message || 'Failed to send reset email. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (resendCountdown > 0) {
      return
    }

    setError('')
    setLoading(true)

    try {
      const response = await authAPI.forgotPassword(email)
      setSuccess(true)
      // Restart 60 second countdown
      setResendCountdown(60)
    } catch (err: any) {
      setError(err.message || 'Failed to resend email. Please try again.')
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
            <h2>Reset Your Password</h2>
            <p>
              Don't worry! Enter your email address and we'll send you a secure 
              link to reset your password and regain access to your security dashboard.
            </p>
            <ul className="auth-features">
              <li>
                <FiShield />
                <span>Secure Password Reset Process</span>
              </li>
              <li>
                <FiZap />
                <span>Quick & Easy Account Recovery</span>
              </li>
              <li>
                <FiCheckCircle />
                <span>Email Link Valid for 1 Hour</span>
              </li>
            </ul>
          </div>
        </div>
        <div className="auth-form-section">
          <div className="auth-container">
            <div className="auth-header">
              <h1>
                <FiMail /> Reset Password
              </h1>
              <p>Enter your email to receive a password reset link</p>
            </div>

            {success ? (
              <div className="success-message">
                <div className="success-icon">
                  <FiCheckCircle />
                </div>
                <h3>Check Your Email</h3>
                <p>
                  If an account with <strong>{email}</strong> exists, we've sent a password reset link.
                </p>
                <p className="success-subtext">
                  Please check your inbox (and spam folder) and follow the instructions. 
                  The link will expire in 1 hour.
                </p>
                
                {resendCountdown > 0 ? (
                  <div className="resend-info">
                    <p>Didn't receive the email?</p>
                    <p className="countdown-text">
                      You can request another email in <strong>{resendCountdown}</strong> seconds
                    </p>
                  </div>
                ) : (
                  <button 
                    type="button" 
                    className="btn-resend" 
                    onClick={handleResend}
                    disabled={loading}
                  >
                    <FiRefreshCw /> {loading ? 'Sending...' : 'Resend Email'}
                  </button>
                )}

                <div className="success-actions">
                  <Link to="/login" className="btn-submit">
                    Back to Login
                  </Link>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="auth-form">
                {error && <div className="error-message">{error}</div>}
                
                <div className="form-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="you@example.com"
                    autoComplete="email"
                    disabled={loading}
                  />
                  <small className="form-hint">
                    Enter the email address associated with your account
                  </small>
                </div>

                <button 
                  type="submit" 
                  className="btn-submit" 
                  disabled={loading || !email}
                >
                  {loading ? (
                    <>
                      <FiRefreshCw className="spinning" /> Sending...
                    </>
                  ) : (
                    <>
                      <FiMail /> Send Reset Link
                    </>
                  )}
                </button>
              </form>
            )}

            <div className="auth-footer">
              <p>Remember your password? <Link to="/login">Sign in</Link></p>
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

export default ForgotPassword
