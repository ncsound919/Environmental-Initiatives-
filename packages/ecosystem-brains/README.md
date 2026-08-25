# ecosystem-brains

Shared Python libraries for ECOS — forecasting, optimization solvers, dispatch,
and readiness checklists across all 13 projects.

## Modules

- `forecasting` — stream flow, solar irradiance, humidity, bulb failure prediction
- `solvers` — nutrient cycle, AWG schedule, geothermal flow, fungal match optimization
- `dispatcher` — cross-project coordination actions
- `checklist` — Level 1–4 readiness phase execution
- `carbon_credits` — carbon credit computation (IPCC AR6 methodology, Verra VCS + Gold Standard pricing)

## Development

```bash
pip install -e ".[dev]"
pytest
```

Heavy ML dependencies (`ortools`, `prophet`, `torch`, `xgboost`) are required to
run the solver/forecasting tests. See `apps/api-gateway/requirements.txt` for the
pinned set used by the API gateway.
