"""API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models import Website, Scan, Issue, SecurityFeature, User
from app.core.security import get_current_active_user, get_optional_user
from app.schemas import (
    Website as WebsiteSchema,
    WebsiteCreate,
    WebsiteUpdate,
    Scan as ScanSchema,
    ScanCreate,
    ScanWithIssues,
    Issue as IssueSchema,
    IssueUpdate,
    SecurityFeature as SecurityFeatureSchema,
    SecuritySummary,
    LandingPageData,
    DemoScanRequest,
    DemoScanResponse
)

router = APIRouter()


# Website endpoints
@router.post("/websites", response_model=WebsiteSchema, status_code=status.HTTP_201_CREATED)
def create_website(
    website: WebsiteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new website for the current user"""
    # Check if website already exists for this user
    existing = db.query(Website).filter(
        Website.url == website.url,
        Website.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Website with URL {website.url} already exists"
        )
    
    db_website = Website(**website.model_dump(), user_id=current_user.id)
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website


@router.get("/websites", response_model=List[WebsiteSchema])
def get_websites(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all websites for the current user"""
    query = db.query(Website).filter(Website.user_id == current_user.id)
    if active_only:
        query = query.filter(Website.is_active == True)
    websites = query.offset(skip).limit(limit).all()
    return websites


@router.get("/websites/{website_id}", response_model=WebsiteSchema)
def get_website(
    website_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific website (only if it belongs to the current user)"""
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id {website_id} not found"
        )
    return website


@router.put("/websites/{website_id}", response_model=WebsiteSchema)
def update_website(
    website_id: int,
    website_update: WebsiteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a website (only if it belongs to the current user)"""
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id {website_id} not found"
        )
    
    update_data = website_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(website, field, value)
    
    db.commit()
    db.refresh(website)
    return website


@router.delete("/websites/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_website(
    website_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a website (only if it belongs to the current user)"""
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id {website_id} not found"
        )
    db.delete(website)
    db.commit()
    return None


# Scan endpoints
@router.post("/scans", response_model=ScanSchema, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan: ScanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new scan and actually perform the security scan"""
    from app.services.scanner import SecurityScanner
    
    # Verify website exists and belongs to current user
    website = db.query(Website).filter(
        Website.id == scan.website_id,
        Website.user_id == current_user.id
    ).first()
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id {scan.website_id} not found"
        )
    
    # Perform the security scan based on scan_type
    scanner = SecurityScanner()
    
    if scan.scan_type == "deep":
        # Perform deep scan with ZAP
        scan_result = await scanner.perform_deep_scan(website.url, use_zap=True)
        zap_results = scan_result.get("zap_scan")
    else:
        # Perform quick scan only
        scan_result = scanner.quick_scan(website.url)
        zap_results = None
    
    # Handle error case (matches security.py - returns {"error": str(e)})
    if "error" in scan_result or scan_result.get("status") == "failed":
        scan_time = scan_result.get("scan_time")
        if scan_time and isinstance(scan_time, datetime):
            if scan_time.tzinfo is None:
                scan_time = scan_time.replace(tzinfo=timezone.utc)
        else:
            scan_time = datetime.now(timezone.utc)
        
        db_scan = Scan(
            website_id=scan.website_id,
            scan_type=scan.scan_type,
            scan_time=scan_time,
            status="failed",
            error_message=scan_result.get("error") or scan_result.get("error_message"),
            total_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
            security_score=0,
            owasp_aligned=True,
            scan_data={},
            zap_results=zap_results
        )
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        return db_scan
    
    # Create scan record with results
    scan_time = scan_result.get("scan_time")
    if scan_time and isinstance(scan_time, datetime):
        if scan_time.tzinfo is None:
            scan_time = scan_time.replace(tzinfo=timezone.utc)
    else:
        scan_time = datetime.now(timezone.utc)
    
    db_scan = Scan(
        website_id=scan.website_id,
        scan_type=scan.scan_type,
        scan_time=scan_time,
        status=scan_result.get("status", "completed"),
        error_message=scan_result.get("error_message"),
        total_issues=scan_result.get("total_issues", 0),
        high_issues=scan_result.get("high_issues", 0),
        medium_issues=scan_result.get("medium_issues", 0),
        low_issues=scan_result.get("low_issues", 0),
        security_score=scan_result.get("security_score"),
        owasp_aligned=scan_result.get("owasp_aligned", True),
        scan_data=scan_result.get("scan_data"),
        zap_results=zap_results
    )
    db.add(db_scan)
    db.flush()  # Get the scan ID
    
    # Create issue records (issues are tuples: (severity, type, description))
    # Handle both quick scan issues and ZAP alerts
    issues_to_create = []
    
    # Add quick scan issues
    for issue_tuple in scan_result.get("issues", []):
        if isinstance(issue_tuple, tuple) and len(issue_tuple) >= 3:
            issues_to_create.append({
                "impact": issue_tuple[0],
                "issue_type": issue_tuple[1],
                "description": issue_tuple[2]
            })
    
    # Add ZAP alerts as issues if ZAP scan was performed
    if zap_results and zap_results.get("success"):
        for alert in zap_results.get("alerts", []):
            # Map ZAP risk levels to our impact levels
            risk_mapping = {
                "high": "HIGH",
                "medium": "MEDIUM",
                "low": "LOW",
                "informational": "LOW"  # Map informational to LOW
            }
            impact = risk_mapping.get(alert.get("risk_lower", "low"), "LOW")
            
            issues_to_create.append({
                "impact": impact,
                "issue_type": f"ZAP: {alert.get('name', 'Unknown')}",
                "description": f"{alert.get('description', '')}\nSolution: {alert.get('solution', 'N/A')}"
            })
    
    # Create issue records
    for issue_data in issues_to_create:
        from app.models import Issue
        issue = Issue(
            scan_id=db_scan.id,
            impact=issue_data["impact"],
            issue_type=issue_data["issue_type"],
            description=issue_data["description"],
            status="open"
        )
        db.add(issue)
    
    # Create security feature records
    from app.models import SecurityFeature
    security_features = {
        "HTTPS Enforced": not scan_result.get("error_message") and website.url.startswith("https://"),
        "TLS Validation": scan_result.get("security_score", 0) > 0,
        "Security Headers": scan_result["high_issues"] < 3,  # Less than 3 HIGH header issues
        "OWASP Aligned": scan_result["owasp_aligned"]
    }
    
    for feature_name, is_implemented in security_features.items():
        feature = SecurityFeature(
            scan_id=db_scan.id,
            feature_name=feature_name,
            feature_type="security_control",
            is_implemented=is_implemented,
            implementation_details=f"Checked during {scan.scan_type} scan"
        )
        db.add(feature)
    
    db.commit()
    db.refresh(db_scan)
    
    # Send alerts if HIGH issues found (matching security.py behavior)
    if scan_result["high_issues"] > 0:
        try:
            from app.services.alerts import send_slack_alert, send_email_alert
            # Format alerts data to match security.py format exactly
            alerts_data = {
                website.url: {
                    "scans": {
                        "quick": {
                            "issues": [
                                {"impact": i[0], "type": i[1], "description": i[2], "status": "open", "reported_at": datetime.now().isoformat()}
                                for i in scan_result.get("issues", []) if i[0] == "HIGH"
                            ]
                        }
                    }
                }
            }
            send_slack_alert(alerts_data)
            send_email_alert(alerts_data)
        except Exception as e:
            # Don't fail the scan if alerts fail (matches security.py behavior)
            print(f"Alert sending failed: {e}")
    
    return db_scan


@router.get("/scans", response_model=List[ScanSchema])
def get_scans(
    skip: int = 0,
    limit: int = 100,
    website_id: Optional[int] = None,
    scan_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all scans for websites belonging to the current user"""
    # Join with websites to filter by user_id
    query = db.query(Scan).join(Website).filter(Website.user_id == current_user.id)
    
    if website_id:
        # Also verify website belongs to user
        website = db.query(Website).filter(
            Website.id == website_id,
            Website.user_id == current_user.id
        ).first()
        if not website:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with id {website_id} not found"
            )
        query = query.filter(Scan.website_id == website_id)
    if scan_type:
        query = query.filter(Scan.scan_type == scan_type)
    
    scans = query.order_by(desc(Scan.scan_time)).offset(skip).limit(limit).all()
    return scans


@router.get("/scans/{scan_id}", response_model=ScanWithIssues)
def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific scan with issues (only if website belongs to current user)"""
    scan = db.query(Scan).join(Website).filter(
        Scan.id == scan_id,
        Website.user_id == current_user.id
    ).first()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with id {scan_id} not found"
        )
    
    # Get issues for this scan (relationship should load automatically, but explicitly loading)
    issues = db.query(Issue).filter(Issue.scan_id == scan_id).order_by(desc(Issue.reported_at)).all()
    
    # Get website info
    website = scan.website
    
    # Return scan with issues populated
    scan.issues = issues
    scan.website = website
    return scan


@router.get("/scans/latest/{website_id}", response_model=ScanWithIssues)
def get_latest_scan(
    website_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the latest scan for a website with issues (only if website belongs to current user)"""
    # Verify website belongs to user
    website = db.query(Website).filter(
        Website.id == website_id,
        Website.user_id == current_user.id
    ).first()
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Website with id {website_id} not found"
        )
    
    scan = (
        db.query(Scan)
        .filter(Scan.website_id == website_id)
        .order_by(desc(Scan.scan_time))
        .first()
    )
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scans found for website {website_id}"
        )
    
    # Get issues for this scan (relationship should load automatically, but explicitly loading)
    issues = db.query(Issue).filter(Issue.scan_id == scan.id).order_by(desc(Issue.reported_at)).all()
    
    # Get website info (relationship should load automatically)
    website = scan.website
    
    # Return scan with issues populated
    scan.issues = issues
    scan.website = website
    return scan


# Issue endpoints
@router.get("/issues", response_model=List[IssueSchema])
def get_issues(
    skip: int = 0,
    limit: int = 100,
    scan_id: Optional[int] = None,
    impact: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all issues for scans belonging to the current user"""
    # Join through Scan and Website to filter by user_id
    query = db.query(Issue).join(Scan).join(Website).filter(Website.user_id == current_user.id)
    
    if scan_id:
        # Also verify scan belongs to user's website
        scan = db.query(Scan).join(Website).filter(
            Scan.id == scan_id,
            Website.user_id == current_user.id
        ).first()
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan with id {scan_id} not found"
            )
        query = query.filter(Issue.scan_id == scan_id)
    if impact:
        query = query.filter(Issue.impact == impact.upper())
    if status_filter:
        query = query.filter(Issue.status == status_filter)
    
    issues = query.order_by(desc(Issue.reported_at)).offset(skip).limit(limit).all()
    return issues


@router.put("/issues/{issue_id}", response_model=IssueSchema)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an issue (e.g., mark as resolved) - only if it belongs to current user"""
    issue = db.query(Issue).join(Scan).join(Website).filter(
        Issue.id == issue_id,
        Website.user_id == current_user.id
    ).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with id {issue_id} not found"
        )
    
    update_data = issue_update.model_dump(exclude_unset=True)
    
    # If marking as resolved, set resolved_at
    if update_data.get("status") == "resolved" and not issue.resolved_at:
        update_data["resolved_at"] = datetime.now(timezone.utc)
    
    for field, value in update_data.items():
        setattr(issue, field, value)
    
    db.commit()
    db.refresh(issue)
    return issue


# Summary endpoints
@router.get("/summary", response_model=SecuritySummary)
def get_security_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall security summary for the current user"""
    total_websites = db.query(Website).filter(Website.user_id == current_user.id).count()
    active_websites = db.query(Website).filter(
        Website.user_id == current_user.id,
        Website.is_active == True
    ).count()
    
    # Get latest scan for each website belonging to current user
    from sqlalchemy import distinct
    subquery = (
        db.query(
            Scan.website_id,
            func.max(Scan.scan_time).label('max_time')
        )
        .join(Website)
        .filter(Website.user_id == current_user.id)
        .group_by(Scan.website_id)
        .subquery()
    )
    
    latest_scans = (
        db.query(Scan)
        .join(Website)
        .filter(Website.user_id == current_user.id)
        .join(
            subquery,
            (Scan.website_id == subquery.c.website_id) &
            (Scan.scan_time == subquery.c.max_time)
        )
        .all()
    )
    
    secure_websites = sum(1 for scan in latest_scans if scan.high_issues == 0)
    total_issues = sum(scan.total_issues for scan in latest_scans)
    high_issues = sum(scan.high_issues for scan in latest_scans)
    medium_issues = sum(scan.medium_issues for scan in latest_scans)
    low_issues = sum(scan.low_issues for scan in latest_scans)
    
    security_score = (
        (secure_websites / active_websites * 100) if active_websites > 0 else 0
    )
    
    last_scan_time = (
        db.query(func.max(Scan.scan_time))
        .join(Website)
        .filter(Website.user_id == current_user.id)
        .scalar()
    )
    
    return SecuritySummary(
        total_websites=total_websites,
        active_websites=active_websites,
        secure_websites=secure_websites,
        security_score=round(security_score, 1),
        total_issues=total_issues,
        high_issues=high_issues,
        medium_issues=medium_issues,
        low_issues=low_issues,
        last_scan_time=last_scan_time
    )


@router.get("/landing-page-data", response_model=LandingPageData)
def get_landing_page_data(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get data formatted for landing page. If user is authenticated, show their data; otherwise show empty/default data."""
    # If user is authenticated, filter by user_id; otherwise return empty data
    if current_user:
        # Get summary data for current user
        total_websites = db.query(Website).filter(Website.user_id == current_user.id).count()
        active_websites = db.query(Website).filter(
            Website.user_id == current_user.id,
            Website.is_active == True
        ).count()
        
        # Corrected query to get the latest scan for each website belonging to current user
        subquery = (
            db.query(
                Scan.website_id,
                func.max(Scan.scan_time).label('max_time')
            )
            .join(Website)
            .filter(Website.user_id == current_user.id)
            .group_by(Scan.website_id)
            .subquery()
        )
        
        latest_scans_for_summary = (
            db.query(Scan)
            .join(Website)
            .filter(Website.user_id == current_user.id)
            .join(
                subquery,
                (Scan.website_id == subquery.c.website_id) &
                (Scan.scan_time == subquery.c.max_time)
            )
            .all()
        )
        
        # Filter out failed scans for score calculation
        successfully_scanned_sites = [
            scan for scan in latest_scans_for_summary
            if scan.status != "failed" and not scan.error_message
        ]
        
        secure_websites = sum(1 for scan in successfully_scanned_sites if scan.high_issues == 0)
        total_issues = sum(scan.total_issues for scan in successfully_scanned_sites)
        high_issues = sum(scan.high_issues for scan in successfully_scanned_sites)
        medium_issues = sum(scan.medium_issues for scan in successfully_scanned_sites)
        low_issues = sum(scan.low_issues for scan in successfully_scanned_sites)
        
        security_score = (
            (secure_websites / len(successfully_scanned_sites) * 100)
            if len(successfully_scanned_sites) > 0 else 0
        )
        
        last_scan_time = (
            db.query(func.max(Scan.scan_time))
            .join(Website)
            .filter(Website.user_id == current_user.id)
            .scalar()
        )
        
        # Get all active websites with their latest scan for current user
        websites = db.query(Website).filter(
            Website.user_id == current_user.id,
            Website.is_active == True
        ).all()
        websites_data = []
        
        for website in websites:
            latest_scan = (
                db.query(Scan)
                .filter(Scan.website_id == website.id)
                .order_by(desc(Scan.scan_time))
                .first()
            )
            
            if latest_scan:
                # Determine status based on scan result
                # Calculate low_issues from total - high - medium
                low_issues = max(0, latest_scan.total_issues - latest_scan.high_issues - latest_scan.medium_issues)
                if latest_scan.status == "failed" or latest_scan.error_message:
                    status = "scan_failed"
                    site_error = latest_scan.error_message
                elif latest_scan.high_issues == 0:
                    status = "secure"
                    site_error = None
                else:
                    status = "needs_attention"
                    site_error = None
                
                websites_data.append({
                    "url": website.url,
                    "status": status,
                    "issue_count": latest_scan.total_issues,
                    "high_issues": latest_scan.high_issues,
                    "medium_issues": latest_scan.medium_issues,
                    "low_issues": low_issues,
                    "last_scan": latest_scan.scan_time.isoformat() if latest_scan.scan_time else "",
                    "error": site_error
                })
            else:
                websites_data.append({
                    "url": website.url,
                    "status": "not_scanned",
                    "issue_count": 0,
                    "high_issues": 0,
                    "medium_issues": 0,
                    "low_issues": 0,
                    "last_scan": ""
                })
    else:
        # No user authenticated, return empty/default data
        total_websites = 0
        active_websites = 0
        secure_websites = 0
        total_issues = 0
        high_issues = 0
        medium_issues = 0
        low_issues = 0
        security_score = 0.0
        last_scan_time = None
        websites_data = []
    
    summary = SecuritySummary(
        total_websites=total_websites,
        active_websites=active_websites,
        secure_websites=secure_websites,
        security_score=round(security_score, 1),
        total_issues=total_issues,
        high_issues=high_issues,
        medium_issues=medium_issues,
        low_issues=low_issues,
        last_scan_time=last_scan_time
    )
    
    # Security features (from latest scans)
    security_features = {
        "https_enforced": True,
        "tls_validation": True,
        "security_headers": True,
        "owasp_aligned": True,
        "vulnerability_detection": True,
        "multi_environment": len(websites_data) > 1 if current_user else False,
        "responsible_disclosure": True
    }
    
    return LandingPageData(
        last_updated=datetime.now(timezone.utc),
        summary=summary,
        security_features=security_features,
        websites=websites_data
    )


# Public Demo Scan Endpoint (No authentication required)
@router.post("/demo/scan", response_model=DemoScanResponse, status_code=status.HTTP_200_OK)
def demo_scan(
    scan_request: DemoScanRequest,
    db: Session = Depends(get_db)
):
    """
    Public demo scan endpoint - allows users to try scanning without authentication.
    Results are not saved to the database.
    """
    from app.services.scanner import SecurityScanner
    
    # Validate URL format
    url = scan_request.url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Perform the scan
    scanner = SecurityScanner()
    scan_result = scanner.quick_scan(url)
    
    # Handle error case
    scan_time = scan_result.get("scan_time")
    if scan_time and isinstance(scan_time, datetime):
        # Ensure timezone-aware datetime
        if scan_time.tzinfo is None:
            scan_time = scan_time.replace(tzinfo=timezone.utc)
    else:
        scan_time = datetime.now(timezone.utc)
    
    if "error" in scan_result:
        return DemoScanResponse(
            scan_time=scan_time,
            status="failed",
            error_message=scan_result.get("error_message", scan_result.get("error", "Unknown error")),
            total_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
            security_score=0,
            owasp_aligned=True,
            issues=[],
            scan_type="quick",
            is_demo=True
        )
    
    # Convert issues from tuple format to dict format for API response
    issues_list = []
    for issue_tuple in scan_result.get("issues", []):
        if isinstance(issue_tuple, tuple) and len(issue_tuple) >= 3:
            issues_list.append({
                "impact": issue_tuple[0],
                "issue_type": issue_tuple[1],
                "description": issue_tuple[2]
            })
    
    return DemoScanResponse(
        scan_time=scan_time,
        status=scan_result.get("status", "completed"),
        error_message=scan_result.get("error_message"),
        total_issues=scan_result.get("total_issues", 0),
        high_issues=scan_result.get("high_issues", 0),
        medium_issues=scan_result.get("medium_issues", 0),
        low_issues=scan_result.get("low_issues", 0),
        security_score=scan_result.get("security_score", 0),
        owasp_aligned=scan_result.get("owasp_aligned", True),
        issues=issues_list,
        scan_type="quick",
        is_demo=True
    )


# ZAP Status Endpoint
@router.get("/zap/status")
def get_zap_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get ZAP scanner status and availability"""
    try:
        from app.main import get_zap_scanner
        
        zap_scanner = get_zap_scanner()
        if zap_scanner:
            status = zap_scanner.get_scan_status()
            return status
        else:
            return {
                "enabled": False,
                "available": False,
                "url": None,
                "version": None,
                "error": "ZAP scanner not initialized"
            }
    except Exception as e:
        return {
            "enabled": False,
            "available": False,
            "url": None,
            "version": None,
            "error": str(e)
        }

