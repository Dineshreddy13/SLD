import os

class Settings:
    PROJECT_NAME: str = "Sign Language Detection API"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    MAX_NUM_HANDS: int = 2
    MIN_DETECTION_CONFIDENCE: float = 0.5
    MIN_TRACKING_CONFIDENCE: float = 0.5

settings = Settings()
