from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from vuka.schemas.registration import RegistrationResponse, RegistrationUpdate
from vuka.services import registration as registration_service
from vuka.dependency import require_admin
from vuka.models.registration import Registration
from vuka.security.audit import record_event
import os, secrets

router=APIRouter(tags=["Admin"])
ADMIN_BOOTSTRAP_KEY=os.getenv("ADMIN_BOOTSTRAP_KEY")

class BootstrapAdminRequest(BaseModel): user_id:int; bootstrap_key:str
class RoleChangeRequest(BaseModel): user_type:str

@router.post("/bootstrap",response_model=RegistrationResponse)
def bootstrap_admin(payload:BootstrapAdminRequest,db:Session=Depends(get_db)):
    if not ADMIN_BOOTSTRAP_KEY: raise HTTPException(503,"Admin bootstrap is not configured")
    if not secrets.compare_digest(payload.bootstrap_key,ADMIN_BOOTSTRAP_KEY): raise HTTPException(403,"Invalid bootstrap credentials")
    if db.query(Registration).filter(Registration.user_type=="admin").first(): raise HTTPException(409,"Administrator already exists")
    user=db.get(Registration,payload.user_id)
    if not user: raise HTTPException(404,"User not found")
    user.user_type="admin"; db.commit(); record_event(db,event_type="ADMIN_CREATED",action="bootstrap_admin",user_id=user.user_id,target_type="user",target_id=user.user_id,severity="CRITICAL",alert=True)
    return user

@router.get("/users",response_model=list[RegistrationResponse])
def get_users(db:Session=Depends(get_db),current_user=Depends(require_admin)): return registration_service.get_registrations(db)

@router.get("/users/{user_id}",response_model=RegistrationResponse)
def get_user(user_id:int,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    user=registration_service.get_registration(db,user_id)
    if not user: raise HTTPException(404,"User not found")
    return user

@router.patch("/users/{user_id}",response_model=RegistrationResponse)
def update_user(user_id:int,registration:RegistrationUpdate,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    user=db.get(Registration,user_id)
    if not user: raise HTTPException(404,"User not found")
    old_role=user.user_type
    user=registration_service.update_registration(db,user_id,registration)
    if old_role!=user.user_type: record_event(db,event_type="ROLE_CHANGED",action="role_change",user_id=current_user.user_id,target_type="user",target_id=user_id,metadata={"from":old_role,"to":user.user_type},severity="HIGH",alert=True)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id:int,db:Session=Depends(get_db),current_user=Depends(require_admin)):
    return registration_service.delete_registration(db,user_id)
