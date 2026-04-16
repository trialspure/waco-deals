# Waco Real Estate Deal Finder

Automatically scrapes Zillow listings in Waco, TX, scores them across 4 investment strategies, and generates cash offer letters.

## Stack

- **Backend**: Python FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js 16 + Tailwind CSS + shadcn/ui
- **Data**: HasData Zillow API + RentCast API
- **Maps**: Leaflet + OpenStreetMap (free)

---

## Setup

### 1. Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for PostgreSQL)
- Python 3.11+
- Node.js 20+

### 2. Get API Keys

| Service | URL | Cost |
|---|---|---|
| HasData (Zillow) | https://hasdata.com | 1,000 free calls to start |
| RentCast | https://app.rentcast.io/app/api-keys | Free (50 calls) |

### 3. Start PostgreSQL

```bash
cd waco-deals
docker compose up -d
```

### 4. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Edit `.env` and add your API keys:
```
RAPIDAPI_KEY=your_key_here
RENTCAST_API_KEY=your_key_here
```

Run migrations and start the server:
```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard at: http://localhost:3000

---

## Usage

1. **Refresh Listings** — Click the button in the nav bar to scrape Waco listings from Zillow
2. **Dashboard** — Browse properties sorted by investment score, filter by strategy/price/ZIP
3. **Property Detail** — Click any property to see all 4 strategy scores with full breakdown
4. **Map** — Color-coded pins on an OpenStreetMap view, filterable by strategy
5. **Make Offer** — Generate a PDF cash offer letter with auto-calculated offer price
6. **Settings** — Tune scoring thresholds to match your criteria

---

## Scoring Models

| Strategy | Key Metric | Score 8-10 | Score 5-7 |
|---|---|---|---|
| Wholesale | Equity % | ≥ 30% | 15-29% |
| Fix & Flip | Profit margin | ≥ 20% + $20k | 10-19% |
| Long-Term Rental | Cap rate | ≥ 8% | 5-7.9% |
| Airbnb / STR | Gross yield | ≥ 12% | 8-11.9% |

All thresholds are adjustable on the Settings page.

---

## Auto-Scraping

The backend automatically runs the full scrape + score pipeline every 6 hours via APScheduler. You can also trigger it manually:

```bash
curl -X POST http://localhost:8000/admin/scrape
```

---

## MLS Integration (Phase 2)

To access MLS data you'll need:
- A Texas real estate license, OR
- A partnership with a local Waco agent who can provide RESO Web API credentials

Once you have credentials, add a new scraper in `backend/app/scrapers/mls.py` following the same pattern as `zillow.py`.
