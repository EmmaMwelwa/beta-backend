from datetime import datetime,timedelta,timezone
from sqlalchemy.orm import Session
from vuka.models.security import LoginAttempt

def record_login(db,user,identifier,ip,success):
    attempt=LoginAttempt(
        user_id=user.user_id if user else None,
        identifier=identifier,
        ip_address=ip,
        success=success
    )
    db.add(attempt)
    db.commit()

def recent_ip_failures(db,ip):
    since=datetime.now(timezone.utc)-timedelta(minutes=15)
    return db.query(LoginAttempt).filter(
        LoginAttempt.ip_address==ip,
        LoginAttempt.success.is_(False),
        LoginAttempt.attempted_at>=since
    ).count()

def locked(user):
    return (user.failed_login_attempts or 0)>=5