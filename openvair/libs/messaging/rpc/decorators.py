"""Decorators for RPC input/output validation and serialization (sync only).

`rpc_io` validates function arguments per annotations, optionally validates
the return value against the annotated return type, and serializes the
result into plain Python structures (dict/list/primitives) suitable for
transport.

Main features:
    - Input validation via `pydantic.validate_call`.
    - Optional output validation via return annotation.
    - Serialization to dict/list/primitive via `pydantic.TypeAdapter`.
    - Translation of `ValidationError` into `MessagingPayloadError`.

Public API:
    - rpc_io: decorator for sync functions used over RPC.
"""

from __future__ import annotations

import functools
from typing import (
    Type,
    Literal,
    TypeVar,
    Callable,
    NoReturn,
    cast,
    get_type_hints,
)
from dataclasses import dataclass

from pydantic import TypeAdapter, ValidationError, validate_call
from typing_extensions import ParamSpec

from openvair.libs.log import get_logger
from openvair.libs.messaging.exceptions import MessagingPayloadError

LOG = get_logger(__name__)

DumpMode = Literal['python', 'json']

P = ParamSpec('P')
R_co = TypeVar('R_co', covariant=True)

SyncCallable = Callable[P, R_co]


@dataclass(frozen=True)
class _Config:
    """Configuration for `rpc_io`.

    Attributes:
        by_alias (bool): Use field aliases from Pydantic models when dumping.
        exclude_none (bool): Exclude fields with `None` values on dump.
        dump_mode (DumpMode): "python" for pure Python structures; "json"
            for JSON-compatible types.
        translate_errors (bool): If True, translate `ValidationError` into
            `MessagingPayloadError`; otherwise re-raise original error.
    """

    by_alias: bool
    exclude_none: bool
    dump_mode: DumpMode
    translate_errors: bool


def _process_value(
    adapter: TypeAdapter[object],
    value: object,
    cfg: _Config,
) -> object:
    """Serialize return value according to the annotated return type."""
    return adapter.dump_python(
        value,
        by_alias=cfg.by_alias,
        exclude_none=cfg.exclude_none,
        mode=cfg.dump_mode,
    )


def _handle_validation_error(
    exc: ValidationError, *, translate: bool
) -> NoReturn:
    """Translate or re-raise pydantic validation errors."""
    if translate:
        LOG.warning('RPC payload validation error: %s', exc)
        raise MessagingPayloadError(str(exc)) from exc
    raise exc


def rpc_io(
    *,
    validate_out: bool = False,
    by_alias: bool = True,
    exclude_none: bool = False,
    dump_mode: DumpMode = 'json',
    translate_errors: bool = True,
) -> Callable[[SyncCallable[P, R_co]], SyncCallable[P, R_co]]:
    """Validate args/return and serialize return value for RPC (sync only).

    This decorator validates input arguments via annotations, optionally
    validates the return value against the function's annotated return type,
    and finally serializes the returned value to plain Python data using the
    same return annotation as a schema.

    Args:
        validate_out: Validate and coerce the returned value to the annotated
            type.
        by_alias: Use Pydantic field aliases when dumping.
        exclude_none: Exclude fields with `None` values during dump.
        dump_mode: Serialization mode ("python" or "json").
        translate_errors: Convert `ValidationError` to `MessagingPayloadError`.

    Returns:
        A decorator preserving the original function signature (sync).
    """
    cfg = _Config(
        by_alias=by_alias,
        exclude_none=exclude_none,
        dump_mode=dump_mode,
        translate_errors=translate_errors,
    )

    def outer(func: SyncCallable[P, R_co]) -> SyncCallable[P, R_co]:
        # pydantic decorates the function to validate
        # inputs (and optionally output)
        validated = validate_call(validate_return=validate_out)(func)

        # Use the original return annotation as a schema for serialization
        hints = get_type_hints(func)
        return_type: Type[object] = hints.get('return', object)
        adapter: TypeAdapter[object] = TypeAdapter(return_type)

        @functools.wraps(validated)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            try:
                raw = validated(*args, **kwargs)
                dumped = _process_value(adapter, raw, cfg)
                # For static typing we keep the original return type R_co,
                # while at runtime we return the serialized (transport) shape.
                return cast(R_co, dumped)
            except ValidationError as exc:
                _handle_validation_error(exc, translate=cfg.translate_errors)

        return wrapper

    return outer
