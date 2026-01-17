import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token refresh state to prevent multiple simultaneous refresh requests
let isRefreshing = false
interface QueuedRequest {
  resolve: (token: string | null) => void
  reject: (error: Error) => void
}
let failedQueue: QueuedRequest[] = []

const processQueue = (error: Error | null, token: string | null = null): void => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Try to get token from localStorage first, then from cookies
    let token = localStorage.getItem('access_token')
    if (!token) {
      // Try to get from cookies (for httpOnly cookies, this won't work in JS, but we try)
      const cookies = document.cookie.split(';')
      const accessTokenCookie = cookies.find(c => c.trim().startsWith('access_token='))
      if (accessTokenCookie) {
        token = accessTokenCookie.split('=')[1]
      }
    }
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Include credentials for cookies
    config.withCredentials = true
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling and automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
    
    // If unauthorized and not already retrying, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      const isLandingPageData = originalRequest?.url?.includes('/landing-page-data')
      const isAuthEndpoint = originalRequest?.url?.includes('/auth/login') || 
                            originalRequest?.url?.includes('/auth/signup') ||
                            originalRequest?.url?.includes('/auth/refresh')
      
      // Don't try to refresh for auth endpoints or landing page data
      if (isAuthEndpoint || isLandingPageData) {
        if (!isLandingPageData) {
          // Clear tokens for auth endpoints
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
        }
        throw new Error((error.response?.data as any)?.detail || (error.response?.data as any)?.message || 'An error occurred')
      }
      
      // Try to refresh token
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return api(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token') || 
                            document.cookie.split(';').find(c => c.trim().startsWith('refresh_token='))?.split('=')[1]
        
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }
        
        const response = await api.post(
          '/auth/refresh',
          { refresh_token: refreshToken },
          { withCredentials: true }
        )
        
        const { access_token, refresh_token: new_refresh_token } = response.data as { access_token: string; refresh_token?: string }
        
        // Store new tokens
        localStorage.setItem('access_token', access_token)
        if (new_refresh_token) {
          localStorage.setItem('refresh_token', new_refresh_token)
        }
        
        // Update original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        
        // Process queued requests
        processQueue(null, access_token)
        isRefreshing = false
        
        // Retry original request
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        processQueue(refreshError as Error, null)
        isRefreshing = false
        
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        
        const isAuthPage = window.location.pathname.includes('/login') || 
                          window.location.pathname.includes('/signup') ||
                          window.location.pathname.includes('/forgot-password') ||
                          window.location.pathname.includes('/reset-password')
        
        if (!isAuthPage) {
          window.location.href = '/login'
        }
        
        throw new Error('Session expired. Please login again.')
      }
    }
    
    // Handle other errors
    if (error.response) {
      throw new Error((error.response.data as any)?.detail || (error.response.data as any)?.message || 'An error occurred')
    } else if (error.request) {
      throw new Error('Unable to connect to server. Please check if the API is running.')
    } else {
      throw new Error(error.message || 'An unexpected error occurred')
    }
  }
)

// Type definitions
interface User {
  id: number
  email: string
  full_name?: string
  is_active?: boolean
  created_at?: string
}

interface LoginResponse {
  access_token: string
  refresh_token?: string
  user: User
}

interface SignupData {
  email: string
  password: string
  full_name?: string
}

interface LoginCredentials {
  email: string
  password: string
}

interface Website {
  id: number
  url: string
  name: string
  description?: string
  user_id?: number
  created_at?: string
  updated_at?: string
}

interface WebsiteData {
  url: string
  name: string
  description?: string
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
  scan_type: string
  status: string
  scan_time?: string
  total_issues?: number
  high_issues?: number
  medium_issues?: number
  low_issues?: number
  security_score?: number
  owasp_aligned?: boolean
  zap_results?: ZapScanResult
  created_at?: string
}

interface ScanData {
  website_id: number
  scan_type?: string
}

interface Issue {
  id: number
  scan_id: number
  website_id: number
  issue_type: string
  severity: string
  description: string
  status?: string
  created_at?: string
}

interface IssueUpdate {
  status?: string
  notes?: string
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
  issues: Array<{
    impact: string
    issue_type: string
    description: string
  }>
  scan_type: string
  is_demo: boolean
}

export const authAPI = {
  // ========== Authentication Endpoints ==========
  
  // Sign up
  signup: async (userData: SignupData): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/signup', userData)
    return response.data
  },

  // Login
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', credentials, { withCredentials: true })
    // Store tokens and user info
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token)
      }
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  // Logout
  logout: async (): Promise<void> => {
    try {
      // Call logout endpoint to invalidate session
      await api.post('/auth/logout', {}, { withCredentials: true })
    } catch (error) {
      // Even if logout fails, clear local storage
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  // Forgot password
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/forgot-password', { email })
    return response.data
  },

  // Reset password
  resetPassword: async (token: string, newPassword: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/reset-password', {
      token,
      new_password: newPassword
    })
    return response.data
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return !!(localStorage.getItem('access_token') || 
              document.cookie.split(';').some(c => c.trim().startsWith('access_token=')))
  },
  
  // Refresh access token
  refreshToken: async (): Promise<{ access_token: string; refresh_token?: string }> => {
    const refreshToken = localStorage.getItem('refresh_token') || 
                         document.cookie.split(';').find(c => c.trim().startsWith('refresh_token='))?.split('=')[1]
    
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }
    
    const response = await api.post<{ access_token: string; refresh_token?: string }>('/auth/refresh', 
      { refresh_token: refreshToken },
      { withCredentials: true }
    )
    
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token)
      }
    }
    
    return response.data
  },

  // Get stored user
  getStoredUser: (): User | null => {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }
}

export const securityAPI = {
  // ========== Website Endpoints ==========
  
  // Create a new website
  createWebsite: async (websiteData: WebsiteData): Promise<Website> => {
    const response = await api.post<Website>('/websites', websiteData)
    return response.data
  },

  // Get all websites
  getWebsites: async (params: Record<string, any> = {}): Promise<Website[]> => {
    const response = await api.get<Website[]>('/websites', { params })
    return response.data
  },

  // Get website by ID
  getWebsite: async (id: number): Promise<Website> => {
    const response = await api.get<Website>(`/websites/${id}`)
    return response.data
  },

  // Update website
  updateWebsite: async (id: number, updateData: Partial<WebsiteData>): Promise<Website> => {
    const response = await api.put<Website>(`/websites/${id}`, updateData)
    return response.data
  },

  // Delete website
  deleteWebsite: async (id: number): Promise<boolean> => {
    await api.delete(`/websites/${id}`)
    return true
  },

  // ========== Scan Endpoints ==========

  // Create a new scan
  createScan: async (scanData: ScanData): Promise<Scan> => {
    const response = await api.post<Scan>('/scans', scanData)
    return response.data
  },

  // Get all scans
  getScans: async (params: Record<string, any> = {}): Promise<Scan[]> => {
    const response = await api.get<Scan[]>('/scans', { params })
    return response.data
  },

  // Get scan by ID
  getScan: async (id: number): Promise<Scan> => {
    const response = await api.get<Scan>(`/scans/${id}`)
    return response.data
  },

  // Get latest scan for website
  getLatestScan: async (websiteId: number): Promise<Scan> => {
    const response = await api.get<Scan>(`/scans/latest/${websiteId}`)
    return response.data
  },

  // ========== Issue Endpoints ==========

  // Get all issues
  getIssues: async (params: Record<string, any> = {}): Promise<Issue[]> => {
    const response = await api.get<Issue[]>('/issues', { params })
    return response.data
  },

  // Update issue
  updateIssue: async (id: number, updateData: IssueUpdate): Promise<Issue> => {
    const response = await api.put<Issue>(`/issues/${id}`, updateData)
    return response.data
  },

  // ========== Summary Endpoints ==========

  // Get security summary
  getSummary: async (): Promise<any> => {
    const response = await api.get('/summary')
    return response.data
  },

  // Get landing page data
  getLandingPageData: async (): Promise<any> => {
    const response = await api.get('/landing-page-data')
    return response.data
  },

  // ========== ZAP Status Endpoint ==========

  // Get ZAP scanner status
  getZapStatus: async (): Promise<{
    enabled: boolean
    available: boolean
    url: string | null
    version: string | null
    error?: string
  }> => {
    const response = await api.get('/zap/status')
    return response.data
  },

  // ========== Combined Operations ==========

  // Add website and trigger scan (convenience method)
  addWebsiteAndScan: async (url: string, scanType: string = 'quick'): Promise<{ website: Website; scan: Scan }> => {
    // Normalize URL
    let normalizedUrl = url.trim()
    if (!normalizedUrl.startsWith('http://') && !normalizedUrl.startsWith('https://')) {
      normalizedUrl = 'https://' + normalizedUrl
    }

    try {
      // Extract name from URL
      const urlObj = new URL(normalizedUrl)
      const name = urlObj.hostname.replace('www.', '')

      // Create website
      const website = await securityAPI.createWebsite({
        url: normalizedUrl,
        name: name,
        description: `Website added via quick scan`
      })

      // Trigger scan
      const scan = await securityAPI.createScan({
        website_id: website.id,
        scan_type: scanType
      })

      return { website, scan }
    } catch (error: any) {
      // If website already exists, try to get it and create scan
      if (error.message?.includes('already exists')) {
        // Get all websites and find the one with matching URL
        const websites = await securityAPI.getWebsites()
        const existingWebsite = websites.find(
          w => w.url === normalizedUrl || 
               w.url === normalizedUrl + '/' || 
               w.url === normalizedUrl.replace(/\/$/, '')
        )
        
        if (existingWebsite) {
          const scan = await securityAPI.createScan({
            website_id: existingWebsite.id,
            scan_type: scanType
          })
          return { website: existingWebsite, scan }
        }
      }
      throw error
    }
  },

  // ========== Demo Scan (Public, No Auth Required) ==========
  
  // Demo scan - allows users to try scanning without authentication
  demoScan: async (url: string): Promise<DemoScanResponse> => {
    // Create a separate axios instance without auth interceptors for demo scans
    const demoApi = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: false, // No cookies needed for demo
    })
    
    const response = await demoApi.post<DemoScanResponse>('/demo/scan', { url })
    return response.data
  },
}

export default api

