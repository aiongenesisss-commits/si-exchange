from fastapi import FastAPI

app = FastAPI(
    title="SI Exchange",
    description="AI-assisted digital asset exchange demo",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "name": "SI Exchange",
        "status": "running",
        "mode": "DEMO",
        "message": "Welcome to SI Exchange",
        "real_trading_enabled": False,
        "deposits_enabled": False,
        "withdrawals_enabled": False,
    }


@app.get("/health")
def health():
    return {"status": "ok", "mode": "DEMO"}


@app.get("/ready")
def readiness():
    return {
        "status": "demo_only",
        "database_connected": False,
        "real_trading_enabled": False,
        "deposits_enabled": False,
        "withdrawals_enabled": False,
    }
