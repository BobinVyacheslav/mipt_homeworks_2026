import functools
import json
from datetime import UTC, datetime, timedelta
from typing import Any, Never, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


def _is_invalid_positive_integer(value: object) -> bool:
    return isinstance(value, bool) or not isinstance(value, int) or value <= 0


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime) -> None:
        self.func_name = func_name
        self.block_time = block_time
        super().__init__(TOO_MUCH)


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        errors = self._validate_args(critical_count, time_to_recover)
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)
        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.failures_count = 0
        self.blocked_at: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            func_name = f"{func.__module__}.{func.__name__}"
            now = datetime.now(UTC)
            self._unlock_if_recovered(now)
            self._raise_if_blocked(func_name)
            try:
                result = func(*args, **kwargs)
            except self.triggers_on as error:
                self._handle_failure(func_name, now, error)
            else:
                self.failures_count = 0
                return result

        return wrapper

    @classmethod
    def _validate_args(cls, critical_count: object, time_to_recover: object) -> list[ValueError]:
        errors: list[ValueError] = []
        if _is_invalid_positive_integer(critical_count):
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if _is_invalid_positive_integer(time_to_recover):
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        return errors

    def _unlock_if_recovered(self, now: datetime) -> None:
        if self.blocked_at is None:
            return
        recovery_deadline = self.blocked_at + timedelta(seconds=self.time_to_recover)
        if now >= recovery_deadline:
            self.blocked_at = None
            self.failures_count = 0

    def _raise_if_blocked(self, func_name: str) -> None:
        if self.blocked_at is not None:
            raise BreakerError(func_name, self.blocked_at)

    def _handle_failure(self, func_name: str, now: datetime, error: Exception) -> Never:
        self.failures_count += 1
        if self.failures_count < self.critical_count:
            raise error
        self.blocked_at = now
        raise BreakerError(func_name, self.blocked_at) from error


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
