import { FiFileText, FiHome, FiMail, FiShield, FiUsers } from 'react-icons/fi'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ReactNode } from 'react'
import { authAPI } from '../services/api'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const isAuthenticated = authAPI.isAuthenticated()
  const user = authAPI.getStoredUser()

  const handleLogout = () => {
    authAPI.logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-logo">
            <img src="/shieldopsdarkmode.png" alt="ShieldOps" className="logo-img" />
          </Link>
          <div className="nav-links">
            <Link 
              to="/" 
              className={location.pathname === '/' ? 'active' : ''}
            >
              Home
            </Link>
            {isAuthenticated && (
              <Link 
                to="/dashboard" 
                className={location.pathname === '/dashboard' ? 'active' : ''}
              >
                Dashboard
              </Link>
            )}
            <Link 
              to="/security" 
              className={location.pathname === '/security' ? 'active' : ''}
            >
              Features
            </Link>
            {isAuthenticated ? (
              <>
                <span className="nav-user">{user?.email || 'User'}</span>
                <button onClick={handleLogout} className="btn-nav-logout">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  className={location.pathname === '/login' ? 'active' : ''}
                >
                  Sign In
                </Link>
                <Link 
                  to="/signup" 
                  className="btn-nav-signup"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
      <main className="main-content">
        {children}
      </main>
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section footer-brand">
            <div className="footer-logo">
              <img src="/shieldopsdarkmode.png" alt="ShieldOps" className="footer-logo-img" />
            </div>
            <p className="footer-description">
              OWASP Top-10 aligned security scanning for your websites. 
              Continuous monitoring, automated alerts, and comprehensive security reports.
            </p>
            <div className="footer-badge">
              <FiShield />
              <span>OWASP-Aligned Security</span>
            </div>
          </div>
          
          <div className="footer-section">
            <h4>
              <FiHome /> Quick Links
            </h4>
            <ul className="footer-links">
              <li><Link to="/">Home</Link></li>
              {isAuthenticated && <li><Link to="/dashboard">Dashboard</Link></li>}
              <li><Link to="/security">Security & Features</Link></li>
              {!isAuthenticated && (
                <>
                  <li><Link to="/login">Sign In</Link></li>
                  <li><Link to="/signup">Get Started</Link></li>
                </>
              )}
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>
              <FiFileText /> Resources
            </h4>
            <ul className="footer-links">
              <li><Link to="/security">Security Features</Link></li>
              <li><Link to="/security#process">Security Process</Link></li>
              <li><Link to="/security#compliance">Compliance</Link></li>
              <li><Link to="/security#contact">Report Security Issue</Link></li>
              {/* <li><Link to="/documentation">Documentation</Link></li> */}
              {/* <li><Link to="/api-docs">API Documentation</Link></li> */}
              {/* <li><Link to="/blog">Blog</Link></li> */}
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>
              <FiUsers /> Support
            </h4>
            <ul className="footer-links">
              <li>
                <a href="mailto:security@apexneural.com" className="footer-contact">
                  <FiMail /> security@apexneural.com
                </a>
              </li>
              <li>
                <a href="mailto:support@apexneural.com" className="footer-contact">
                  <FiMail /> support@apexneural.com
                </a>
              </li>
              {isAuthenticated && (
                <li><Link to="/dashboard">My Dashboard</Link></li>
              )}
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p className="footer-copyright">
              © 2026 ShieldOps. All rights reserved.
            </p>
            <div className="footer-legal">
              <Link to="/terms">Terms of Use</Link>
              <span className="footer-separator">•</span>
              <Link to="/privacy">Privacy Policy</Link>
              <span className="footer-separator">•</span>
              <Link to="/cookies">Cookie Policy</Link>
              <span className="footer-separator">•</span>
              <Link to="/security#contact">Security</Link>
              {/* <span className="footer-separator">•</span> */}
              {/* <Link to="/about">About Us</Link> */}
              {/* <span className="footer-separator">•</span> */}
              {/* <Link to="/contact">Contact</Link> */}
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout

