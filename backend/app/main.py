from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from datetime import datetime

from app.database import SessionLocal, engine, Base
from app.models import Invoice
from app.utils import generate_invoice_pdf, generate_upi_qr, generate_invoice_number, calculate_gst

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GST Invoice", version="1.0.0")

frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")
templates = Jinja2Templates(directory=frontend_path)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/app", response_class=HTMLResponse)
def app_dashboard(request: Request, db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(50).all()
    total_revenue = sum(i.total_amount for i in invoices)
    total_tax = sum(i.cgst + i.sgst + i.igst for i in invoices)
    return templates.TemplateResponse("app.html", {
        "request": request,
        "invoices": invoices,
        "total_revenue": total_revenue,
        "total_tax": total_tax,
        "invoice_count": len(invoices)
    })


@app.get("/app/create", response_class=HTMLResponse)
def create_invoice_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/api/invoices")
def create_invoice(
    client_name: str = Form(...),
    client_gstin: str = Form(""),
    client_address: str = Form(""),
    description: str = Form(...),
    hsn_code: str = Form("9983"),
    amount: float = Form(...),
    gst_type: str = Form("cgst_sgst"),
    place_of_supply: str = Form("Same State"),
    upi_id: str = Form(""),
    db: Session = Depends(get_db)
):
    invoice_number = generate_invoice_number(db)
    cgst, sgst, igst, total = calculate_gst(amount, gst_type)

    invoice = Invoice(
        invoice_number=invoice_number,
        client_name=client_name,
        client_gstin=client_gstin,
        client_address=client_address,
        description=description,
        hsn_code=hsn_code,
        amount=amount,
        cgst=cgst,
        sgst=sgst,
        igst=igst,
        total_amount=total,
        gst_type=gst_type,
        place_of_supply=place_of_supply,
        upi_id=upi_id,
        status="unpaid"
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return RedirectResponse(url=f"/app/invoice/{invoice.id}", status_code=303)


@app.get("/app/invoice/{invoice_id}", response_class=HTMLResponse)
def view_invoice(request: Request, invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return templates.TemplateResponse("invoice.html", {"request": request, "invoice": invoice})


@app.get("/api/invoices/{invoice_id}/pdf")
def download_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    pdf_path = generate_invoice_pdf(invoice)
    return FileResponse(pdf_path, filename=f"GST_Invoice_{invoice.invoice_number}.pdf", media_type="application/pdf")


@app.get("/api/invoices/{invoice_id}/qr")
def get_qr_code(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not invoice.upi_id:
        raise HTTPException(status_code=400, detail="No UPI ID set for this invoice")
    qr_path = generate_upi_qr(invoice)
    return FileResponse(qr_path, media_type="image/png")


@app.get("/api/invoices")
def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return [{
        "id": i.id,
        "invoice_number": i.invoice_number,
        "client_name": i.client_name,
        "amount": i.amount,
        "cgst": i.cgst,
        "sgst": i.sgst,
        "igst": i.igst,
        "total_amount": i.total_amount,
        "status": i.status,
        "created_at": i.created_at.isoformat()
    } for i in invoices]


@app.get("/api/reports/gst")
def gst_report(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    report = {
        "period": datetime.now().strftime("%Y-%m"),
        "total_invoices": len(invoices),
        "total_taxable_value": sum(i.amount for i in invoices),
        "total_cgst": sum(i.cgst for i in invoices),
        "total_sgst": sum(i.sgst for i in invoices),
        "total_igst": sum(i.igst for i in invoices),
        "grand_total": sum(i.total_amount for i in invoices),
        "invoices": [{
            "invoice_number": i.invoice_number,
            "date": i.created_at.strftime("%Y-%m-%d"),
            "hsn": i.hsn_code,
            "taxable": i.amount,
            "cgst": i.cgst,
            "sgst": i.sgst,
            "igst": i.igst,
            "total": i.total_amount
        } for i in invoices]
    }
    return report
