"""
Visitor profile models for browser fingerprinting and analytics.
These models match the data collected by the JavaScript core-utils.js script.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.base import BaseDocument

class IOSInfo(BaseModel):
    """iOS-specific browser information."""
    is_ios: bool = Field(False, description="Is running on iOS")
    ios_version: Optional[str] = Field(None, description="iOS version")
    actual_browser: Optional[str] = Field(None, description="Actual browser (Chrome, Firefox, Edge, etc.)")
    webkit_version: Optional[str] = Field(None, description="WebKit version")
    crios_version: Optional[str] = Field(None, description="Chrome iOS version")
    fxios_version: Optional[str] = Field(None, description="Firefox iOS version")
    edgios_version: Optional[str] = Field(None, description="Edge iOS version")

class NavigatorInfo(BaseModel):
    """Navigator/browser information."""
    ua: str = Field(..., description="User agent string")
    plat: Optional[str] = Field(None, description="Platform")
    lang: Optional[str] = Field(None, description="Primary language")
    langs: Optional[List[str]] = Field(default_factory=list, description="Supported languages")
    cookies: Optional[bool] = Field(None, description="Cookies enabled")
    online: Optional[bool] = Field(None, description="Online status")
    dnt: Optional[str] = Field(None, description="Do not track setting")
    java: Optional[bool] = Field(None, description="Java enabled")
    browser_name: Optional[str] = Field(None, description="Browser name (with iOS distinction)")
    browser_version: Optional[str] = Field(None, description="Browser version")
    ios_info: Optional[IOSInfo] = Field(None, description="iOS-specific browser information")

class BatteryInfo(BaseModel):
    """Battery information with enhanced details."""
    charging: Optional[bool] = Field(None, description="Charging status")
    level: Optional[float] = Field(None, description="Battery level (0.0-1.0)")
    percentage: Optional[int] = Field(None, description="Battery percentage (0-100)")
    capacity: Optional[str] = Field(None, description="Estimated battery capacity")
    charging_time: Optional[float] = Field(None, description="Time to full charge")
    discharging_time: Optional[float] = Field(None, description="Time to battery depletion")
    error: Optional[str] = Field(None, description="Error if battery info unavailable")
    reason: Optional[str] = Field(None, description="Reason for error")

class HardwareInfo(BaseModel):
    """Hardware information."""
    cores: Optional[int] = Field(None, description="CPU cores")
    mem: Optional[float] = Field(None, description="Device memory in GB")
    touch: Optional[int] = Field(None, description="Max touch points")
    touchable: Optional[bool] = Field(None, description="Touch support")
    vibrate: Optional[bool] = Field(None, description="Vibration support")

class DisplayInfo(BaseModel):
    """Display/screen information."""
    screen_width: Optional[int] = Field(None, description="Screen width")
    screen_height: Optional[int] = Field(None, description="Screen height")
    avail_width: Optional[int] = Field(None, description="Available width")
    avail_height: Optional[int] = Field(None, description="Available height")
    color_depth: Optional[int] = Field(None, description="Color depth")
    pixel_depth: Optional[int] = Field(None, description="Pixel depth")
    pixel_ratio: Optional[float] = Field(None, description="Device pixel ratio")
    orientation: Optional[str] = Field(None, description="Screen orientation")

class LocationInfo(BaseModel):
    """Location information."""
    gps: Optional[Dict[str, Any]] = Field(None, description="GPS coordinates and metadata")
    ip_location: Optional[Dict[str, Any]] = Field(None, description="IP-based location")
    timezone: Optional[str] = Field(None, description="Timezone")
    timezone_offset: Optional[int] = Field(None, description="Timezone offset")

class IOSInfo(BaseModel):
    """iOS-specific information."""
    browser_type: Optional[str] = Field(None, description="Actual browser on iOS (Chrome iOS, Firefox iOS, etc.)")
    webkit_version: Optional[str] = Field(None, description="WebKit version")
    is_webview: Optional[bool] = Field(None, description="Whether running in WebView")
    standalone_mode: Optional[bool] = Field(None, description="PWA standalone mode")

class VisitorProfile(BaseDocument):
    """Complete visitor profile with browser fingerprinting data."""
    visitor_id: str = Field(..., description="Unique visitor identifier")
    session_key: Optional[str] = Field(None, description="Session key")
    ip_address: str = Field(..., description="Visitor IP address")
    real_ip: Optional[str] = Field(None, description="Real IP if behind proxy")
    
    # Core fingerprinting data
    navigator: Optional[NavigatorInfo] = Field(None, description="Browser/navigator info")
    hardware: Optional[HardwareInfo] = Field(None, description="Hardware information")
    display: Optional[DisplayInfo] = Field(None, description="Display information")
    location: Optional[LocationInfo] = Field(None, description="Location data")
    battery: Optional[BatteryInfo] = Field(None, description="Battery information")
    
    # Advanced fingerprinting
    canvas_fingerprint: Optional[str] = Field(None, description="Canvas fingerprint")
    webgl_fingerprint: Optional[str] = Field(None, description="WebGL fingerprint")
    audio_fingerprint: Optional[str] = Field(None, description="Audio context fingerprint")
    fonts: Optional[List[str]] = Field(default_factory=list, description="Available fonts")
    features: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Browser features")
    
    # Analytics data
    visit_count: int = Field(1, description="Total visit count")
    browser: Optional[str] = Field(None, description="Detected browser")
    device_type: Optional[str] = Field(None, description="Device type")
    os: Optional[str] = Field(None, description="Operating system")
    
    # Metadata
    collect_duration: Optional[int] = Field(None, description="Time taken to collect fingerprint (ms)")
    adblock_detected: Optional[bool] = Field(None, description="Ad blocker detected")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen timestamp")

class VisitorProfileCreate(BaseModel):
    """Model for creating visitor profile."""
    visitor_id: str
    session_key: Optional[str] = None
    ip_address: str
    real_ip: Optional[str] = None
    navigator: Optional[NavigatorInfo] = None
    hardware: Optional[HardwareInfo] = None
    display: Optional[DisplayInfo] = None
    location: Optional[LocationInfo] = None
    battery: Optional[BatteryInfo] = None
    canvas_fingerprint: Optional[str] = None
    webgl_fingerprint: Optional[str] = None
    audio_fingerprint: Optional[str] = None
    fonts: Optional[List[str]] = None
    features: Optional[Dict[str, Any]] = None
    visit_count: int = 1
    browser: Optional[str] = None
    device_type: Optional[str] = None
    os: Optional[str] = None
    collect_duration: Optional[int] = None
    adblock_detected: Optional[bool] = None

class VisitorProfileResponse(BaseModel):
    """Response model for visitor profile operations."""
    id: str
    visitor_id: str
    session_key: Optional[str]
    ip_address: str
    visit_count: int
    browser: Optional[str]
    device_type: Optional[str]
    os: Optional[str]
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

class FingerprintAnalysis(BaseModel):
    """Analysis results for a fingerprint."""
    uniqueness_score: float = Field(..., ge=0, le=100, description="Uniqueness score (0-100)")
    entropy: float = Field(..., description="Fingerprint entropy")
    similar_fingerprints: int = Field(..., description="Number of similar fingerprints found")
    risk_level: str = Field(..., description="Risk level (low, medium, high)")
    characteristics: List[str] = Field(default_factory=list, description="Key identifying characteristics")
    tracking_resistance: float = Field(..., ge=0, le=100, description="Resistance to tracking (0-100)")
