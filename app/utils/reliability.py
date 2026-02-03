"""
Reliability utilities for the Legal Agent bot.

Provides:
- Retry decorator with exponential backoff
- Circuit breaker pattern
- Error classification
"""

import time
import random
import logging
import functools
from typing import Callable, TypeVar, Any, Tuple, Type

import requests
from telegram.error import (
    NetworkError,
    TimedOut,
    RetryAfter,
    TelegramError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Retryable errors
RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    NetworkError,
    TimedOut,
    ConnectionError,
    TimeoutError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)

# Rate limit errors (need special handling)
RATE_LIMIT_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    RetryAfter,
)


def retry_with_backoff(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = None,
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to delays
        retryable_exceptions: Tuple of exceptions to retry on

    Example:
        @retry_with_backoff(max_retries=3)
        def my_api_call():
            ...
    """
    if retryable_exceptions is None:
        retryable_exceptions = RETRYABLE_EXCEPTIONS

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except RATE_LIMIT_EXCEPTIONS as e:
                    # Handle rate limit with specific wait time
                    if isinstance(e, RetryAfter):
                        wait_time = e.retry_after + 1
                        logger.warning(
                            f"Rate limited on {func.__name__}, waiting {wait_time}s"
                        )
                        time.sleep(wait_time)
                        continue

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    # Add jitter
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.1f}s: {e}"
                    )
                    time.sleep(delay)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            return None

        return wrapper
    return decorator


def async_retry_with_backoff(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = None,
):
    """
    Async version of retry_with_backoff decorator.
    """
    import asyncio

    if retryable_exceptions is None:
        retryable_exceptions = RETRYABLE_EXCEPTIONS

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except RATE_LIMIT_EXCEPTIONS as e:
                    if isinstance(e, RetryAfter):
                        wait_time = e.retry_after + 1
                        logger.warning(
                            f"Rate limited on {func.__name__}, waiting {wait_time}s"
                        )
                        await asyncio.sleep(wait_time)
                        continue

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}"
                        )
                        raise

                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.1f}s: {e}"
                    )
                    await asyncio.sleep(delay)

            if last_exception:
                raise last_exception
            return None

        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.

    States:
    - CLOSED: Normal operation, requests go through
    - OPEN: Failing, requests are blocked
    - HALF_OPEN: Testing if service recovered
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0
        self._half_open_calls = 0

    @property
    def state(self) -> str:
        if self._state == self.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = self.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    def record_success(self):
        """Record a successful call."""
        if self._state == self.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                # Recovered
                self._state = self.CLOSED
                self._failure_count = 0
        else:
            self._failure_count = 0

    def record_failure(self):
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = self.OPEN
            logger.warning(
                f"Circuit breaker opened after {self._failure_count} failures"
            )

    def can_execute(self) -> bool:
        """Check if a call can be executed."""
        return self.state != self.OPEN

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Use as decorator."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not self.can_execute():
                raise RuntimeError(
                    f"Circuit breaker is open for {func.__name__}"
                )

            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise

        return wrapper


def is_retryable_error(exception: Exception) -> bool:
    """Check if an exception is retryable."""
    return isinstance(exception, RETRYABLE_EXCEPTIONS + RATE_LIMIT_EXCEPTIONS)


def classify_error(exception: Exception) -> str:
    """
    Classify an error for logging/monitoring.

    Returns:
        Error category string
    """
    if isinstance(exception, NetworkError):
        return "network"
    elif isinstance(exception, TimedOut):
        return "timeout"
    elif isinstance(exception, RetryAfter):
        return "rate_limit"
    elif isinstance(exception, TelegramError):
        return "telegram"
    elif isinstance(exception, (ConnectionError, requests.exceptions.ConnectionError)):
        return "connection"
    elif isinstance(exception, (TimeoutError, requests.exceptions.Timeout)):
        return "timeout"
    else:
        return "unknown"
