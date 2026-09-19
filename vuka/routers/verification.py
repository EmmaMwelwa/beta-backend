import mimetypes, os, secrets
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from database import get_db
from vuka.dependency import get_current_user, require_verifier
from vuka.models.registration import Registration
from vuka.models.security import VerificationDocument
from vuka.schemas.verification import VerificationResponse, VerificationReview
from vuka.security.audit import record_event

router=APIRouter(prefix="/graduate-verification",tags=["Graduate Verification"])
UPLOAD_DIR=Path(os.getenv("VERIFICATION_UPLOAD_DIR","./uploads/verification")).resolve()
MAX_SIZE=int(os.getenv("VERIFICATION_MAX_FILE_SIZE","5242880"))
ALLOWED={"pdf":"application/pdf","jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png"}

@router.post("/documents",response_model=VerificationResponse,status_code=201)
async def upload_document(file:UploadFile=File(...),current_user:Registration=Depends(get_current_user),db:Session=Depends(get_db)):
    ext=Path(file.filename or "").suffix.lower().lstrip('.')
    if ext not in ALLOWED: raise HTTPException(400,"Unsupported document type")
    if file.content_type != ALLOWED[ext]: raise HTTPException(400,"Invalid document MIME type")
    data=await file.read(MAX_SIZE+1)
    if len(data)>MAX_SIZE: raise HTTPException(413,"File is too large")
    if ext=="pdf" and not data.startswith(b"%PDF-"): raise HTTPException(400,"Invalid PDF file")
    if ext in {"jpg","jpeg"} and not data.startswith(b"\xff\xd8\xff"): raise HTTPException(400,"Invalid JPEG file")
    if ext=="png" and not data.startswith(b"\x89PNG\r\n\x1a\n"): raise HTTPException(400,"Invalid PNG file")
    UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
    ref=f"{current_user.user_id}/{secrets.token_urlsafe(32)}.{ext}"
    path=(UPLOAD_DIR/ref).resolve()
    if UPLOAD_DIR not in path.parents: raise HTTPException(400,"Invalid file path")
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    doc=VerificationDocument(user_id=current_user.user_id,document_reference=ref,document_type="FINAL_YEAR_KENYAN_HIGH_SCHOOL_RESULTS",file_size=len(data),mime_type=ALLOWED[ext])
    db.add(doc); db.commit(); db.refresh(doc)
    record_event(db,event_type="DOCUMENT_UPLOADED",action="graduate_document_upload",user_id=current_user.user_id,target_type="verification_document",target_id=doc.id)
    return doc

@router.get("/me",response_model=list[VerificationResponse])
def my_documents(current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    return db.query(VerificationDocument).filter(VerificationDocument.user_id==current_user.user_id).order_by(VerificationDocument.uploaded_at.desc()).all()

@router.get("/pending",response_model=list[VerificationResponse])
def pending(current_user=Depends(require_verifier),db:Session=Depends(get_db)):
    return db.query(VerificationDocument).filter(VerificationDocument.verification_status.in_(["PENDING","REQUIRES_REVIEW"])).all()

@router.patch("/documents/{document_id}",response_model=VerificationResponse)
def review(document_id:int,payload:VerificationReview,current_user=Depends(require_verifier),db:Session=Depends(get_db)):
    doc=db.get(VerificationDocument,document_id)
    if not doc: raise HTTPException(404,"Verification document not found")
    if doc.user_id==current_user.user_id: raise HTTPException(403,"You cannot review your own document")
    if payload.status=="REJECTED" and not payload.rejection_reason: raise HTTPException(400,"Rejection reason is required")
    doc.verification_status=payload.status; doc.rejection_reason=payload.rejection_reason; doc.reviewed_at=datetime.now(timezone.utc); doc.reviewed_by=current_user.user_id
    user=db.get(Registration,doc.user_id); user.is_verified=(payload.status=="VERIFIED")
    db.commit()
    record_event(db,event_type="DOCUMENT_VERIFIED" if payload.status=="VERIFIED" else "DOCUMENT_REJECTED",action="graduate_document_review",user_id=current_user.user_id,target_type="verification_document",target_id=doc.id,metadata={"status":payload.status},severity="MEDIUM")
    return doc
