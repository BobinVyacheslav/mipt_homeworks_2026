from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, TypeVar, cast, overload

from part4_oop.interfaces import Policy, Storage

if TYPE_CHECKING:
    from collections.abc import Callable

K = TypeVar("K")
V = TypeVar("V")


class _PropertyCache[V](Protocol):
    def exists(self, key: str) -> bool: ...
    def get(self, key: str) -> V | None: ...
    def set(self, key: str, value: V) -> None: ...


class _HasPropertyCache[V](Protocol):
    cache: _PropertyCache[V]


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        if self.exists(key):
            self._data.pop(key)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            return
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if not self._order or len(self._order) < self.capacity:
            return None
        return self._order[0]

    def remove_key(self, key: K) -> None:
        for i in self._order:
            if i == key:
                self._order.remove(i)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)
            return
        index = 0
        for position, current_key in enumerate(self._order):
            if current_key == key:
                index = position
                break
        found_key = self._order.pop(index)
        self._order.append(found_key)

    def get_key_to_evict(self) -> K | None:
        if not self._order or len(self._order) < self.capacity:
            return None
        return self._order[0]

    def remove_key(self, key: K) -> None:
        for i in self._order:
            if i == key:
                self._order.remove(i)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _order: list[K] = field(default_factory=list, init=False)
    _last_inserted: K | None = field(default=None, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_counter[key] = 1
            self._order.append(key)
            self._last_inserted = key
            return
        self._key_counter[key] += 1
        self._last_inserted = None

    def get_key_to_evict(self) -> K | None:
        if not self._key_counter or len(self._key_counter) <= self.capacity:
            return None

        candidates = self._get_eviction_candidates()

        if not candidates:
            return None

        min_count = min(self._key_counter[key] for key in candidates)
        for key in candidates:
            if self._key_counter[key] == min_count:
                return key
        return None

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)
        if key in self._order:
            self._order.remove(key)
        if self._last_inserted == key:
            self._last_inserted = None

    def clear(self) -> None:
        self._key_counter.clear()
        self._order.clear()
        self._last_inserted = None

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0

    def _get_eviction_candidates(self) -> list[K]:
        candidates: list[K] = []
        for key in self._order:
            if key == self._last_inserted:
                continue
            if key not in self._key_counter:
                continue
            candidates.append(key)
        return candidates


class MIPTCache[K, V]:
    storage: Storage[K, V]
    policy: Policy[K]

    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.policy.register_access(key)
        self.storage.set(key, value)
        key_to_evict = self.policy.get_key_to_evict()
        if key_to_evict is not None:
            self.storage.remove(key_to_evict)
            self.policy.remove_key(key_to_evict)

    def get(self, key: K) -> V | None:
        if self.exists(key):
            self.policy.register_access(key)
            return self.storage.get(key)
        return None

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[T, V]:
    def __init__(self, func: Callable[[T], V]) -> None:
        self.func = func
        self.key = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.key = name

    @overload
    def __get__(
        self,
        instance: None,
        owner: type[T],
    ) -> CachedProperty[T, V]: ...

    @overload
    def __get__(self, instance: T, owner: type[T]) -> V: ...

    def __get__(
        self,
        instance: T | None,
        owner: type[T],
    ) -> CachedProperty[T, V] | V:
        if instance is None:
            return self
        cache = cast("_HasPropertyCache[V]", instance).cache
        if cache.exists(self.key):
            cached_value = cache.get(self.key)
            if cached_value is not None:
                return cached_value
        value = self.func(instance)
        cache.set(self.key, value)
        return value
