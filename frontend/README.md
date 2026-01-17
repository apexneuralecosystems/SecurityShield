# Security Platform - React Frontend

Modern React frontend for the Advanced Security Platform - a SaaS product for website security monitoring.

## Features

- 📊 **Dashboard** - Real-time security status and metrics
- 🏠 **Landing Page** - Product marketing with quick scan
- 🔒 **Security Page** - Detailed security information
- 👤 **User Authentication** - Sign up and login
- 🌐 **Website Management** - Add, monitor, and remove websites
- ⚡ **Instant Scanning** - Quick security scans without signup
- 📱 **Responsive Design** - Works on all devices
- 🔄 **API Integration** - Fully connected to FastAPI backend

## Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- FastAPI backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Frontend will be available at http://localhost:3000

### Production Build

```bash
npm run build
```

Output will be in `dist/` directory.

## Configuration

### API Connection

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

The frontend will automatically connect to the backend API.

## API Endpoints Used

### Websites
- `POST /api/v1/websites` - Create website
- `GET /api/v1/websites` - List websites
- `GET /api/v1/websites/{id}` - Get website
- `PUT /api/v1/websites/{id}` - Update website
- `DELETE /api/v1/websites/{id}` - Delete website

### Scans
- `POST /api/v1/scans` - Create scan
- `GET /api/v1/scans` - List scans
- `GET /api/v1/scans/{id}` - Get scan details
- `GET /api/v1/scans/latest/{website_id}` - Latest scan

### Summary
- `GET /api/v1/summary` - Security summary
- `GET /api/v1/landing-page-data` - Landing page data

## User Flow

1. **Landing Page** → Enter URL → Quick scan (no signup)
2. **Dashboard** → Add websites → Monitor security
3. **Sign Up** → Create account → Manage websites

## Pages

### `/` - Landing Page
- Hero section with quick scan form
- Product features showcase
- "How It Works" section
- Call-to-action buttons

### `/dashboard` - Security Dashboard
- Add websites to monitor
- View security statistics
- Website status list
- Remove websites

### `/security` - Security Information
- Complete security program overview
- Feature details
- Process explanation
- Responsible disclosure

### `/signup` - User Registration
- Create new account
- Form validation

### `/login` - User Login
- Sign in to account
- Remember me option

## Components

- `Layout` - Navigation and footer
- `SecurityBadge` - Security badge component
- `StatCard` - Statistics display card
- `WebsiteStatusList` - List of websites with status

## API Service

The `services/api.js` file contains all API methods:

- `createWebsite()` - Add new website
- `createScan()` - Trigger security scan
- `addWebsiteAndScan()` - Combined operation
- `getWebsites()` - List all websites
- `getLandingPageData()` - Get dashboard data
- And more...

## Error Handling

The frontend includes comprehensive error handling:
- API connection errors
- Validation errors
- User-friendly error messages
- Automatic retry for failed requests

## Deployment

### Option 1: Static Hosting

Build and deploy the `dist/` folder to:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

### Option 2: Serve with Backend

Copy `dist/` contents to your FastAPI static files directory.

### Option 3: Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

## Development Notes

- Uses Vite for fast development
- React Router for navigation
- Axios for API calls with interceptors
- CSS modules for styling
- Responsive design with mobile support
- Error boundaries and loading states

## Troubleshooting

### API Connection Issues

1. Ensure FastAPI backend is running on port 8000
2. Check `VITE_API_URL` in `.env`
3. Verify CORS is configured in backend
4. Check browser console for errors

### CORS Issues

The backend should have CORS configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

- [ ] Add user authentication API integration
- [ ] Add real-time scan status updates
- [ ] Add scan history view
- [ ] Add issue detail pages
- [ ] Add export functionality
- [ ] Add notifications system
