from contextlib import asynccontextmanager

import debugpy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .configuration import settings
from .database import engine
from .domains.commuting.routes import router as commuting_router
from .domains.inventories.routes import router as inventories_router
from .domains.organizations.routes import router as organizations_router
from .domains.questionnaires.routes import router as questionnaires_router
from .domains.reference_data.routes import router as reference_data_router
from .domains.reports.routes import router as reports_router
from .domains.scope1.effluents.routes import router as effluents_router
from .domains.scope1.fugitive.routes import router as fugitive_router
from .domains.scope1.mobile_combustion.routes import router as mobile_combustion_router
from .domains.scope1.stationary_combustion.routes import router as stationary_combustion_router
from .domains.scope2.energy.routes import router as energy_router
from .domains.scope3.business_travel.routes import router as business_travel_router
from .domains.users.routes import router as users_router
from .models import Base
from .util.logger import retrieve_logger

_LOGGER = retrieve_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _LOGGER.info("Application started")

    yield

    await engine.dispose()
    _LOGGER.info("Application stopped")


app = FastAPI(
    title="Meu Inventário",
    description="""Backend service for GHG Protocol emissions inventory management.

## Features

* **Multi-tenant**: Organization-scoped data isolation
* **GHG Protocol**: Scope 1, 2, and 3 emission tracking
* **Server-side calculations**: All emission calculations performed server-side
* **Keycloak Authentication**: OAuth2 Bearer token via Keycloak
* **Public Questionnaires**: Anonymous commuting data collection with rate limiting
* **Reports**: PDF and Excel export of emission inventories
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Mercado Net Zero Team",
        "email": "support@mercadonetzero.com",
    },
    license_info={
        "name": "Proprietary",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
    allow_credentials=True,
)

app.include_router(organizations_router)
app.include_router(users_router)
app.include_router(inventories_router)
app.include_router(mobile_combustion_router)
app.include_router(stationary_combustion_router)
app.include_router(fugitive_router)
app.include_router(effluents_router)
app.include_router(energy_router)
app.include_router(business_travel_router)
app.include_router(commuting_router)
app.include_router(questionnaires_router)
app.include_router(reference_data_router)
app.include_router(reports_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    if settings.remote_debug:
        debugpy.listen(("0.0.0.0", 5680))
        _LOGGER.info("Remote debugging enabled. Listening on port 5680")

    uvicorn.run(app, host=settings.host, port=settings.port)
