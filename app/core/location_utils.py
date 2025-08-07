import httpx
from typing import Dict
import hashlib
from app.database.redis_client import get_redis_client
import logging

logger = logging.getLogger(__name__)

async def get_location_from_coordinates(lat: float, lon: float) -> Dict:
    """Get location information from coordinates using multiple services with caching."""
    # Create cache key from coordinates
    cache_key = f"geo:{hashlib.md5(f'{lat},{lon}'.encode()).hexdigest()}"
    
    # Try to get from cache first
    redis_client = await get_redis_client()
    cached_result = await redis_client.get(cache_key)
    if cached_result:
        logger.info(f"Using cached geolocation for {lat},{lon}")
        return cached_result
    
    location_result = {
        "coordinates": {"latitude": lat, "longitude": lon},
        "sources": {}
    }
    # Service 1: OpenStreetMap Nominatim (Free, no API key required)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1",
                headers={"User-Agent": "BFP-Analytics/1.0"}
            )
            if response.status_code == 200:
                data = response.json()
                if "address" in data:
                    address = data["address"]
                    location_result["sources"]["openstreetmap"] = {
                        "display_name": data.get("display_name"),
                        "country": address.get("country"),
                        "country_code": address.get("country_code"),
                        "state": address.get("state"),
                        "city": address.get("city") or address.get("town") or address.get("village"),
                        "postcode": address.get("postcode"),
                        "road": address.get("road"),
                        "house_number": address.get("house_number"),
                        "suburb": address.get("suburb") or address.get("neighbourhood"),
                        "district": address.get("city_district") or address.get("district"),
                        "county": address.get("county"),
                        "region": address.get("region")
                    }
                else:
                    location_result["sources"]["openstreetmap"] = {"error": "No address found"}
    except Exception as e:
        location_result["sources"]["openstreetmap"] = {"error": str(e)}
    # Service 2: BigDataCloud (Free tier, no API key required)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
            )
            if response.status_code == 200:
                data = response.json()
                location_result["sources"]["bigdatacloud"] = {
                    "city": data.get("city"),
                    "locality": data.get("locality"),
                    "district": data.get("principalSubdivision"),
                    "country": data.get("countryName"),
                    "country_code": data.get("countryCode"),
                    "continent": data.get("continent"),
                    "timezone": data.get("localityInfo", {}).get("administrative", [{}])[0].get("name") if data.get("localityInfo") else None
                }
    except Exception as e:
        location_result["sources"]["bigdatacloud"] = {"error": str(e)}
    # Service 3: IP-API for additional context (if we have coordinates, we can get more info)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://ip-api.com/json/?lat={lat}&lon={lon}&fields=status,country,countryCode,region,regionName,city,timezone,isp,org")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    location_result["sources"]["ip_api"] = {
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "region": data.get("regionName"),
                        "city": data.get("city"),
                        "timezone": data.get("timezone"),
                        "isp": data.get("isp"),
                        "organization": data.get("org")
                    }
    except Exception as e:
        location_result["sources"]["ip_api"] = {"error": str(e)}
    # Combine best information from all sources
    combined_location = combine_location_data(location_result["sources"])
    location_result["combined"] = combined_location
    
    # Cache the result for future use
    await redis_client.set(cache_key, location_result)
    logger.info(f"Cached geolocation result for {lat},{lon}")
    
    return location_result

def combine_location_data(sources: Dict) -> Dict:
    """Combine location data from multiple sources to get the best information."""
    combined = {}
    # Priority order for different fields
    source_priority = ["openstreetmap", "bigdatacloud", "ip_api"]
    fields_to_combine = [
        "country", "country_code", "state", "region", "city", 
        "district", "postcode", "timezone", "road", "suburb"
    ]
    for field in fields_to_combine:
        for source in source_priority:
            if source in sources and isinstance(sources[source], dict):
                value = sources[source].get(field)
                if value and value != "":
                    combined[field] = value
                    combined[f"{field}_source"] = source
                    break
    # Special handling for display name
    if "openstreetmap" in sources and "display_name" in sources["openstreetmap"]:
        combined["full_address"] = sources["openstreetmap"]["display_name"]
    # Create a formatted address
    address_parts = []
    if combined.get("road"):
        address_parts.append(combined["road"])
    if combined.get("city"):
        address_parts.append(combined["city"])
    if combined.get("state") or combined.get("region"):
        address_parts.append(combined.get("state") or combined.get("region"))
    if combined.get("country"):
        address_parts.append(combined["country"])
    if address_parts:
        combined["formatted_address"] = ", ".join(address_parts)
    return combined 