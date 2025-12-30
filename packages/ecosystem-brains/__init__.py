# ECOS Ecosystem Brains
# Shared Python libraries for forecasting and optimization across all 13 projects

from .forecasting import forecast
from .solvers import optimize
from .dispatcher import dispatch

__version__ = "1.0.0"

__all__ = ["forecast", "optimize", "dispatch"]
