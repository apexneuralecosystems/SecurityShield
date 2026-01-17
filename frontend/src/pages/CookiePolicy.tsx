import { FiShield } from 'react-icons/fi'
import './LegalPage.css'

function CookiePolicy() {
  return (
    <div className="legal-page">
      <div className="page-container">
        <div className="legal-header">
          <h1>
            <FiShield /> Cookie Policy
          </h1>
          <p className="last-updated">Last Updated: 15-Dec-2025</p>
        </div>

        <div className="legal-content">
          <p className="intro">
            This page explains how the Platform uses cookies and similar technologies. "Cookies" are small text files stored on your device by your browser.
          </p>

          <section>
            <h2>1. How the Platform Handles Sessions</h2>
            <p>The Platform primarily uses browser storage (for example, localStorage) to store authentication tokens for logged-in sessions, rather than relying on cookies for authentication.</p>
          </section>

          <section>
            <h2>2. Cookies We Use</h2>
            <p>The Platform does not intentionally set advertising cookies. Depending on how the Platform is hosted and delivered, your browser or our infrastructure providers may set limited, essential cookies required for basic functionality (for example, load balancing or security protections).</p>
          </section>

          <section>
            <h2>3. Managing Cookies</h2>
            <p>You can control and delete cookies through your browser settings. If you disable cookies entirely, some parts of the Platform may not function as intended.</p>
          </section>

          <section>
            <h2>4. Updates</h2>
            <p>We may update this Cookie Policy from time to time. If we introduce optional analytics or other non-essential cookies, we will provide notice and choices where required by law.</p>
          </section>
        </div>
      </div>
    </div>
  )
}

export default CookiePolicy

