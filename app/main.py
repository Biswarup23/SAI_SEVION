from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base
from app.api.v1.router import api_router
from dotenv import load_dotenv
from app.models.feedback import Feedback  # noqa: F401

# Import models so SQLAlchemy registers them
from app.models.user import User  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from fastapi import FastAPI
from app.api.v1.routes.polish import router as polish_router
# import app.db.base_imports  # ✅ must happen before create_all
from app.db.session import engine
from app.db.base import Base
import app.db.base_imports  # ✅ must happen before create_all

Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI()
app.include_router(polish_router, prefix="/api/v1")

def create_app() -> FastAPI:
    # app = FastAPI(title="SAI Devion Backend", version="1.0.0")

    app = FastAPI(title="SAI Devion Backend", version="1.0.0", debug=True)  # <-- add debug=True


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten later
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)
    app.include_router(api_router)

    @app.get("/")
    def root():
        return {"status": "ok"}

    return app

app = create_app()
