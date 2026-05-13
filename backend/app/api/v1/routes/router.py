from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, cards, companies, contacts, exports, ml, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(cards.router)
api_router.include_router(contacts.router)
api_router.include_router(companies.router)
api_router.include_router(ml.router)
api_router.include_router(reports.router)
api_router.include_router(exports.router)

