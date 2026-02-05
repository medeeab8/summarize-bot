import os

# Logging configuration
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "text")  # "text" or "json"
LOG_JSON = os.getenv("LOG_JSON", "false").lower() in {"1", "true", "yes", "on"}
LOG_COLOR = os.getenv("LOG_COLOR", "true").lower() in {"1", "true", "yes", "on"}

# Optional file logging
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "")  # empty disables file logging
LOG_FILE_MAX_BYTES = int(os.getenv("LOG_FILE_MAX_BYTES", "10485760"))  # 10MB
LOG_FILE_BACKUP_COUNT = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

# Extra context toggles
LOG_INCLUDE_PROCESS = os.getenv("LOG_INCLUDE_PROCESS", "false").lower() in {"1", "true", "yes", "on"}
LOG_INCLUDE_THREAD = os.getenv("LOG_INCLUDE_THREAD", "false").lower() in {"1", "true", "yes", "on"}
