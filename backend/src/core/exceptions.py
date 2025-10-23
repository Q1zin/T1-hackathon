"""Кастомные исключения приложения."""


class CodeMetricsException(Exception):
    """Базовое исключение для приложения."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(CodeMetricsException):
    """Ошибка конфигурации."""

    pass


class DataCollectionError(CodeMetricsException):
    """Ошибка при сборе данных."""

    pass


class APIClientError(CodeMetricsException):
    """Ошибка при работе с API."""

    pass


class StorageError(CodeMetricsException):
    """Ошибка при работе с хранилищем."""

    pass


class MetricsCalculationError(CodeMetricsException):
    """Ошибка при расчете метрик."""

    pass


class AnalyticsError(CodeMetricsException):
    """Ошибка при выполнении аналитики."""

    pass


class ValidationError(CodeMetricsException):
    """Ошибка валидации данных."""

    pass


class NotFoundError(CodeMetricsException):
    """Сущность не найдена."""

    pass
