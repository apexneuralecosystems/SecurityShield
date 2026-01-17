import { FiFileText, FiShield } from 'react-icons/fi'
import './LegalPage.css'

function TermsOfUse() {
  return (
    <div className="legal-page">
      <div className="page-container">
        <div className="legal-header">
          <h1>
            <FiFileText /> Terms of Use
          </h1>
          <p className="last-updated">Last Updated: 15-Dec-2025</p>
        </div>

        <div className="legal-content">
          <p className="intro">
            These Terms of Use ("Terms") govern your access to and use of this website, its related domains, subdomains, product-specific websites, mobile applications, APIs, dashboards, communications, and any related products and services operated by ApexNeural Private Limited ("ApexNeural", "we", "us", or "our") (collectively, the "Platform" or "Services").
          </p>

          <p className="intro">
            This website is owned and operated by ApexNeural Private Limited. All product websites, domains, and subdomains are properties of ApexNeural unless expressly stated otherwise.
          </p>

          <p className="intro">
            If you do not agree with these Terms or the applicable Privacy Policy available on this Website, you must not access or use the Platform.
          </p>

          <p className="intro">
            Accessing the Platform with or without creating an account constitutes your acceptance of these Terms.
          </p>

          <p className="intro">
            If you are accepting these Terms on behalf of a company or other legal entity, you represent that you are authorized to bind that entity. If you lack such authority, you must not access or use the Platform.
          </p>

          <section>
            <h2>1. Changes to Terms</h2>
            <p>We may revise these Terms at any time. Changes will be posted on the Platform, and the "Last Updated" date will be revised. Your continued use of the Platform following any update constitutes acceptance of the revised Terms.</p>
            <p>Your sole remedy if you do not agree with the revised Terms is to discontinue use of the Platform.</p>
          </section>

          <section>
            <h2>2. Description of Services</h2>
            <p>ApexNeural provides a web-based software platform for automated code analysis and end-to-end (E2E) testing workflows. The Services are designed to help users and teams upload or connect software projects, run automated analysis and test workflows, track execution status, and view, preview, and download generated reports and artifacts.</p>
            <p>Depending on the workflow you choose, the Platform may (a) analyze your codebase for potential issues, quality concerns, and improvement opportunities, (b) run automated E2E test executions, and (c) generate outputs such as reports, recommendations, summaries, and test results (including HTML/JSON/Markdown reports).</p>
            <p>You may be able to provide project inputs in different ways, including by uploading a ZIP file or providing a Git repository URL. The Platform may also provide dashboards and project pages to manage projects, initiate workflows, and monitor progress.</p>
            <p>The Platform may include automated and/or AI-assisted features. Generated outputs may be inaccurate, incomplete, or unsuitable for your specific use case, and must be independently reviewed before relying on them.</p>
            <p>The form, features, algorithms, and functionality of the Services may change or be discontinued at any time without prior notice.</p>
          </section>

          <section>
            <h2>3. Eligibility</h2>
            <p>You must be at least 18 years old and legally capable of entering into binding contracts to use the Platform. By using the Services, you represent that you meet this requirement.</p>
          </section>

          <section>
            <h2>4. User Accounts</h2>
            <p>You are responsible for maintaining the confidentiality of your login credentials and for activities occurring under your account. You must notify us immediately at <a href="mailto:info@apexneural.com">info@apexneural.com</a> of any unauthorized use.</p>
            <p>We are not responsible for any loss arising due to unauthorized access resulting from your failure to secure your account.</p>
          </section>

          <section>
            <h2>5. Acceptable Use and Prohibited Activities</h2>
            <p>You agree not to (and not to permit others to):</p>
            <ul>
              <li>use the Services for any illegal, unauthorized, harmful, or unethical purpose;</li>
              <li>upload, submit, or generate content that is defamatory, obscene, discriminatory, harmful, violates privacy, infringes intellectual property, or breaches any law;</li>
              <li>upload or use data without lawful rights, consents, or other valid legal basis as required under applicable laws, including the Digital Personal Data Protection Act, 2023 (India) and other relevant data protection laws;</li>
              <li>use the Services for high-risk activities such as autonomous weapons, medical or legal decision-making, critical infrastructure, scientific accuracy-critical systems, or applications requiring error-free outputs without independent verification;</li>
              <li>probe, scan, test vulnerability, breach or attempt to bypass security controls, rate limits, access restrictions, or authentication mechanisms;</li>
              <li>crawl, scrape, mine, or systematically copy data or outputs without explicit written consent;</li>
              <li>reverse-engineer, decompile, disassemble, reproduce, or attempt to derive source code, models, architecture, or underlying algorithms;</li>
              <li>resell, sublicense, rent, lease, white-label, or commercially exploit the Services without a separate written agreement;</li>
              <li>remove or alter any proprietary, copyright, or trademark notices;</li>
              <li>use the Services to generate deepfakes, discriminatory content, deceiving content, or misleading content intended to manipulate, harm, or defraud others.</li>
            </ul>
            <p>We may suspend or terminate your access immediately, with or without notice, for violation of this section.</p>
          </section>

          <section>
            <h2>6. User Content and Outputs</h2>
            <p><strong>User Content</strong> means any content (text, data, files, images, code, repositories, etc.) you submit to the Platform.</p>
            <ul>
              <li>You retain ownership of your User Content.</li>
              <li>By submitting User Content, you grant ApexNeural a worldwide, non-exclusive, royalty-free, irrevocable license to store, host, analyze, process, modify, adapt, aggregate, anonymize, distribute, and create derivative works from such User Content for the purposes of operating, delivering, securing, maintaining, analyzing, researching, developing, improving, and enhancing the Services, subject to applicable laws.</li>
              <li>You represent and warrant that you: (i) own or have lawful rights to upload User Content; and (ii) have obtained necessary consents, including for personal data uploaded.</li>
            </ul>
            <p><strong>Outputs</strong> means content generated by the Services in response to your inputs (for example, analysis summaries, recommendations, and test reports).</p>
            <ul>
              <li>Outputs are licensed (not owned) by you for personal or internal business use only, subject to these Terms. Outputs may not be unique and may resemble content generated for others. ApexNeural does not guarantee accuracy, reliability, or third-party rights relating to Outputs.</li>
              <li>You are solely responsible for: (i) use of Outputs, and (ii) verifying accuracy, legality, and suitability for intended use.</li>
            </ul>
            <p>ApexNeural may retain User Content for as long as reasonably necessary to fulfill the purposes outlined in these Terms, including operational, analytical, research, development, security, compliance, audit, and backup purposes. Aggregated or anonymized data that does not identify individuals may be retained indefinitely.</p>
          </section>

          <section>
            <h2>7. Intellectual Property</h2>
            <p>All rights, title, and interest in the Platform, Services, algorithms, trademarks, software, and technology (excluding User Content) belong exclusively to ApexNeural or licensors. No rights are granted to you other than those expressly stated in these Terms. No implied rights or licenses are granted.</p>
            <p>All websites, domains, subdomains, and product-specific platforms operated under the ApexNeural brand are the exclusive property of ApexNeural Private Limited.</p>
          </section>

          <section>
            <h2>8. Payments and Refunds</h2>
            <p>Certain features may be free; others may require payment. Taxes are additional unless expressly stated.</p>
            <p>Payments are non-refundable unless required by applicable law or explicitly stated.</p>
            <p>In the case of chargebacks, failed payments, or non-payment, ApexNeural may suspend account access immediately.</p>
          </section>

          <section>
            <h2>9. Privacy</h2>
            <p>ApexNeural processes personal data in accordance with the applicable Privacy Policy published on the respective website. By using the Platform, you acknowledge and consent to such processing in accordance with applicable laws.</p>
          </section>

          <section>
            <h2>10. Third-Party Links and Integrations</h2>
            <p>The Platform may contain links or integrations to third-party services. ApexNeural is not responsible for the content, privacy practices, or availability of such third-party services.</p>
          </section>

          <section>
            <h2>11. Termination</h2>
            <p>We may suspend or terminate your access with or without cause or notice.</p>
            <p>Upon termination, your right to use the Services ceases immediately.</p>
            <p>We may retain User Content and account information as required by law, fraud prevention, backup integrity, or audit purposes. Sections 5–17 survive termination.</p>
          </section>

          <section>
            <h2>12. Disclaimer</h2>
            <p className="disclaimer-text">
              THE PLATFORM AND SERVICES (INCLUDING OUTPUTS) ARE PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTY OF ANY KIND—EXPRESS, IMPLIED, OR STATUTORY—INCLUDING WARRANTIES OF ACCURACY, FITNESS, NON-INFRINGEMENT, MERCHANTABILITY, RELIABILITY, OR ERROR-FREE OPERATION.
            </p>
            <p className="disclaimer-text">
              OUTPUTS DO NOT CONSTITUTE PROFESSIONAL (LEGAL, MEDICAL, FINANCIAL, TECHNICAL, OR SCIENTIFIC) ADVICE AND SHOULD NOT BE USED WITHOUT INDEPENDENT VERIFICATION.
            </p>
          </section>

          <section>
            <h2>13. Limitation of Liability</h2>
            <p className="disclaimer-text">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, APEXNEURAL AND ITS DIRECTORS, OFFICERS, EMPLOYEES, AND AGENTS SHALL NOT BE LIABLE FOR ANY INDIRECT, SPECIAL, INCIDENTAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR LOSS OF PROFITS, DATA, REVENUE, OR BUSINESS.
            </p>
            <p>OUR TOTAL AGGREGATE LIABILITY RELATING TO THE PLATFORM OR THESE TERMS SHALL NOT EXCEED THE GREATER OF: (A) INR 30,000; OR (B) THE FEES PAID BY YOU IN THE 12 MONTHS PRECEDING THE CLAIM.</p>
            <p>This limitation does not apply to liability that cannot legally be excluded, including willful misconduct or fraud.</p>
          </section>

          <section>
            <h2>14. Indemnification</h2>
            <p>You agree to defend, indemnify, and hold harmless ApexNeural, its employees, directors, officers, and agents from any losses, liabilities, damages, penalties, or expenses (including reasonable attorney fees) arising from: (i) your use of the Services or Outputs, (ii) your breach of these Terms, or (iii) unlawful submission or misuse of personal data, confidential data, or third-party rights.</p>
          </section>

          <section>
            <h2>15. Governing Law & Dispute Resolution</h2>
            <p>These Terms are governed by the laws of India.</p>
            <p>Disputes shall first be attempted to be resolved amicably within 30 days.</p>
            <p>Failing resolution, disputes shall be referred to final and binding arbitration in Hyderabad, Telangana, under the Arbitration and Conciliation Act, 1996 by a sole arbitrator mutually appointed by the parties.</p>
            <p>If the parties fail to agree within 15 days, the arbitrator shall be appointed in accordance with the Act. The seat and venue of arbitration shall be Hyderabad, Telangana. Subject to arbitration, courts in Hyderabad shall have exclusive jurisdiction.</p>
          </section>

          <section>
            <h2>16. Miscellaneous</h2>
            <ul>
              <li><strong>Force Majeure:</strong> We are not liable for delayed performance caused by circumstances beyond our reasonable control.</li>
              <li><strong>Severability:</strong> If any provision is invalid, the remaining provisions remain in force.</li>
              <li><strong>No Waiver:</strong> Failure to enforce a right does not constitute a waiver.</li>
              <li><strong>Entire Agreement:</strong> These Terms and the Privacy Policy constitute the entire agreement between you and ApexNeural.</li>
            </ul>
          </section>

          <section>
            <h2>Contact</h2>
            <p>ApexNeural Private Limited<br />
            5th Floor, Shantha Sriram Building, PRS Towers,<br />
            Gachibowli, K.V. Rangareddy,<br />
            Telangana - 500032<br />
            Email: <a href="mailto:info@apexneural.com">info@apexneural.com</a></p>
          </section>
        </div>
      </div>
    </div>
  )
}

export default TermsOfUse

