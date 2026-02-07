# -*- coding: utf-8 -*-
"""
Sandbox Paketi - Güvenli kod çalıştırma ortamı.
"""
from sandbox.executor import run_safe
from sandbox.security import (
    SandboxSecurityError,
    get_safe_builtins,
    get_sandbox_scope,
    ALLOWED_MODULES,
)
from sandbox.guards import (
    ResourceLimitError,
    MemoryLimitError,
    CPULimitError,
    OperationLimitError,
    RecursionLimitError,
    ResourceGuardian,
    MemoryGuard,
    CPUGuard,
    LoopGuard,
    RecursionGuard,
)
from sandbox.vfs import MockFileSystem, MockFileHandle

__all__ = [
    # Executor
    'run_safe',
    # Security
    'SandboxSecurityError',
    'get_safe_builtins',
    'get_sandbox_scope',
    'ALLOWED_MODULES',
    # Guards
    'ResourceLimitError',
    'MemoryLimitError',
    'CPULimitError',
    'OperationLimitError',
    'RecursionLimitError',
    'ResourceGuardian',
    'MemoryGuard',
    'CPUGuard',
    'LoopGuard',
    'RecursionGuard',
    # VFS
    'MockFileSystem',
    'MockFileHandle',
]
