from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from . import config as cfg


class LoggingSettings(BaseModel):
	level: str = Field(default=cfg.LOG_LEVEL)
	file_path: str = Field(default=cfg.LOG_FILE_PATH)
	file_max_bytes: int = Field(default=cfg.LOG_FILE_MAX_BYTES)
	file_backup_count: int = Field(default=cfg.LOG_FILE_BACKUP_COUNT)

	@field_validator("level")
	@classmethod
	def normalize_level(cls, value: str) -> str:
		return value.upper().strip()


def configure_logging(settings: Optional[LoggingSettings] = None) -> LoggingSettings:
	settings = settings or LoggingSettings()

	root = logging.getLogger()
	root.setLevel(settings.level)
	root.handlers.clear()

	formatter = logging.Formatter(
		fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)

	console = logging.StreamHandler(stream=sys.stdout)
	console.setFormatter(formatter)
	root.addHandler(console)

	if settings.file_path:
		file_handler = RotatingFileHandler(
			settings.file_path,
			maxBytes=settings.file_max_bytes,
			backupCount=settings.file_backup_count,
		)
		file_handler.setFormatter(formatter)
		root.addHandler(file_handler)

	return settings
