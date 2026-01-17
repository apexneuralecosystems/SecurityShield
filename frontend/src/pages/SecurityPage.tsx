import {
  FiBarChart2,
  FiFileText,
  FiLock,
  FiMail,
  FiSearch,
  FiShield,
  FiUsers,
  FiZap
} from 'react-icons/fi'
import './SecurityPage.css'

function SecurityPage() {
  return (
    <div className="security-page">
      <div className="page-container">
        <div className="security-header">
          <h1>
            <FiLock /> Security & Reliability
          </h1>
          <p>
            Security is built into our infrastructure by design.
          </p>
        </div>

        <div className="intro-section">
          <p>
            All applications enforce HTTPS & TLS encryption, implement modern browser security controls, 
            and undergo continuous automated vulnerability scanning aligned with OWASP Top-10 standards. 
            We maintain audit-ready security reports, monitor multiple production environments, and support 
            responsible vulnerability disclosure.
          </p>
          <p style={{ marginTop: '20px' }}>
            All our platforms enforce HTTPS & TLS encryption and undergo continuous automated security 
            scanning aligned with OWASP Top-10 standards. Security findings are actively monitored, 
            tracked, and reviewed across multiple environments with audit-ready reporting and responsible 
            disclosure support.
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <FiLock />
            </div>
            <h3>HTTPS & TLS Encryption</h3>
            <ul>
              <li>HTTPS enforced across all platforms</li>
              <li>TLS version validation</li>
              <li>Certificate expiry monitoring</li>
              <li>Weak cipher detection</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FiShield />
            </div>
            <h3>Secure HTTP Headers</h3>
            <ul>
              <li>Content-Security-Policy (CSP)</li>
              <li>Strict-Transport-Security (HSTS)</li>
              <li>X-Frame-Options</li>
              <li>X-Content-Type-Options</li>
              <li>X-XSS-Protection</li>
              <li>Referrer-Policy</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FiSearch />
            </div>
            <h3>OWASP Top-10 Aligned</h3>
            <ul>
              <li>Automated security scanning</li>
              <li>Vulnerability detection</li>
              <li>Risk categorization</li>
              <li>OWASP ZAP integration</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FiBarChart2 />
            </div>
            <h3>Continuous Monitoring</h3>
            <ul>
              <li>Regular vulnerability detection</li>
              <li>Remediation tracking</li>
              <li>Multi-environment coverage</li>
              <li>Automated alerts</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FiFileText />
            </div>
            <h3>Audit & Reporting</h3>
            <ul>
              <li>Security reports generated</li>
              <li>Issue tracking & status</li>
              <li>Historical scan data</li>
              <li>Compliance documentation</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FiUsers />
            </div>
            <h3>Responsible Disclosure</h3>
            <ul>
              <li>Security contact defined</li>
              <li>Reporting guidelines</li>
              <li>Vulnerability handling process</li>
              <li>Coordinated disclosure support</li>
            </ul>
          </div>
        </div>

        <div className="scanning-types-section">
          <h2>Automated Security Scanning</h2>
          <p className="scanning-intro">
            We perform two types of security scans to provide comprehensive coverage:
          </p>
          <div className="scanning-types-grid">
            <div className="scanning-type-card">
              <h3>
                <FiShield /> Quick Scan
              </h3>
              <p className="scan-time">Fast surface-level security checks (~10-30 seconds)</p>
              <ul>
                <li>HTTPS/TLS validation and certificate checks</li>
                <li>Security headers verification (CSP, HSTS, X-Frame-Options, etc.)</li>
                <li>Cookie security analysis</li>
                <li>Basic server disclosure checks</li>
                <li>Main page/URL validation</li>
              </ul>
              <p className="scan-use-case">
                <strong>Best for:</strong> Regular monitoring, quick checks, and rapid feedback
              </p>
            </div>
            <div className="scanning-type-card deep-scan">
              <h3>
                <FiZap /> Deep Scan (OWASP ZAP)
              </h3>
              <p className="scan-time">Comprehensive analysis (2-5 minutes)</p>
              <ul>
                <li>Everything in Quick Scan, plus:</li>
                <li>Spider crawling to discover all pages and endpoints</li>
                <li>Active vulnerability testing using OWASP ZAP</li>
                <li>OWASP Top-10 aligned security testing</li>
                <li>Comprehensive coverage across entire applications</li>
                <li>Detailed vulnerability reports with remediation guidance</li>
              </ul>
              <p className="scan-use-case">
                <strong>Best for:</strong> Comprehensive audits, detailed security assessments, and thorough vulnerability discovery
              </p>
            </div>
          </div>
          <p className="scanning-note">
            Both scan types use OWASP-aligned tools and provide audit-ready security reports. 
            Deep scans provide more comprehensive coverage by discovering and testing all pages 
            and endpoints, while Quick scans offer rapid feedback on security configuration.
          </p>
        </div>

        <div className="process-section" id="process">
          <h2>Our Security Process</h2>
          <div className="process-steps">
            <div className="process-step">
              <h4>1. Automated Scanning</h4>
              <p>Regular automated scans using OWASP-aligned tools detect vulnerabilities across all platforms. We offer both Quick Scans for rapid feedback and Deep Scans (OWASP ZAP) for comprehensive analysis.</p>
            </div>
            <div className="process-step">
              <h4>2. Risk Assessment</h4>
              <p>Findings are categorized by severity (HIGH/MEDIUM/LOW) and prioritized for remediation.</p>
            </div>
            <div className="process-step">
              <h4>3. Alerting & Tracking</h4>
              <p>High-priority issues trigger immediate alerts. All issues are tracked until resolution.</p>
            </div>
            <div className="process-step">
              <h4>4. Remediation</h4>
              <p>Security team reviews and addresses findings with documented resolution tracking.</p>
            </div>
            <div className="process-step">
              <h4>5. Verification</h4>
              <p>Re-scans verify fixes and ensure issues are properly resolved.</p>
            </div>
            <div className="process-step">
              <h4>6. Reporting</h4>
              <p>Audit-ready reports document security posture for compliance and review.</p>
            </div>
          </div>
        </div>

        <div className="badge-section" id="compliance">
          <h2>Security Compliance</h2>
          <p>Our security program follows industry standards and best practices</p>
          <div className="security-badge-large">
            <span>
              <FiShield />
            </span>
            <span>
              <strong>OWASP-Aligned</strong><br />
              <small>Continuously Monitored</small>
            </span>
          </div>
        </div>

        <div className="contact-section" id="contact">
          <h2>Security & Responsible Disclosure</h2>
          <p className="security-serious">
            We take security seriously.
          </p>
          <p>
            If you discover a security vulnerability, please report it responsibly to:
          </p>
          <p className="security-contact">
            <strong>
              <FiMail /> <a href="mailto:security@apexneural.com">security@apexneural.com</a>
            </strong>
          </p>
          <div className="security-commitments">
            <h3>We commit to:</h3>
            <ul>
              <li>Acknowledging valid reports</li>
              <li>Investigating promptly</li>
              <li>Fixing confirmed issues</li>
            </ul>
          </div>
          <p className="contact-note">
            Please include a description of the vulnerability, steps to reproduce, potential impact, 
            and any suggested fix if available. We will acknowledge receipt within 48 hours and provide 
            updates on our investigation and remediation progress.
          </p>
        </div>
      </div>
    </div>
  )
}

export default SecurityPage

