import { Route, BrowserRouter as Router, Routes, Navigate } from 'react-router-dom'
import { ReactNode } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import LandingPage from './pages/LandingPage'
import SecurityPage from './pages/SecurityPage'
import WebsiteDetails from './pages/WebsiteDetails'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import PrivacyPolicy from './pages/PrivacyPolicy'
import TermsOfUse from './pages/TermsOfUse'
import CookiePolicy from './pages/CookiePolicy'
import { authAPI } from './services/api'

// Protected Route Component
interface ProtectedRouteProps {
  children: ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const isAuthenticated = authAPI.isAuthenticated()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/" element={<Layout><LandingPage /></Layout>} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Layout><Dashboard /></Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/security" 
          element={<Layout><SecurityPage /></Layout>} 
        />
        <Route 
          path="/website/:websiteId" 
          element={
            <ProtectedRoute>
              <Layout><WebsiteDetails /></Layout>
            </ProtectedRoute>
          } 
        />
        <Route path="/privacy" element={<Layout><PrivacyPolicy /></Layout>} />
        <Route path="/terms" element={<Layout><TermsOfUse /></Layout>} />
        <Route path="/cookies" element={<Layout><CookiePolicy /></Layout>} />
      </Routes>
    </Router>
  )
}

export default App

