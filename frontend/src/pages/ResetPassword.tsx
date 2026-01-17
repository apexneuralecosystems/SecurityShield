import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { FiLock, FiHome, FiShield, FiCheck } from 'react-icons/fi'
import { authAPI } from '../services/api'
import './Auth.css'

function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [token, setToken] = useState('')

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (!tokenParam) {
      setError('Invalid reset link. Please request a new password reset.')
    } else {
      setToken(tokenParam)
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!token) {
      setError('Invalid reset token')
      return
    }

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
      await authAPI.resetPassword(token, formData.password)
      setSuccess(true)
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to reset password. The link may have expired.')
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
            <h2>Set Your New Password</h2>
            <p>
              Create a strong, secure password to protect your ShieldOps account. 
              Make sure it's at least 8 characters long and includes a mix of letters, 
              numbers, and special characters.
            </p>
            <ul className="auth-features">
              <li>
                <FiShield />
                <span>Secure Password Requirements</span>
              </li>
              <li>
                <FiCheck />
                <span>Instant Account Recovery</span>
              </li>
            </ul>
          </div>
        </div>
        <div className="auth-form-section">
          <div className="auth-container">
            <div className="auth-header">
              <h1>
                <FiLock /> Reset Password
              </h1>
              <p>Enter your new password</p>
            </div>

            {success ? (
              <div className="success-message">
                <p>Password has been reset successfully!</p>
                <p>Redirecting to login page...</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="auth-form">
                {error && <div className="error-message">{error}</div>}
                
                <div className="form-group">
                  <label>New Password</label>
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
                  <label>Confirm New Password</label>
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                    required
                    placeholder="Re-enter your password"
                    minLength={8}
                  />
                </div>

                <button type="submit" className="btn-submit" disabled={loading || !token}>
                  {loading ? 'Resetting...' : 'Reset Password'}
                </button>
              </form>
            )}

            <div className="auth-footer">
              <p>Remember your password? <Link to="/login">Sign in</Link></p>
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

export default ResetPassword

