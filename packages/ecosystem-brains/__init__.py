# ECOS Ecosystem Brains
# Shared Python libraries for forecasting and optimization across all 13 projects

# This directory name contains a hyphen ("ecosystem-brains"), so it cannot be
# imported as a regular Python package. The relative imports below are only
# valid when this file is imported with a parent package; guard them so the
# file remains importable when a tool (e.g. pytest) inspects it directly.
if __package__:
    from . import forecasting
    from . import solvers
    from . import dispatcher
    from . import checklist

    __all__ = ["forecasting", "solvers", "dispatcher", "checklist"]

__version__ = "1.0.0"
