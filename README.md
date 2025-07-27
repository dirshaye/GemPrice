# GemPrice - AI-Powered Dynamic Pricing System

**AI Hackfest Submission** | *Intelligent Pricing with Google Gemini AI*

## Prize Categories
- **Best Use of Gemini API** - Advanced prompt engineering for pricing analysis
- **Best Use of MongoDB Atlas** - Efficient data storage and analytics  
- **Best Use of Auth0** - Secure user authentication
- **Best UI/UX** - Clean, intuitive interface

## Overview
GemPrice is an AI-powered dynamic pricing system that helps businesses optimize their pricing strategies using Google Gemini AI. The system analyzes multiple factors including cost price, competitor pricing, inventory levels, and seasonal demand to provide intelligent pricing recommendations.

## Key Features
- **AI-Powered Pricing** - Google Gemini AI analyzes complex pricing factors
- **Real-time Recommendations** - Instant pricing suggestions with reasoning
- **Analytics Dashboard** - Track pricing history and performance
- **Secure Authentication** - Auth0 integration for user management
- **Responsive Design** - Modern SvelteKit frontend
- **Robust Fallbacks** - Intelligent backup pricing when API unavailable

## Technology Stack
- **Backend**: FastAPI (Python)
- **AI Engine**: Google Gemini 1.5 Flash
- **Database**: MongoDB Atlas
- **Authentication**: Auth0
- **Frontend**: SvelteKit + Tailwind CSS
- **Deployment**: Docker

## Prerequisites
- Python 3.8+
- Node.js 18+
- Google Gemini API Key
- MongoDB Atlas account
- Auth0 account

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/dirshaye/GemPrice.git
cd GemPrice
```

### 2. Environment Setup
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=your_mongodb_atlas_uri
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
```

### 3. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints
- `POST /api/v1/recommend-price` - Get AI pricing recommendation
- `POST /api/v1/recommend-price-auth` - Authenticated pricing (saves history)
- `GET /api/v1/user/suggestions` - Get user's pricing history
- `GET /api/v1/user/stats` - Get user analytics

### Health & Monitoring
- `GET /health` - System health check
- `GET /admin/health` - Admin health status

## How It Works

1. **Input Product Data** - Users provide cost price, competitor price, inventory level, season, and category
2. **AI Analysis** - Gemini AI analyzes the data using advanced prompt engineering
3. **Pricing Recommendation** - System returns optimized price with reasoning and confidence score
4. **Analytics Tracking** - All recommendations are stored for performance analysis

## Security Features
- Auth0 JWT token authentication
- Environment variable protection
- CORS configuration
- Input validation and sanitization

## Sample Request/Response

**Request:**
```json
{
  "cost_price": 50.0,
  "competitor_price": 85.0,
  "inventory_level": "High",
  "season": "Summer",
  "category": "Electronics"
}
```

**Response:**
```json
{
  "suggested_price": 75.99,
  "reasoning": "Based on your cost price of $50 and competitor price of $85, I recommend $75.99. This provides a healthy 52% profit margin while staying competitive. High inventory suggests room for aggressive pricing to move stock during summer season.",
  "confidence_score": 0.87
}
```

## Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
1. Set up MongoDB Atlas cluster
2. Configure Auth0 application
3. Deploy FastAPI backend
4. Deploy SvelteKit frontend
5. Configure environment variables

## Project Structure
```
GemPrice/
├── main.py              # FastAPI application
├── models.py            # Pydantic models
├── requirements.txt     # Python dependencies
├── routers/            # API route handlers
├── services/           # Business logic services
├── auth/              # Authentication utilities
├── frontend/          # SvelteKit application
└── docker-compose.yml # Container orchestration
```

## Contributing
This project was built for AI Hackfest. For issues or suggestions, please open a GitHub issue.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- **AI Hackfest** for the amazing opportunity
- **Google Gemini AI** for powerful language model capabilities
- **MongoDB Atlas** for reliable cloud database
- **Auth0** for seamless authentication
- **MLH** for hosting this incredible event

---

**Built with care for AI Hackfest 2025**
