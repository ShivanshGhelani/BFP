# Browser Fingerprinting Models - Captures device and browser characteristics for visitor identification

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.base import BaseDocument

class BrowserInfo(BaseModel):
    """Browser information for fingerprinting."""
    user_agent: str = Field(..., description="Full user agent string")
    browser_name: Optional[str] = Field(None, description="Browser name (Chrome, Firefox, etc.)")
    browser_version: Optional[str] = Field(None, description="Browser version")
    engine: Optional[str] = Field(None, description="Browser engine (Blink, Gecko, etc.)")
    platform: Optional[str] = Field(None, description="Platform/OS")
    language: Optional[str] = Field(None, description="Browser language")
    languages: Optional[List[str]] = Field(default_factory=list, description="Supported languages")
    timezone: Optional[str] = Field(None, description="Browser timezone")

class DeviceInfo(BaseModel):
    """Device hardware information."""
    screen_resolution: Optional[str] = Field(None, description="Screen resolution (e.g., 1920x1080)")
    color_depth: Optional[int] = Field(None, description="Color depth")
    pixel_ratio: Optional[float] = Field(None, description="Device pixel ratio")
    cpu_cores: Optional[int] = Field(None, description="Number of CPU cores")
    memory: Optional[float] = Field(None, description="Device memory in GB")
    touch_support: Optional[bool] = Field(None, description="Touch support available")
    max_touch_points: Optional[int] = Field(None, description="Maximum touch points")
    device_type: Optional[str] = Field(None, description="Device type (mobile, desktop, tablet)")

class NetworkInfo(BaseModel):
    """Network and connection information."""
    ip_address: Optional[str] = Field(None, description="Client IP address")
    connection_type: Optional[str] = Field(None, description="Connection type (4g, wifi, etc.)")
    downlink: Optional[float] = Field(None, description="Effective bandwidth estimate")
    rtt: Optional[int] = Field(None, description="Round-trip time estimate")

class FingerprintData(BaseModel):
    """Complete browser fingerprint data."""
    fingerprint_hash: str = Field(..., description="Unique hash of the complete fingerprint")
    browser_info: BrowserInfo = Field(..., description="Browser information")
    device_info: DeviceInfo = Field(..., description="Device hardware information")
    network_info: Optional[NetworkInfo] = Field(default_factory=NetworkInfo, description="Network information")
    canvas_fingerprint: Optional[str] = Field(None, description="Canvas rendering fingerprint")
    webgl_fingerprint: Optional[str] = Field(None, description="WebGL rendering fingerprint")
    audio_fingerprint: Optional[str] = Field(None, description="Audio context fingerprint")
    fonts: Optional[List[str]] = Field(default_factory=list, description="Available fonts")
    plugins: Optional[List[str]] = Field(default_factory=list, description="Browser plugins")
    features: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Browser feature support")
    location: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Geolocation data")
    confidence_score: Optional[float] = Field(None, ge=0, le=100, description="Fingerprint uniqueness confidence (0-100)")

class BrowserFingerprint(BaseDocument):
    """Browser fingerprint document model."""
    visitor_id: Optional[str] = Field(None, description="Associated visitor ID")
    session_id: Optional[str] = Field(None, description="Session identifier")
    fingerprint_data: FingerprintData = Field(..., description="Complete fingerprint data")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    is_unique: Optional[bool] = Field(None, description="Whether this fingerprint is unique")
    similarity_score: Optional[float] = Field(None, description="Similarity to other fingerprints")
    visit_count: int = Field(1, description="Number of visits with this fingerprint")
    last_seen: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Last time this fingerprint was seen")
    
class BrowserFingerprintCreate(BaseModel):
    """Model for creating browser fingerprint."""
    visitor_id: Optional[str] = None
    session_id: Optional[str] = None
    fingerprint_data: FingerprintData
    ip_address: Optional[str] = None

class BrowserFingerprintUpdate(BaseModel):
    """Model for updating browser fingerprint."""
    fingerprint_data: Optional[FingerprintData] = None
    visit_count: Optional[int] = None
    last_seen: Optional[datetime] = None
    similarity_score: Optional[float] = None
    is_unique: Optional[bool] = None

class BrowserFingerprintResponse(BaseModel):
    """Response model for browser fingerprint operations."""
    id: str
    visitor_id: Optional[str]
    session_id: Optional[str]
    fingerprint_data: FingerprintData
    ip_address: Optional[str]
    is_unique: Optional[bool]
    similarity_score: Optional[float]
    visit_count: int
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

# Legacy classes - keeping for backward compatibility, but deprecated
class Fingerprint(BaseDocument):
    """Deprecated: Use BrowserFingerprint instead."""
    user_id: Optional[str] = Field(None, description="Associated user ID")
    fingerprint_data: FingerprintData = Field(..., description="Fingerprint template and data")
    device_info: Optional[Dict[str, str]] = Field(default_factory=dict, description="Device information")
    is_active: bool = Field(True, description="Whether fingerprint is active")
    verified: bool = Field(False, description="Whether fingerprint is verified")
    
class FingerprintCreate(BaseModel):
    """Model for creating fingerprint."""
    user_id: Optional[str] = None
    fingerprint_data: FingerprintData
    device_info: Optional[Dict[str, str]] = None

class FingerprintUpdate(BaseModel):
    """Model for updating fingerprint."""
    fingerprint_data: Optional[FingerprintData] = None
    device_info: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    verified: Optional[bool] = None

class FingerprintResponse(BaseModel):
    """Response model for fingerprint operations."""
    id: str
    user_id: Optional[str]
    fingerprint_data: FingerprintData
    device_info: Dict[str, str]
    is_active: bool
    verified: bool
    created_at: datetime
    updated_at: datetime
