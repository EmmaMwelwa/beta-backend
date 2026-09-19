from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from database import engine
load_dotenv()
from vuka.models.registration import Registration
from vuka.models.verifiedassessment import VerifiedAssessment
from vuka.models.userprogress import UserProgress
from vuka.models.generated_assessment import GeneratedAssessment

from vuka.routers import admin
from vuka.routers import opportunity_recommendation
from vuka.routers import registration

from vuka.routers.content_pathway import router as pathway_router
from vuka.routers.contents import router as content_router
from vuka.routers.verifiedassessment import router as verified_assessment_router
from vuka.routers.userprogress import router as user_progress_router
from vuka.routers.generated_assessment import router as generated_assessment_router

from vuka.routers import onboarding
from vuka.routers.verification import router as verification_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield

vuka = FastAPI(
    title="Beta Backend",
    version="1",
    lifespan=lifespan,
)

vuka.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@vuka.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"

    if request.url.scheme == "https":
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"

    return response


@vuka.exception_handler(OperationalError)
async def database_error_handler(
    _: Request,
    __: OperationalError,
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "The PostgreSQL database is unavailable"
        },
    )

vuka.include_router(admin.router,prefix="/admin",)
vuka.include_router(registration.router, prefix="/registration",)
vuka.include_router(onboarding.router, prefix="/onboarding",)
vuka.include_router(content_router, prefix="/contents")
vuka.include_router(pathway_router,)
vuka.include_router(verified_assessment_router,)
vuka.include_router(user_progress_router,)
vuka.include_router(generated_assessment_router,)
vuka.include_router(opportunity_recommendation.router, prefix="/opportunity-recommendation",)
vuka.include_router(verification_router,)

