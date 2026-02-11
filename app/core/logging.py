from __future__ import annotations

import logging
import re
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


class ColorFormatter(logging.Formatter):
	COLORS = {
		"DEBUG": "\x1b[36m",
		"INFO": "\x1b[32m",
		"WARNING": "\x1b[33m",
		"ERROR": "\x1b[31m",
		"CRITICAL": "\x1b[35m",
	}
	STATUS_COLORS = {
		"1xx": "\x1b[36m",
		"2xx": "\x1b[32m",
		"3xx": "\x1b[34m",
		"4xx": "\x1b[33m",
		"5xx": "\x1b[31m",
	}
	RESET = "\x1b[0m"
	UVICORN_ERROR_LOGGER = "uvicorn.error"
	UVICORN_LOGGER_ALIAS = "uvicorn"

	def format(self, record: logging.LogRecord) -> str:
		original_name = record.name
		if record.name == self.UVICORN_ERROR_LOGGER:
			record.name = self.UVICORN_LOGGER_ALIAS
		levelname = record.levelname
		if levelname in self.COLORS:
			record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
			try:
				formatted = super().format(record)
			finally:
				record.levelname = levelname
				record.name = original_name
			return self._colorize_status_codes(formatted)
		formatted = super().format(record)
		record.name = original_name
		return self._colorize_status_codes(formatted)

	def _colorize_status_codes(self, text: str) -> str:
		def repl(match: re.Match[str]) -> str:
			code = match.group(1)
			bucket = f"{code[0]}xx"
			color = self.STATUS_COLORS.get(bucket)
			if not color:
				return code
			return f"{color}{code}{self.RESET}"

		return re.sub(r"\b([1-5]\d{2})\b", repl, text)


class UvicornErrorNameFilter(logging.Filter):
	UVICORN_ERROR_LOGGER = "uvicorn.error"
	UVICORN_LOGGER_ALIAS = "uvicorn"

	def filter(self, record: logging.LogRecord) -> bool:
		if record.name == self.UVICORN_ERROR_LOGGER:
			record.name = self.UVICORN_LOGGER_ALIAS
		return True


def configure_logging(settings: Optional[LoggingSettings] = None) -> LoggingSettings:
	settings = settings or LoggingSettings()

	root = logging.getLogger()
	root.setLevel(settings.level)
	root.handlers.clear()
	root.propagate = False

	format_string = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
	date_format = "%Y-%m-%d %H:%M:%S"

	console_formatter = ColorFormatter(
		fmt=format_string,
		datefmt=date_format,
	)
	file_formatter = logging.Formatter(
		fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)

	console = logging.StreamHandler(stream=sys.stdout)
	console.setFormatter(console_formatter)
	console.addFilter(UvicornErrorNameFilter())
	root.addHandler(console)

	if settings.file_path:
		file_handler = RotatingFileHandler(
			settings.file_path,
			maxBytes=settings.file_max_bytes,
			backupCount=settings.file_backup_count,
		)
		file_handler.setFormatter(file_formatter)
		file_handler.addFilter(UvicornErrorNameFilter())
		root.addHandler(file_handler)

	for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
		logger = logging.getLogger(logger_name)
		logger.handlers = root.handlers
		logger.setLevel(settings.level)
		logger.propagate = False

	return settings
