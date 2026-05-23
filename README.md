# GST Invoice

A zero-friction GST invoicing tool for Indian freelancers and micro-businesses.

## Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deploy

### Backend (Vercel)
- Push to GitHub
- Connect to Vercel with Python runtime
- Add environment variables

### Frontend (Vercel)
- Static HTML + CSS + JS in `/frontend`
- Deploy as static site

## Tech Stack

- **Backend**: FastAPI + SQLite + Jinja2 templates
- **Frontend**: Vanilla HTML/CSS/JS (no build step)
- **PDF**: reportlab (GST-compliant invoice PDF generation)
- **QR**: python-qrcode (UPI payment links)
- **Auth**: JWT via python-jose (optional for v1)

## Features

1. Create GST invoices with HSN codes and auto tax calculation
2. Generate PDF invoices (GST-compliant format)
3. QR code for instant UPI payment
4. Simple dashboard with invoice history
5. Export GST reports for filing
