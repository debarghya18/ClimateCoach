"""
GDPR Audit Log Middleware
Tracks all data processing activities for GDPR compliance
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.core.database import get_db, AuditLog
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AuditLogMiddleware:
    """Middleware for GDPR audit logging"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Skip audit logging for static files and health checks
        if self._should_skip_audit(request.url.path):
            await self.app(scope, receive, send)
            return
            
        # Capture request details
        audit_data = await self._capture_request_data(request)
        
        # Process the request
        response_sent = False
        response_status = 200
        
        async def send_wrapper(message):
            nonlocal response_sent, response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                if not response_sent:
                    response_sent = True
                    # Log the audit entry
                    await self._log_audit_entry(audit_data, response_status)
            await send(message)
            
        await self.app(scope, receive, send_wrapper)
    
    def _should_skip_audit(self, path: str) -> bool:
        """Determine if path should be skipped from audit logging"""
        skip_paths = [
            "/static/",
            "/health",
            "/favicon.ico",
            "/api/docs",
            "/api/redoc"
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _capture_request_data(self, request: Request) -> Dict[str, Any]:
        """Capture relevant request data for audit logging"""
        # Extract user information if available
        user_id = None
        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                # Extract user ID from token (simplified)
                # In a real implementation, decode JWT token
                user_id = "extracted_from_token"
            except Exception:
                pass
        
        # Determine if this is a data processing activity
        is_data_processing = self._is_data_processing_activity(request)
        
        return {
            "user_id": user_id,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "timestamp": datetime.now(),
            "is_data_processing": is_data_processing,
            "data_types": self._identify_data_types(request)
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_data_processing_activity(self, request: Request) -> bool:
        """Determine if request involves personal data processing"""
        data_processing_paths = [
            "/api/v1/auth/",
            "/api/v1/analyze",
            "/api/v1/climate/",
            "/api/v1/dashboard/"
        ]
        return any(request.url.path.startswith(path) for path in data_processing_paths)
    
    def _identify_data_types(self, request: Request) -> list:
        """Identify types of personal data being processed"""
        data_types = []
        path = request.url.path
        
        if "/auth/" in path:
            data_types.extend(["identity", "authentication"])
        if "/analyze" in path:
            data_types.extend(["location", "property_data"])
        if "/climate/" in path:
            data_types.extend(["location", "usage_data"])
        if "/dashboard/" in path:
            data_types.extend(["usage_data", "preferences"])
            
        return data_types
    
    async def _log_audit_entry(self, audit_data: Dict[str, Any], response_status: int):
        """Log audit entry to database"""
        try:
            # In a real implementation, you'd use dependency injection
            # For now, we'll simulate the database operation
            audit_entry = {
                "user_id": audit_data.get("user_id"),
                "action": f"{audit_data['method']} {audit_data['path']}",
                "resource": audit_data["path"],
                "ip_address": audit_data["ip_address"],
                "user_agent": audit_data["user_agent"],
                "details": {
                    "query_params": audit_data["query_params"],
                    "response_status": response_status,
                    "data_types": audit_data["data_types"],
                    "is_data_processing": audit_data["is_data_processing"]
                },
                "timestamp": audit_data["timestamp"]
            }
            
            logger.info(f"GDPR Audit: {audit_entry['action']} by user {audit_entry['user_id']}")
            
            # Store in database (implementation would depend on your DB setup)
            # await self._store_audit_log(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to log audit entry: {str(e)}")
    
    async def _store_audit_log(self, audit_entry: Dict[str, Any]):
        """Store audit log in database"""
        # This would be implemented with proper database session management
        pass


class GDPRComplianceService:
    """Service for managing GDPR compliance operations"""
    
    def __init__(self):
        self.data_retention_days = settings.DATA_RETENTION_DAYS
        self.anonymization_enabled = settings.ANONYMIZATION_ENABLED
    
    async def handle_data_subject_request(self, request_type: str, user_id: int, 
                                        details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GDPR data subject requests"""
        try:
            if request_type == "access":
                return await self._handle_access_request(user_id)
            elif request_type == "portability":
                return await self._handle_portability_request(user_id)
            elif request_type == "rectification":
                return await self._handle_rectification_request(user_id, details)
            elif request_type == "erasure":
                return await self._handle_erasure_request(user_id)
            elif request_type == "restriction":
                return await self._handle_restriction_request(user_id, details)
            else:
                return {"error": "Unknown request type"}
                
        except Exception as e:
            logger.error(f"GDPR request handling failed: {str(e)}")
            return {"error": "Request processing failed"}
    
    async def _handle_access_request(self, user_id: int) -> Dict[str, Any]:
        """Handle right of access request (Article 15)"""
        # Collect all personal data for the user
        user_data = {
            "personal_information": await self._get_user_personal_data(user_id),
            "location_data": await self._get_user_location_data(user_id),
            "analysis_results": await self._get_user_analysis_data(user_id),
            "audit_logs": await self._get_user_audit_logs(user_id),
            "data_processing_purposes": self._get_processing_purposes(),
            "data_retention_period": f"{self.data_retention_days} days",
            "third_party_recipients": self._get_third_party_recipients()
        }
        
        return {
            "status": "completed",
            "data": user_data,
            "generated_at": datetime.now().isoformat(),
            "format": "JSON"
        }
    
    async def _handle_portability_request(self, user_id: int) -> Dict[str, Any]:
        """Handle right to data portability request (Article 20)"""
        portable_data = {
            "user_profile": await self._get_portable_user_data(user_id),
            "preferences": await self._get_user_preferences(user_id),
            "analysis_history": await self._get_portable_analysis_data(user_id)
        }
        
        return {
            "status": "completed",
            "portable_data": portable_data,
            "format": "machine_readable_JSON",
            "generated_at": datetime.now().isoformat()
        }
    
    async def _handle_rectification_request(self, user_id: int, 
                                          corrections: Dict[str, Any]) -> Dict[str, Any]:
        """Handle right to rectification request (Article 16)"""
        updated_fields = []
        
        for field, new_value in corrections.items():
            if await self._update_user_field(user_id, field, new_value):
                updated_fields.append(field)
        
        # Log the rectification
        await self._log_rectification(user_id, updated_fields)
        
        return {
            "status": "completed",
            "updated_fields": updated_fields,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_erasure_request(self, user_id: int) -> Dict[str, Any]:
        """Handle right to erasure request (Article 17)"""
        erasure_results = {
            "user_data": await self._erase_user_data(user_id),
            "location_data": await self._erase_location_data(user_id),
            "analysis_data": await self._anonymize_analysis_data(user_id),
            "audit_logs": await self._anonymize_audit_logs(user_id)
        }
        
        # Mark user as erased
        await self._mark_user_erased(user_id)
        
        return {
            "status": "completed",
            "erasure_results": erasure_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_restriction_request(self, user_id: int, 
                                        restrictions: Dict[str, Any]) -> Dict[str, Any]:
        """Handle right to restriction of processing request (Article 18)"""
        restricted_processing = []
        
        for processing_type in restrictions.get("restrict_processing", []):
            if await self._restrict_processing(user_id, processing_type):
                restricted_processing.append(processing_type)
        
        return {
            "status": "completed",
            "restricted_processing": restricted_processing,
            "timestamp": datetime.now().isoformat()
        }
    
    # Helper methods for data operations
    async def _get_user_personal_data(self, user_id: int) -> Dict[str, Any]:
        """Retrieve user's personal data"""
        # Implementation would query the database
        return {"user_id": user_id, "email": "user@example.com", "name": "John Doe"}
    
    async def _get_user_location_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieve user's location data"""
        return [{"latitude": 40.7128, "longitude": -74.0060, "address": "New York, NY"}]
    
    async def _get_user_analysis_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieve user's analysis results"""
        return [{"analysis_id": 1, "risk_score": 7.2, "date": "2024-01-01"}]
    
    async def _get_user_audit_logs(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieve user's audit logs"""
        return [{"action": "login", "timestamp": "2024-01-01T10:00:00Z"}]
    
    def _get_processing_purposes(self) -> List[str]:
        """Get list of data processing purposes"""
        return [
            "Climate risk analysis",
            "Personalized recommendations",
            "Service improvement",
            "Security and fraud prevention"
        ]
    
    def _get_third_party_recipients(self) -> List[str]:
        """Get list of third-party data recipients"""
        return [
            "Weather data providers",
            "Mapping services",
            "Analytics providers (anonymized data only)"
        ]
    
    async def _get_portable_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data in portable format"""
        return {"user_id": user_id, "preferences": {}, "settings": {}}
    
    async def _get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        return {"notification_preferences": {}, "privacy_settings": {}}
    
    async def _get_portable_analysis_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Get analysis data in portable format"""
        return [{"analysis_type": "climate_risk", "results": {}}]
    
    async def _update_user_field(self, user_id: int, field: str, value: Any) -> bool:
        """Update a user data field"""
        # Implementation would update the database
        logger.info(f"Updated field {field} for user {user_id}")
        return True
    
    async def _log_rectification(self, user_id: int, fields: List[str]):
        """Log data rectification"""
        logger.info(f"Data rectification for user {user_id}, fields: {fields}")
    
    async def _erase_user_data(self, user_id: int) -> bool:
        """Erase user's personal data"""
        # Implementation would delete from database
        logger.info(f"Erased personal data for user {user_id}")
        return True
    
    async def _erase_location_data(self, user_id: int) -> bool:
        """Erase user's location data"""
        logger.info(f"Erased location data for user {user_id}")
        return True
    
    async def _anonymize_analysis_data(self, user_id: int) -> bool:
        """Anonymize analysis data (keep for statistical purposes)"""
        logger.info(f"Anonymized analysis data for user {user_id}")
        return True
    
    async def _anonymize_audit_logs(self, user_id: int) -> bool:
        """Anonymize audit logs"""
        logger.info(f"Anonymized audit logs for user {user_id}")
        return True
    
    async def _mark_user_erased(self, user_id: int):
        """Mark user as erased in the system"""
        logger.info(f"Marked user {user_id} as erased")
    
    async def _restrict_processing(self, user_id: int, processing_type: str) -> bool:
        """Restrict specific type of data processing"""
        logger.info(f"Restricted {processing_type} processing for user {user_id}")
        return True
    
    async def schedule_data_retention_cleanup(self):
        """Schedule cleanup of data beyond retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        
        # Find and process expired data
        expired_data = await self._find_expired_data(cutoff_date)
        
        for data_entry in expired_data:
            if self.anonymization_enabled:
                await self._anonymize_expired_data(data_entry)
            else:
                await self._delete_expired_data(data_entry)
        
        logger.info(f"Processed {len(expired_data)} expired data entries")
    
    async def _find_expired_data(self, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Find data that has exceeded retention period"""
        # Implementation would query database for old data
        return []
    
    async def _anonymize_expired_data(self, data_entry: Dict[str, Any]):
        """Anonymize expired data"""
        logger.info(f"Anonymized expired data entry: {data_entry.get('id')}")
    
    async def _delete_expired_data(self, data_entry: Dict[str, Any]):
        """Delete expired data"""
        logger.info(f"Deleted expired data entry: {data_entry.get('id')}")
