"""
Pytest configuration for the ECOS API Gateway smoke tests.

Heavy ML dependencies (prophet, torch, ortools, pulp) are stubbed here so the
gateway module imports without a full ML toolchain. These stubs are sufficient
for exercising HTTP routes; the real ML modules are covered by the
ecosystem-brains test suite.
"""
import sys
import types
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "packages", "ecosystem-brains"
    ),
)


def _install_stubs() -> None:
    # prophet
    prophet = types.ModuleType("prophet")
    class _FakeProphet:
        def __init__(self, *args, **kwargs):
            pass
    prophet.Prophet = _FakeProphet
    sys.modules.setdefault("prophet", prophet)

    # torch
    torch = types.ModuleType("torch")
    nn = types.ModuleType("torch.nn")
    class _FakeModule:
        pass
    class _FakeLinear:
        def __init__(self, *args, **kwargs):
            pass
    class _FakeLSTM:
        def __init__(self, *args, **kwargs):
            pass
    nn.Module = _FakeModule
    nn.Linear = _FakeLinear
    nn.LSTM = _FakeLSTM
    torch.nn = nn
    torch.zeros = lambda *args, **kwargs: None
    torch.randn = lambda *args, **kwargs: None
    sys.modules.setdefault("torch", torch)
    sys.modules.setdefault("torch.nn", nn)

    # ortools
    ortools = types.ModuleType("ortools")
    ls = types.ModuleType("ortools.linear_solver")
    class _Solver:
        @staticmethod
        def CreateSolver(name):
            raise NotImplementedError("stub solver")
        def NewIntVar(self, *a, **k): pass
        def NewNumVar(self, *a, **k): pass
        def Add(self, *a, **k): pass
        def Minimize(self, *a, **k): pass
        def Maximize(self, *a, **k): pass
        def Solve(self): return 0
        def Objective(self): return None
    ls.pywraplp = _Solver
    ortools.linear_solver = ls
    sys.modules.setdefault("ortools", ortools)
    sys.modules.setdefault("ortools.linear_solver", ls)

    # pulp
    pulp = types.ModuleType("pulp")
    class _Var:
        def __init__(self, *a, **k): pass
        def __add__(self, o): return self
        def __mul__(self, o): return self
    class _Prob:
        def __init__(self, *a, **k): pass
    pulp.LpProblem = _Prob
    pulp.LpMinimize = "LpMinimize"
    pulp.LpVariable = _Var
    pulp.lpSum = lambda *a: a[0]
    pulp.LpStatus = {"Optimal": "Optimal"}
    sys.modules.setdefault("pulp", pulp)


_install_stubs()

# Force rate limiter onto its in-memory fallback (no Redis server in CI).
import middleware.rate_limit as _rl  # noqa: E402
_rl.REDIS_AVAILABLE = False