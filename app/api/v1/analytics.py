from fastapi import APIRouter, Request, status
from app.core import create_response
from app.core.rate_limiter import limiter
import logging
import httpx
import ipaddress
from typing import Dict, Any
from pydantic import BaseModel
from app.core.services import log_visitor_profile
from app.core.location_utils import get_location_from_coordinates, combine_location_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_client_ip(request: Request) -> str:
    """Extract real client IP address considering proxies and load balancers."""
    # Check for X-Forwarded-For header (most common with reverse proxies)
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        ip = x_forwarded_for.split(",")[0].strip()
        try:
            # Validate IP address
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            pass
    
    # Check for X-Real-IP header (Nginx)
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        try:
            ipaddress.ip_address(x_real_ip)
            return x_real_ip
        except ValueError:
            pass
    
    # Check for CF-Connecting-IP (Cloudflare)
    cf_connecting_ip = request.headers.get("cf-connecting-ip")
    if cf_connecting_ip:
        try:
            ipaddress.ip_address(cf_connecting_ip)
            return cf_connecting_ip
        except ValueError:
            pass
    
    # Fallback to direct client host
    return request.client.host if request.client else "unknown"

@router.get("/ip-info", response_model=dict, summary="Get client IP and location info")
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def get_ip_info(request: Request):
    """Get client IP address and basic location information."""
    try:
        client_ip = get_client_ip(request)
        
        # If we got localhost/private IP, try to get real public IP
        real_public_ip = client_ip
        if client_ip in ["127.0.0.1", "localhost", "::1"] or client_ip.startswith("192.168.") or client_ip.startswith("10.") or client_ip.startswith("172."):
            try:
                # Get real public IP from external service
                async with httpx.AsyncClient(timeout=5.0) as client:
                    # Try multiple services for reliability
                    for service in ["https://api.ipify.org?format=json", "https://ipinfo.io/json", "https://httpbin.org/ip"]:
                        try:
                            response = await client.get(service)
                            if response.status_code == 200:
                                data = response.json()
                                if "ip" in data:
                                    real_public_ip = data["ip"]
                                    break
                                elif "origin" in data:  # httpbin format
                                    real_public_ip = data["origin"]
                                    break
                        except:
                            continue
            except Exception as e:
                logger.warning(f"Failed to get public IP: {str(e)}")
        
        # Basic IP info
        ip_info = {
            "detectedIP": client_ip,
            "publicIP": real_public_ip,
            "isLocalhost": client_ip in ["127.0.0.1", "localhost", "::1"],
            "isPrivate": (client_ip.startswith("192.168.") or client_ip.startswith("10.") or client_ip.startswith("172.")),
            "headers": {
                "x_forwarded_for": request.headers.get("x-forwarded-for"),
                "x_real_ip": request.headers.get("x-real-ip"),
                "cf_connecting_ip": request.headers.get("cf-connecting-ip"),
                "user_agent": request.headers.get("user-agent"),
                "host": request.headers.get("host")
            }
        }
        
        # Use public IP for geolocation
        ip_for_geo = real_public_ip
        
        # Try to get geolocation data for the IP
        if ip_for_geo and ip_for_geo != "unknown" and not ip_for_geo.startswith("127.") and not ip_for_geo.startswith("192.168.") and not ip_for_geo.startswith("10."):
            try:
                # Use a free IP geolocation service
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"http://ip-api.com/json/{ip_for_geo}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,mobile,proxy,hosting,query")
                    
                    if response.status_code == 200:
                        geo_data = response.json()
                        if geo_data.get("status") == "success":
                            ip_info["location"] = {
                                "country": geo_data.get("country"),
                                "countryCode": geo_data.get("countryCode"),
                                "region": geo_data.get("regionName"),
                                "city": geo_data.get("city"),
                                "latitude": geo_data.get("lat"),
                                "longitude": geo_data.get("lon"),
                                "timezone": geo_data.get("timezone"),
                                "isp": geo_data.get("isp"),
                                "organization": geo_data.get("org"),
                                "continent": geo_data.get("continent"),
                                "mobile": geo_data.get("mobile"),
                                "proxy": geo_data.get("proxy"),
                                "hosting": geo_data.get("hosting"),
                                "query": geo_data.get("query")
                            }
                        else:
                            ip_info["location"] = {"error": geo_data.get("message", "Location lookup failed")}
                    else:
                        ip_info["location"] = {"error": "Geolocation service unavailable"}
                        
            except Exception as e:
                logger.warning(f"Geolocation lookup failed for IP {ip_for_geo}: {str(e)}")
                ip_info["location"] = {"error": "Geolocation lookup failed"}
        else:
            ip_info["location"] = {"error": "Private or local IP address", "note": "Using localhost - deploy to see real location"}
        
        return create_response(
            data=ip_info,
            message="IP information retrieved successfully",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting IP info: {str(e)}")
        return create_response(
            data={"ip": "unknown", "error": "IP detection failed"},
            message="IP information partially available",
            status_code=200
        )

@router.get("/my-ip", response_model=dict, summary="Get simple client IP")
@limiter.limit("20/minute")  # Rate limit: 20 requests per minute
async def get_my_ip(request: Request):
    """Simple endpoint to get just the client IP address."""
    try:
        client_ip = get_client_ip(request)
        return {"ip": client_ip}
    except Exception as e:
        logger.error(f"Error getting IP: {str(e)}")
        return {"ip": "unknown"}

@router.post("/reverse-geocode", response_model=dict, summary="Get location from coordinates")
@limiter.limit("15/minute")  # Rate limit: 15 requests per minute
async def reverse_geocode(request: Request, coordinates: Dict[str, float]):
    """Convert latitude and longitude to readable location information."""
    try:
        lat = coordinates.get("latitude")
        lon = coordinates.get("longitude")
        
        if not lat or not lon:
            return create_response(
                data={"error": "Missing latitude or longitude"},
                message="Invalid coordinates",
                status_code=400
            )
        
        # Use multiple reverse geocoding services for reliability
        location_data = await get_location_from_coordinates(lat, lon)
        
        return create_response(
            data=location_data,
            message="Location retrieved successfully",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error in reverse geocoding: {str(e)}")
        return create_response(
            data={"error": "Reverse geocoding failed"},
            message="Location lookup failed",
            status_code=200
        )

@router.post("/visitor-log", status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")  # Rate limit: 30 requests per minute for visitor logging
async def visitor_log(request: Request, profile: Dict[str, Any]):
    # Get real client IP (X-Forwarded-For or fallback)
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        real_ip = x_forwarded_for.split(",")[0].strip()
    else:
        real_ip = request.client.host
    client_ip = get_client_ip(request)
    await log_visitor_profile(client_ip, profile, real_ip=real_ip)
    return {"ok": True}
