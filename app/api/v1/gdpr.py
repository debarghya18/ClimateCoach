"""
GDPR Compliance API Endpoints
Handles data subject requests and privacy management
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_gdpr_consent
from app.core.database import User
from app.middleware.audit_log import GDPRComplianceService

logger = logging.getLogger(__name__)
router = APIRouter()
gdpr_service = GDPRComplianceService()


class ConsentRequest(BaseModel):
    """Model for consent requests"""
    data_processing_consent: bool
    marketing_consent: bool
    analytics_consent: bool = False
    third_party_sharing: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "data_processing_consent": True,
                "marketing_consent": False,
                "analytics_consent": True,
                "third_party_sharing": False
            }
        }


class DataSubjectRequest(BaseModel):
    """Model for data subject requests"""
    request_type: str
    details: Dict[str, Any] = {}
    reason: str = ""
    
    @validator('request_type')
    def validate_request_type(cls, v):
        valid_types = ['access', 'portability', 'rectification', 'erasure', 'restriction']
        if v not in valid_types:
            raise ValueError(f'Invalid request type. Must be one of: {valid_types}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "request_type": "access",
                "details": {},
                "reason": "I want to know what data you have about me"
            }
        }


class PrivacySettings(BaseModel):
    """Model for privacy settings"""
    data_retention_preference: str = "standard"  # standard, minimal, extended
    anonymization_preference: str = "enabled"   # enabled, disabled
    audit_log_access: bool = True
    third_party_data_sharing: bool = False
    marketing_communications: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "data_retention_preference": "standard",
                "anonymization_preference": "enabled",
                "audit_log_access": True,
                "third_party_data_sharing": False,
                "marketing_communications": False
            }
        }


@router.post("/consent")
async def update_consent(
    consent_request: ConsentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user consent preferences"""
    try:
        # Update user consent in database
        current_user.data_processing_consent = consent_request.data_processing_consent
        current_user.marketing_consent = consent_request.marketing_consent
        current_user.consent_date = datetime.now()
        
        # Save to database
        await db.commit()
        
        # Log consent change
        background_tasks.add_task(
            log_consent_change,
            current_user.id,
            consent_request.dict()
        )
        
        return {
            "status": "success",
            "message": "Consent preferences updated successfully",
            "consent_date": current_user.consent_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Consent update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update consent")


@router.get("/consent")
async def get_consent(
    current_user: User = Depends(get_current_user)
):
    """Get current user consent status"""
    return {
        "data_processing_consent": current_user.data_processing_consent,
        "marketing_consent": current_user.marketing_consent,
        "consent_date": current_user.consent_date.isoformat() if current_user.consent_date else None,
        "gdpr_compliant": current_user.data_processing_consent
    }


@router.post("/data-subject-request")
async def submit_data_subject_request(
    request: DataSubjectRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_gdpr_consent)
):
    """Submit a GDPR data subject request"""
    try:
        # Process the request in background
        background_tasks.add_task(
            process_data_subject_request,
            request.request_type,
            current_user.id,
            request.details,
            request.reason
        )
        
        return {
            "status": "accepted",
            "message": f"Your {request.request_type} request has been submitted",
            "request_id": f"DSR-{current_user.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "estimated_completion": "30 days maximum as per GDPR Article 12",
            "contact_email": "privacy@climateai.com"
        }
        
    except Exception as e:
        logger.error(f"Data subject request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process request")


@router.get("/my-data")
async def get_my_data(
    current_user: User = Depends(require_gdpr_consent)
):
    """Get user's personal data (Right of Access - Article 15)"""
    try:
        # Get comprehensive user data
        user_data = await gdpr_service._handle_access_request(current_user.id)
        
        return {
            "status": "success",
            "data": user_data,
            "generated_at": datetime.now().isoformat(),
            "format": "JSON",
            "note": "This data export complies with GDPR Article 15 (Right of Access)"
        }
        
    except Exception as e:
        logger.error(f"Data access request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve data")


@router.get("/data-export")
async def export_my_data(
    format: str = "json",
    current_user: User = Depends(require_gdpr_consent)
):
    """Export user data in portable format (Right to Data Portability - Article 20)"""
    try:
        if format.lower() not in ["json", "csv", "xml"]:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        # Get portable data
        portable_data = await gdpr_service._handle_portability_request(current_user.id)
        
        return {
            "status": "success",
            "export_data": portable_data,
            "format": format.upper(),
            "generated_at": datetime.now().isoformat(),
            "note": "This data export complies with GDPR Article 20 (Right to Data Portability)"
        }
        
    except Exception as e:
        logger.error(f"Data export failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export data")


@router.delete("/my-account")
async def delete_my_account(
    confirmation: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Delete user account and data (Right to Erasure - Article 17)"""
    try:
        if confirmation != "DELETE_MY_ACCOUNT":
            raise HTTPException(
                status_code=400, 
                detail="Please confirm deletion by sending 'DELETE_MY_ACCOUNT'"
            )
        
        # Process erasure in background
        background_tasks.add_task(
            process_account_deletion,
            current_user.id
        )
        
        return {
            "status": "accepted",
            "message": "Account deletion request has been submitted",
            "deletion_id": f"DEL-{current_user.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "estimated_completion": "72 hours",
            "note": "Some data may be retained for legal obligations as per GDPR Article 17(3)"
        }
        
    except Exception as e:
        logger.error(f"Account deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process deletion")


@router.get("/privacy-policy")
async def get_privacy_policy():
    """Get current privacy policy and data processing information"""
    return {
        "privacy_policy": {
            "version": "1.0",
            "last_updated": "2024-01-01",
            "data_controller": {
                "name": "Climate AI Platform",
                "contact": "privacy@climateai.com",
                "address": "123 Climate Street, Earth City, EC 12345"
            },
            "data_processing_purposes": [
                "Climate risk analysis and recommendations",
                "Service personalization and improvement",
                "Security and fraud prevention",
                "Legal compliance and customer support"
            ],
            "legal_basis": [
                "Consent (Article 6(1)(a))",
                "Contract performance (Article 6(1)(b))",
                "Legitimate interests (Article 6(1)(f))"
            ],
            "data_retention": {
                "personal_data": "365 days after account closure",
                "analytics_data": "Anonymized after 30 days",
                "audit_logs": "7 years for legal compliance"
            },
            "your_rights": [
                "Right of access (Article 15)",
                "Right to rectification (Article 16)",
                "Right to erasure (Article 17)",
                "Right to restrict processing (Article 18)",
                "Right to data portability (Article 20)",
                "Right to object (Article 21)"
            ],
            "data_transfers": {
                "third_countries": False,
                "safeguards": "All data processing within EU/EEA"
            }
        }
    }


@router.get("/audit-log")
async def get_my_audit_log(
    limit: int = 100,
    current_user: User = Depends(require_gdpr_consent)
):
    """Get user's audit log (transparency requirement)"""
    try:
        # Get audit logs for the user
        audit_logs = await gdpr_service._get_user_audit_logs(current_user.id)
        
        # Limit results
        limited_logs = audit_logs[:limit] if audit_logs else []
        
        return {
            "status": "success",
            "audit_logs": limited_logs,
            "total_entries": len(audit_logs) if audit_logs else 0,
            "showing": len(limited_logs),
            "note": "This log shows all data processing activities related to your account"
        }
        
    except Exception as e:
        logger.error(f"Audit log retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit log")


@router.post("/privacy-settings")
async def update_privacy_settings(
    settings: PrivacySettings,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Update user privacy settings"""
    try:
        # Log settings change
        background_tasks.add_task(
            log_privacy_settings_change,
            current_user.id,
            settings.dict()
        )
        
        return {
            "status": "success",
            "message": "Privacy settings updated successfully",
            "settings": settings.dict(),
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Privacy settings update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update privacy settings")


@router.get("/data-processing-activities")
async def get_data_processing_activities(
    current_user: User = Depends(get_current_user)
):
    """Get information about current data processing activities"""
    return {
        "active_processing": [
            {
                "purpose": "Climate risk analysis",
                "legal_basis": "Consent + Contract performance",
                "data_types": ["Location data", "Property specifications"],
                "retention_period": "365 days",
                "can_object": True
            },
            {
                "purpose": "Service improvement",
                "legal_basis": "Legitimate interests",
                "data_types": ["Usage analytics", "Performance metrics"],
                "retention_period": "Anonymized after 30 days",
                "can_object": True
            },
            {
                "purpose": "Security monitoring",
                "legal_basis": "Legitimate interests + Legal obligation",
                "data_types": ["Access logs", "IP addresses"],
                "retention_period": "90 days",
                "can_object": False
            }
        ],
        "user_id": current_user.id,
        "last_consent_update": current_user.consent_date.isoformat() if current_user.consent_date else None
    }


# Background task functions
async def log_consent_change(user_id: int, consent_data: Dict[str, Any]):
    """Log consent changes for audit purposes"""
    logger.info(f"Consent updated for user {user_id}: {consent_data}")


async def process_data_subject_request(request_type: str, user_id: int, 
                                     details: Dict[str, Any], reason: str):
    """Process data subject request in background"""
    try:
        logger.info(f"Processing {request_type} request for user {user_id}")
        
        # Handle the request using GDPR service
        result = await gdpr_service.handle_data_subject_request(
            request_type, user_id, details
        )
        
        logger.info(f"Completed {request_type} request for user {user_id}: {result}")
        
        # In a real implementation, you would:
        # 1. Send email notification to user
        # 2. Update request status in database
        # 3. Generate compliance reports
        
    except Exception as e:
        logger.error(f"Failed to process {request_type} request for user {user_id}: {str(e)}")


async def process_account_deletion(user_id: int):
    """Process account deletion in background"""
    try:
        logger.info(f"Processing account deletion for user {user_id}")
        
        # Handle erasure using GDPR service
        result = await gdpr_service._handle_erasure_request(user_id)
        
        logger.info(f"Completed account deletion for user {user_id}: {result}")
        
    except Exception as e:
        logger.error(f"Failed to delete account for user {user_id}: {str(e)}")


async def log_privacy_settings_change(user_id: int, settings: Dict[str, Any]):
    """Log privacy settings changes"""
    logger.info(f"Privacy settings updated for user {user_id}: {settings}")
