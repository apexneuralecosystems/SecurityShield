"""Security scanning service - matches security.py SecurityPlatform.quick_scan() exactly"""
import requests
import ssl
import socket
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Security scanner for websites - matches SecurityPlatform.quick_scan() behavior exactly"""
    
    def __init__(self):
        self.timeout = 10
    
    def _check_tls(self, hostname: str, port: int = 443) -> List[Tuple[str, str, str]]:
        """Check TLS version and certificate validity - matches security.py exactly"""
        issues = []
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Check TLS version - matches security.py exactly
                    tls_version = ssock.version()
                    if tls_version in ("TLSv1", "TLSv1.1"):
                        issues.append(("HIGH", "Weak TLS Version", f"Using {tls_version} (should be TLSv1.2+)"))
                    
                    # Check certificate expiry - matches security.py exactly
                    cert = ssock.getpeercert()
                    if cert:
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (not_after - datetime.now()).days
                        if days_until_expiry < 30:
                            issues.append(("HIGH" if days_until_expiry < 7 else "MEDIUM",
                                         "Certificate Expiring Soon",
                                         f"Certificate expires in {days_until_expiry} days"))
        except Exception as e:
            issues.append(("MEDIUM", "TLS Check Failed", str(e)))
        return issues
    
    def quick_scan(self, url: str) -> Dict:
        """Perform quick security scan - matches security.py SecurityPlatform.quick_scan() exactly"""
        issues = []
        
        try:
            r = requests.get(url, timeout=self.timeout, allow_redirects=True)
            
            # HTTPS & TLS encryption enforced - matches security.py exactly
            if not url.startswith("https://"):
                issues.append(("HIGH", "No HTTPS", "Site does not enforce HTTPS"))
            else:
                # Extract hostname for TLS check
                parsed = urlparse(url)
                if parsed.hostname:
                    tls_issues = self._check_tls(parsed.hostname, parsed.port or 443)
                    issues.extend(tls_issues)
            
            # Secure HTTP headers implemented (CSP, HSTS, XFO, X-XSS-Protection, Referrer-Policy)
            # Matches security.py exactly
            headers = {
                "Content-Security-Policy": "HIGH",
                "Strict-Transport-Security": "HIGH",
                "X-Frame-Options": "HIGH",
                "X-Content-Type-Options": "MEDIUM",
                "X-XSS-Protection": "MEDIUM",
                "Referrer-Policy": "MEDIUM",
                "Permissions-Policy": "LOW"
            }
            
            for h, severity in headers.items():
                if h not in r.headers:
                    issues.append((severity, f"Missing {h}", f"{h} header not set"))
            
            # Cookie security - matches security.py exactly
            for c in r.cookies:
                if not c.secure:
                    issues.append(("MEDIUM", "Insecure Cookie", f"{c.name} missing Secure"))
                if not c.has_nonstandard_attr("HttpOnly"):
                    issues.append(("MEDIUM", "Cookie HttpOnly Missing", c.name))
                if not c.get_nonstandard_attr("SameSite"):
                    issues.append(("LOW", "Cookie SameSite Missing", c.name))
            
            # Server disclosure - matches security.py exactly
            if "Server" in r.headers:
                issues.append(("LOW", "Server Disclosure", r.headers["Server"]))
            
            # Return format matches security.py exactly
            return {
                "scan_time": datetime.now(),
                "status": "completed",
                "error_message": None,
                "total_issues": len(issues),
                "high_issues": sum(1 for i in issues if i[0] == "HIGH"),
                "medium_issues": sum(1 for i in issues if i[0] == "MEDIUM"),
                "low_issues": sum(1 for i in issues if i[0] == "LOW"),
                "security_score": max(0, 100 - (sum(1 for i in issues if i[0] == "HIGH") * 10) - 
                                     (sum(1 for i in issues if i[0] == "MEDIUM") * 5) - 
                                     (sum(1 for i in issues if i[0] == "LOW") * 1)),
                "owasp_aligned": True,
                "scan_data": {
                    "status_code": r.status_code,
                    "headers": dict(r.headers)
                },
                "issues": issues  # List of (severity, type, description) tuples for backend processing
            }
            
        except Exception as e:
            # Match security.py error handling exactly - returns {"error": str(e)}
            error_str = str(e)
            return {
                "scan_time": datetime.now(),
                "status": "failed",
                "error_message": error_str,
                "error": error_str,  # Also include 'error' key like security.py
                "total_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
                "security_score": 0,
                "owasp_aligned": True,
                "scan_data": {},
                "issues": []  # Empty issues on error
            }
    
    async def perform_deep_scan(self, url: str, use_zap: bool = False) -> Dict:
        """
        Perform a deep security scan combining quick scan with optional ZAP scan
        
        Args:
            url: Website URL to scan
            use_zap: Whether to include ZAP deep scanning
        
        Returns:
            Dict containing both quick scan and optional ZAP scan results
        """
        # Always perform quick scan
        quick_result = self.quick_scan(url)
        
        result = {
            "scan_time": datetime.now(),
            "status": quick_result.get("status", "completed"),
            "error_message": quick_result.get("error_message"),
            "quick_scan": quick_result,
            "zap_scan": None
        }
        
        # Add ZAP scan if requested and available
        if use_zap:
            try:
                from app.main import get_zap_scanner
                from app.core.config import settings
                
                zap_scanner = get_zap_scanner()
                
                if zap_scanner and zap_scanner.is_available():
                    logger.info(f"Performing ZAP deep scan for {url}")
                    zap_result = await zap_scanner.scan_website(
                        url=url,
                        spider_max_duration=settings.ZAP_SPIDER_MAX_DURATION,
                        scan_timeout=settings.ZAP_TIMEOUT
                    )
                    result["zap_scan"] = zap_result
                    
                    # Merge ZAP issues into total counts if scan was successful
                    if zap_result.get("success"):
                        zap_summary = zap_result.get("summary", {})
                        # Convert ZAP severity to our format and add to issues
                        zap_high = zap_summary.get("high", 0)
                        zap_medium = zap_summary.get("medium", 0)
                        zap_low = zap_summary.get("low", 0)
                        
                        # Update total counts
                        result["total_issues"] = quick_result.get("total_issues", 0) + zap_result.get("total_alerts", 0)
                        result["high_issues"] = quick_result.get("high_issues", 0) + zap_high
                        result["medium_issues"] = quick_result.get("medium_issues", 0) + zap_medium
                        result["low_issues"] = quick_result.get("low_issues", 0) + zap_low
                        
                        # Recalculate security score
                        result["security_score"] = max(0, 100 - 
                            (result["high_issues"] * 10) - 
                            (result["medium_issues"] * 5) - 
                            (result["low_issues"] * 1))
                    else:
                        logger.warning(f"ZAP scan failed for {url}: {zap_result.get('error')}")
                        # Use quick scan results only
                        result["total_issues"] = quick_result.get("total_issues", 0)
                        result["high_issues"] = quick_result.get("high_issues", 0)
                        result["medium_issues"] = quick_result.get("medium_issues", 0)
                        result["low_issues"] = quick_result.get("low_issues", 0)
                        result["security_score"] = quick_result.get("security_score", 0)
                else:
                    logger.warning("ZAP scanner requested but not available")
                    result["zap_scan"] = {
                        "success": False,
                        "error": "ZAP scanner is not available",
                        "total_alerts": 0,
                        "summary": {"high": 0, "medium": 0, "low": 0, "informational": 0}
                    }
                    # Use quick scan results only
                    result["total_issues"] = quick_result.get("total_issues", 0)
                    result["high_issues"] = quick_result.get("high_issues", 0)
                    result["medium_issues"] = quick_result.get("medium_issues", 0)
                    result["low_issues"] = quick_result.get("low_issues", 0)
                    result["security_score"] = quick_result.get("security_score", 0)
            except ImportError:
                logger.error("ZAP scanner module not available")
                result["zap_scan"] = {
                    "success": False,
                    "error": "ZAP scanner module not installed",
                    "total_alerts": 0,
                    "summary": {"high": 0, "medium": 0, "low": 0, "informational": 0}
                }
                result["total_issues"] = quick_result.get("total_issues", 0)
                result["high_issues"] = quick_result.get("high_issues", 0)
                result["medium_issues"] = quick_result.get("medium_issues", 0)
                result["low_issues"] = quick_result.get("low_issues", 0)
                result["security_score"] = quick_result.get("security_score", 0)
            except Exception as e:
                logger.error(f"Error during ZAP scan: {e}")
                result["zap_scan"] = {
                    "success": False,
                    "error": str(e),
                    "total_alerts": 0,
                    "summary": {"high": 0, "medium": 0, "low": 0, "informational": 0}
                }
                result["total_issues"] = quick_result.get("total_issues", 0)
                result["high_issues"] = quick_result.get("high_issues", 0)
                result["medium_issues"] = quick_result.get("medium_issues", 0)
                result["low_issues"] = quick_result.get("low_issues", 0)
                result["security_score"] = quick_result.get("security_score", 0)
        else:
            # No ZAP scan, use quick scan results only
            result["total_issues"] = quick_result.get("total_issues", 0)
            result["high_issues"] = quick_result.get("high_issues", 0)
            result["medium_issues"] = quick_result.get("medium_issues", 0)
            result["low_issues"] = quick_result.get("low_issues", 0)
            result["security_score"] = quick_result.get("security_score", 0)
        
        result["owasp_aligned"] = True
        result["scan_data"] = quick_result.get("scan_data", {})
        result["issues"] = quick_result.get("issues", [])
        
        return result
