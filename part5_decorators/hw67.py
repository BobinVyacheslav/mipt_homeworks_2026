import functools
import json
from datetime import UTC, datetime, timedelta
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


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
        errors: list[ValueError] = []
        if critical_count <= 0 or type(critical_count) is not int:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if time_to_recover <= 0 or type(time_to_recover) is not int:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
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
            if self.blocked_at is not None:
                recovery_deadline = self.blocked_at + timedelta(seconds=self.time_to_recover)
                if now < recovery_deadline:
                    raise BreakerError(func_name, self.blocked_at)
                self.blocked_at = None
                self.failures_count = 0
            try:
                result = func(*args, **kwargs)
            except self.triggers_on as e:
                self.failures_count += 1
                if self.failures_count < self.critical_count:
                    raise
                self.blocked_at = now
                raise BreakerError(func_name, self.blocked_at) from e
            self.failures_count = 0
            return result

        return wrapper


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
