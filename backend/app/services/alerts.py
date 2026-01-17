"""Alerting service for security issues"""
import os
import requests
from typing import Dict
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings


def count_critical(results: dict) -> int:
    """Count HIGH severity issues - matches security.py count_critical() exactly"""
    count = 0
    for site in results.values():
        quick = site.get("scans", {}).get("quick", {})
        # Handle both dict format (from security.py) and tuple format (from scanner)
        issues = quick.get("issues", [])
        for issue in issues:
            # If it's a dict (from security.py format)
            if isinstance(issue, dict):
                if issue.get("impact") == "HIGH":
                    count += 1
            # If it's a tuple (from scanner service)
            elif isinstance(issue, (tuple, list)) and len(issue) >= 1:
                if issue[0] == "HIGH":
                    count += 1
        deep = site.get("scans", {}).get("deep", {})
        for risk, num in deep.get("risk_counts", {}).items():
            if risk == "High":
                count += num
    return count


def send_slack_alert(results: dict):
    """Send Slack alert for HIGH issues"""
    webhook = os.getenv("SLACK_WEBHOOK_URL") or settings.SLACK_WEBHOOK_URL
    if not webhook:
        return
    
    critical = count_critical(results)
    if critical == 0:
        return
    
    message = {
        "text": (
            f"🚨 *Security Alert*\n"
            f"*{critical} HIGH-risk issue(s) detected*\n\n"
            f"Immediate review recommended."
        )
    }
    
    try:
        requests.post(webhook, json=message, timeout=10)
        print("📣 Slack alert sent")
    except Exception as e:
        print(f"Slack alert failed: {e}")


def send_email_alert(results: dict):
    """Send email alert for HIGH issues"""
    api_key = os.getenv("SENDGRID_API_KEY") or settings.SENDGRID_API_KEY
    sender = os.getenv("ALERT_EMAIL_FROM") or settings.ALERT_EMAIL_FROM
    recipient = os.getenv("ALERT_EMAIL_TO") or settings.ALERT_EMAIL_TO
    
    if not all([api_key, sender, recipient]):
        return
    
    critical = count_critical(results)
    if critical == 0:
        return
    
    content = f"""
Security Alert

{critical} HIGH severity issue(s) were detected during the latest scan.

Please review the security report and remediate immediately.

This alert was generated automatically.
"""
    
    message = Mail(
        from_email=sender,
        to_emails=recipient,
        subject="🚨 Security Scan Alert – Action Required",
        plain_text_content=content
    )
    
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        print("📧 Email alert sent")
    except Exception as e:
        print(f"Email alert failed: {e}")

