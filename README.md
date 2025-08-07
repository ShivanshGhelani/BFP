# 🔍 Browser Fingerprinting Platform (BFP)

A comprehensive browser fingerprinting system that collects **100+ data points** across **27+ categories** to create unique visitor profiles for fraud prevention, analytics, and security applications.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-brightgreen.svg)](https://mongodb.com)
[![Redis](https://img.shields.io/badge/Redis-6.0+-red.svg)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### 🎯 **Core Capabilities**
- **100+ Data Points**: Comprehensive fingerprinting across 27+ categories
- **iOS Compatibility**: Enhanced browser detection for iOS devices
- **Real-time Processing**: Immediate fingerprint analysis and storage
- **Multi-device Support**: Desktop, mobile, and tablet detection
- **Geographic Intelligence**: Advanced location services with caching

### 🔧 **Technical Features**
- **FastAPI Backend**: High-performance async web framework
- **MongoDB Storage**: Scalable document database for visitor profiles
- **Redis Caching**: 5-minute TTL for expensive geolocation lookups
- **Rate Limiting**: Production-ready 60 requests/minute protection
- **Enhanced Brand Detection**: Multi-method device brand identification

### 📊 **Data Collection Categories**
1. **Visitor Identity & Session Management**
2. **Navigator/Browser Information** (iOS-enhanced)
3. **Hardware Fingerprinting**
4. **Display & Visual Characteristics**
5. **Advanced Visual Fingerprinting** (Canvas, WebGL)
6. **Audio Fingerprinting**
7. **Font Detection & Analysis**
8. **Browser Features & Capabilities**
9. **Storage & Session Data**
10. **Network & Connectivity**
11. **Location & Geolocation Services**
12. **Device Status** (Battery with iOS compatibility)
13. **Media Devices Enumeration**
14. **Speech & Voice Capabilities**
15. **System Integrations**
16. **User Interaction Tracking**
17. **Security & Privacy Indicators**
18. **Timezone & Locale Information**
19. **Mobile & Desktop Device Detection**
20. **CSS & Styling Preferences**

## 🛠 Installation

### Prerequisites
- Python 3.9+
- MongoDB (local or cloud)
- Redis (optional but recommended)

### Quick Setup

1. **Clone and setup virtual environment:**
```bash
git clone <repository-url>
cd BFP
python -m venv bfp
# Windows
bfp\Scripts\activate
# Linux/Mac
source bfp/bin/activate
```

2. **Run setup script:**
```bash
python setup.py
```

3. **Configure environment:**
   - Copy `.env.example` to `.env` (if available)
   - Update MongoDB connection string
   - Configure Redis URL if using caching

4. **Start the application:**
```bash
python main.py
# or
uvicorn main:app --reload
```

## ⚙️ Configuration

### Environment Variables (.env)

```properties
# MongoDB Configuration
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=your_database

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=3600

# API Configuration
API_BASE_URL1=http://localhost:8000
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Security
SECRET_KEY=your-secret-key-change-in-production

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Development
DEBUG=true
LOG_LEVEL=info
```

## 📡 API Endpoints

### Analytics Endpoints

#### Get IP Information
```
GET /api/v1/analytics/ip-info
```
Returns detailed IP information including geolocation data.

#### Simple IP Lookup
```
GET /api/v1/analytics/my-ip
```
Returns just the client IP address.

#### Reverse Geocoding
```
POST /api/v1/analytics/reverse-geocode
Content-Type: application/json

{
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

#### Visitor Logging
```
POST /api/v1/analytics/visitor-log
Content-Type: application/json

{
  "visitor_id": "unique-visitor-id",
  "navigator": {...},
  "hardware": {...},
  "loc": {...}
}
```

### Health Check
```
GET /api/v1/health/
GET /api/v1/health/db
```

## 🧩 Browser Fingerprinting

The platform collects various browser and device characteristics:

- **Navigator Information**: User agent, platform, language
- **Hardware Details**: CPU cores, memory, touch capabilities
- **Display Properties**: Screen resolution, color depth, pixel ratio
- **WebGL Fingerprinting**: Graphics card and driver information
- **Canvas Fingerprinting**: Unique rendering characteristics
- **Audio Context**: Audio processing capabilities
- **Font Detection**: Installed fonts and rendering
- **Network Information**: Connection type and speed
- **Geolocation**: GPS coordinates (with permission)

## 🔒 Privacy & Security

### Rate Limiting
- Configurable rate limits per endpoint
- IP-based limiting with proxy support
- Custom rate limit handlers

### Data Protection
- Configurable data retention periods
- Anonymization after specified days
- Secure MongoDB connections

### CORS Protection
- Configurable allowed origins
- Credential support for authenticated requests

## 🏗 Architecture

### Project Structure
```
BFP/
├── main.py                 # FastAPI application entry
├── requirements.txt        # Python dependencies
├── setup.py               # Setup and installation script
├── app/
│   ├── api/v1/           # API version 1 endpoints
│   │   ├── analytics.py  # Analytics and fingerprinting
│   │   └── health.py     # Health checks
│   ├── config/           # Configuration management
│   │   └── settings.py   # Pydantic settings
│   ├── core/             # Core utilities
│   │   ├── location_utils.py  # Geolocation services
│   │   ├── rate_limiter.py    # Rate limiting
│   │   ├── services.py        # Business logic
│   │   └── utils.py           # Helper functions
│   ├── database/         # Database connections
│   │   ├── connection.py      # MongoDB
│   │   └── redis_client.py    # Redis caching
│   └── models/           # Data models
├── static/               # Static assets
└── templates/           # HTML templates
```

### Key Components

1. **FastAPI Application**: Modern async web framework
2. **MongoDB**: Document storage for visitor data
3. **Redis**: Caching layer for geolocation data
4. **Rate Limiting**: SlowAPI-based request limiting
5. **Multi-source Geolocation**: Redundant location services

## 🚦 Running in Production

### Environment Setup
1. Set `DEBUG=false` in production
2. Use strong `SECRET_KEY`
3. Configure proper CORS origins
4. Set up MongoDB authentication
5. Use Redis for caching in production

### Deployment Options
- **Docker**: Containerized deployment
- **Cloud Platforms**: AWS, GCP, Azure
- **Traditional Servers**: With reverse proxy (Nginx)

### Monitoring
- Health check endpoints for uptime monitoring
- Structured logging with configurable levels
- Error tracking and rate limit monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **API Documentation**: http://localhost:8000/docs (when running)
- **Interactive API**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health
