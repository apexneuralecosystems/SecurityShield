# Cloudflare Security Headers Configuration

## Quick Setup (5 minutes)

### Option 1: Transform Rules (Recommended)

1. Go to **Cloudflare Dashboard** → Your Domain → **Rules** → **Transform Rules**
2. Create a new **Response Header Modification** rule
3. Add these headers:

```
Header name: Content-Security-Policy
Value: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https:; frame-ancestors 'self';

Header name: Strict-Transport-Security
Value: max-age=31536000; includeSubDomains; preload

Header name: X-Frame-Options
Value: SAMEORIGIN

Header name: X-Content-Type-Options
Value: nosniff

Header name: X-XSS-Protection
Value: 1; mode=block

Header name: Referrer-Policy
Value: strict-origin-when-cross-origin

Header name: Permissions-Policy
Value: geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()
```

### Option 2: Page Rules (Simpler, but less flexible)

1. Go to **Cloudflare Dashboard** → **Rules** → **Page Rules**
2. Create a rule for `*yourdomain.com/*`
3. Add **Response Headers**:
   - Same headers as above

### Option 3: Workers (Most Control)

Create a Cloudflare Worker to add headers:

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const response = await fetch(request)
  
  // Clone response to modify headers
  const newResponse = new Response(response.body, response)
  
  // Add security headers
  newResponse.headers.set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';")
  newResponse.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')
  newResponse.headers.set('X-Frame-Options', 'SAMEORIGIN')
  newResponse.headers.set('X-Content-Type-Options', 'nosniff')
  newResponse.headers.set('X-XSS-Protection', '1; mode=block')
  newResponse.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  newResponse.headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
  
  return newResponse
}
```

## Verification

After adding headers, verify with:

```bash
curl -I https://yourdomain.com | grep -i "content-security-policy\|strict-transport-security\|x-frame-options"
```

Or use online tools:
- https://securityheaders.com
- https://observatory.mozilla.org

## Expected Impact

After adding headers:
- **HIGH issues**: Drop from ~47 to ~10-15
- **Security score**: Jump from 17% to 50-70%
- **Scan time**: Same (headers are quick to check)

## Notes

- **CSP (Content-Security-Policy)**: May need adjustment based on your app's JavaScript/CSS sources
- **HSTS**: Only works on HTTPS sites
- **X-Frame-Options**: Use `SAMEORIGIN` if you embed your site in iframes
- All headers apply to **all subdomains** if using Cloudflare

