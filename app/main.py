from fastapi import FastAPI

from app.report.router import router as report_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Report Export Service",
        version="1.0.0",
    )
    app.include_router(report_router)
    return app


app = create_app()
