"""OWASP ZAP security scanner integration"""
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import asyncio

try:
    from zapv2 import ZAPv2
except ImportError:
    ZAPv2 = None
    logging.warning("python-owasp-zap-v2.4 not installed. ZAP scanning will not be available.")

logger = logging.getLogger(__name__)


class ZAPScanner:
    """OWASP ZAP security scanner wrapper"""
    
    def __init__(self, zap_url: str = "http://localhost:8080", api_key: Optional[str] = None, enabled: bool = False):
        """
        Initialize ZAP scanner
        
        Args:
            zap_url: ZAP API URL (default: http://localhost:8080)
            api_key: ZAP API key (optional, only if authentication enabled)
            enabled: Whether ZAP scanning is enabled
        """
        self.zap_url = zap_url
        self.api_key = api_key
        self.enabled = enabled
        self.zap = None
        
        if enabled and ZAPv2:
            try:
                self.zap = ZAPv2(proxies={'http': zap_url, 'https': zap_url}, apikey=api_key)
                logger.info(f"ZAP Scanner initialized with URL: {zap_url}")
            except Exception as e:
                logger.error(f"Failed to initialize ZAP scanner: {e}")
                self.zap = None
                self.enabled = False
    
    def is_available(self) -> bool:
        """
        Check if ZAP is available and running
        
        Returns:
            bool: True if ZAP is available, False otherwise
        """
        if not self.enabled or not self.zap:
            return False
        
        try:
            version = self.zap.core.version
            if version:
                logger.debug(f"ZAP is available, version: {version}")
                return True
        except Exception as e:
            logger.warning(f"ZAP availability check failed: {e}")
        
        return False
    
    async def scan_website(
        self,
        url: str,
        spider_max_duration: int = 2,
        scan_timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Perform a full ZAP scan (spider + active scan) on a website
        
        Args:
            url: Website URL to scan
            spider_max_duration: Maximum duration for spider scan in minutes
            scan_timeout: Maximum timeout for the entire scan in seconds
        
        Returns:
            Dict containing scan results with alerts categorized by severity
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "ZAP scanner is not available or not enabled",
                "total_alerts": 0,
                "summary": {"high": 0, "medium": 0, "low": 0, "informational": 0},
                "alerts": []
            }
        
        try:
            logger.info(f"Starting ZAP scan for {url}")
            
            # Step 1: Spider scan
            logger.info(f"Starting spider scan for {url}")
            scan_id = self.zap.spider.scan(url)
            
            # Wait for spider to complete
            timeout = spider_max_duration * 60  # Convert to seconds
            while int(self.zap.spider.status(scan_id)) < 100:
                await asyncio.sleep(2)
                timeout -= 2
                if timeout <= 0:
                    logger.warning(f"Spider scan timeout for {url}")
                    break
            
            logger.info(f"Spider scan completed for {url}")
            
            # Step 2: Active scan
            logger.info(f"Starting active scan for {url}")
            ascan_id = self.zap.ascan.scan(url)
            
            # Wait for active scan to complete
            timeout = scan_timeout
            while int(self.zap.ascan.status(ascan_id)) < 100:
                await asyncio.sleep(5)
                timeout -= 5
                if timeout <= 0:
                    logger.warning(f"Active scan timeout for {url}")
                    break
            
            logger.info(f"Active scan completed for {url}")
            
            # Step 3: Get alerts
            alerts = self.zap.core.alerts(baseurl=url)
            
            # Process alerts
            processed = self._process_alerts(alerts)
            
            logger.info(f"ZAP scan completed for {url}: {processed['summary']}")
            
            return {
                "success": True,
                "total_alerts": processed["total_alerts"],
                "summary": processed["summary"],
                "alerts": processed["alerts"],
                "scan_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ZAP scan failed for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_alerts": 0,
                "summary": {"high": 0, "medium": 0, "low": 0, "informational": 0},
                "alerts": []
            }
    
    async def quick_passive_scan(self, url: str) -> Dict[str, Any]:
        """
        Perform a quick passive scan (spider only, no active scanning)
        
        Args:
            url: Website URL to scan
        
        Returns:
            Dict containing scan results
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "ZAP scanner is not available or not enabled",
                "total_alerts": 0,
                "summary": {"high": 0, "medium": 0, "low": 0, "informational": 0},
                "alerts": []
            }
        
        try:
            logger.info(f"Starting ZAP passive scan for {url}")
            
            # Spider scan only
            scan_id = self.zap.spider.scan(url)
            
            # Wait for spider to complete (shorter timeout for quick scan)
            timeout = 60  # 1 minute
            while int(self.zap.spider.status(scan_id)) < 100:
                await asyncio.sleep(2)
                timeout -= 2
                if timeout <= 0:
                    break
            
            # Get alerts (passive only)
            alerts = self.zap.core.alerts(baseurl=url)
            
            # Process alerts
            processed = self._process_alerts(alerts)
            
            return {
                "success": True,
                "total_alerts": processed["total_alerts"],
                "summary": processed["summary"],
                "alerts": processed["alerts"],
                "scan_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ZAP passive scan failed for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_alerts": 0,
                "summary": {"high": 0, "medium": 0, "low": 0, "informational": 0},
                "alerts": []
            }
    
    def _process_alerts(self, alerts: list) -> Dict[str, Any]:
        """
        Process ZAP alerts and categorize by severity
        
        Args:
            alerts: List of ZAP alert dictionaries
        
        Returns:
            Dict with categorized alerts and summary
        """
        summary = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "informational": 0
        }
        
        processed_alerts = []
        
        # ZAP risk levels: Informational, Low, Medium, High
        risk_mapping = {
            "Informational": "informational",
            "Low": "low",
            "Medium": "medium",
            "High": "high"
        }
        
        for alert in alerts:
            risk = alert.get("risk", "Informational")
            risk_lower = risk_mapping.get(risk, "informational")
            
            summary[risk_lower] = summary.get(risk_lower, 0) + 1
            
            processed_alerts.append({
                "risk": risk,
                "risk_lower": risk_lower,
                "name": alert.get("name", "Unknown"),
                "description": alert.get("description", ""),
                "solution": alert.get("solution", ""),
                "url": alert.get("url", ""),
                "parameter": alert.get("parameter", ""),
                "evidence": alert.get("evidence", "")
            })
        
        return {
            "total_alerts": len(alerts),
            "summary": summary,
            "alerts": processed_alerts
        }
    
    def get_scan_status(self) -> Dict[str, Any]:
        """
        Get ZAP scanner status
        
        Returns:
            Dict with scanner status information
        """
        status = {
            "enabled": self.enabled,
            "available": False,
            "url": self.zap_url,
            "version": None
        }
        
        if self.is_available():
            try:
                status["available"] = True
                status["version"] = self.zap.core.version
            except Exception as e:
                logger.warning(f"Failed to get ZAP version: {e}")
        
        return status

