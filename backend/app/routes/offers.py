from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Property, OfferLetter
from app.pdf_generator import generate_offer_letter

router = APIRouter(prefix="/offers", tags=["offers"])


class OfferRequest(BaseModel):
    property_id: int
    buyer_name: str
    buyer_address: Optional[str] = ""
    buyer_phone: Optional[str] = ""
    buyer_email: Optional[str] = ""
    strategy: str  # wholesale | flip | rental | airbnb
    offer_price: float
    earnest_money: float = 1000.0
    closing_days: int = 21
    inspection_days: int = 10
    notes: Optional[str] = ""


@router.post("/generate")
def generate_offer(req: OfferRequest, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.id == req.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    full_address = f"{prop.address}, {prop.city}, {prop.state} {prop.zip_code}"

    pdf_bytes = generate_offer_letter(
        property_address=full_address,
        buyer_name=req.buyer_name,
        buyer_address=req.buyer_address,
        buyer_phone=req.buyer_phone,
        buyer_email=req.buyer_email,
        offer_price=req.offer_price,
        earnest_money=req.earnest_money,
        closing_days=req.closing_days,
        inspection_days=req.inspection_days,
        strategy=req.strategy,
        notes=req.notes,
    )

    # Persist to DB
    letter = OfferLetter(
        property_id=req.property_id,
        buyer_name=req.buyer_name,
        buyer_address=req.buyer_address,
        buyer_phone=req.buyer_phone,
        buyer_email=req.buyer_email,
        strategy=req.strategy,
        offer_price=req.offer_price,
        earnest_money=req.earnest_money,
        closing_days=req.closing_days,
        inspection_days=req.inspection_days,
        notes=req.notes,
    )
    db.add(letter)
    db.commit()

    safe_address = prop.address.replace(" ", "_").replace(",", "")[:40]
    filename = f"offer_{safe_address}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
