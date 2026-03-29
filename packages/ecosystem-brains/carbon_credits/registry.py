"""
ECOS Carbon Credit Registry Integration
Connects to Verra VCS and Gold Standard APIs for automated carbon credit
monetization from RegeneraFarm (P03), SolarShare (P12), MicroHydro (P13),
ThermalGrid (P10), and BioSynth (P11).

In production: replace stub HTTP calls with real API credentials from
https://registry.verra.org/app/search/VCS and https://registry.goldstandard.org
"""
from __future__ import annotations

import os
import math
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date

# Optional: real HTTP client for production API calls
try:
    import httpx
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False


# ---------------------------------------------------------------------------
# Carbon accounting constants (IPCC AR6 / Gold Standard methodology)
# ---------------------------------------------------------------------------

# CO2e emission factors
EMISSION_FACTOR_GRID_KWH = 0.386    # kg CO2e per kWh (US average grid, EPA eGRID 2023)
EMISSION_FACTOR_NATURAL_GAS = 2.204  # kg CO2e per m3 natural gas combusted
EMISSION_FACTOR_DIESEL = 2.679       # kg CO2e per liter diesel
SOIL_CARBON_FACTOR_HA_YR = 1.5      # tonnes CO2e per hectare per year (regenerative ag baseline)

# Carbon credit market prices (USD per tonne CO2e) - update periodically
CARBON_PRICES = {
    "verra_vcs": 12.50,      # Verra VCS spot price (voluntary market)
    "gold_standard": 18.00, # Gold Standard premium
    "california_cap": 35.00, # California Cap & Trade
    "eu_ets": 65.00,         # EU ETS (compliance market)
}


@dataclass
class CarbonEvent:
    """A carbon reduction or sequestration event from an ECOS project."""
    project_id: int
    project_code: str
    event_type: str        # solar_gen / hydro_gen / geothermal_saving / soil_carbon / bio_carbon
    quantity_kwh_or_kg: float
    unit: str              # kwh / kg / ha / tonne_co2e
    timestamp: datetime = field(default_factory=datetime.utcnow)
    methodology: str = "IPCC_AR6"


@dataclass
class CarbonCredit:
    """Calculated carbon credit from an event."""
    event: CarbonEvent
    tonnes_co2e_avoided: float
    tonnes_co2e_sequestered: float
    total_tonnes_co2e: float
    estimated_value_usd: dict[str, float]   # market -> USD value
    verra_methodology: Optional[str] = None
    gold_standard_methodology: Optional[str] = None
    verification_status: str = "unverified"  # unverified / pending / verified


# ---------------------------------------------------------------------------
# Carbon calculation engine
# ---------------------------------------------------------------------------

def calculate_carbon_credit(event: CarbonEvent) -> CarbonCredit:
    """
    Calculate carbon credits for an ECOS project event.
    Returns a CarbonCredit object with tonne CO2e and market value estimates.
    """
    tonnes_avoided = 0.0
    tonnes_sequestered = 0.0
    verra_method = None
    gs_method = None

    if event.event_type == "solar_gen":  # SolarShare P12
        # Grid displacement methodology
        kg_avoided = event.quantity_kwh_or_kg * EMISSION_FACTOR_GRID_KWH
        tonnes_avoided = kg_avoided / 1000.0
        verra_method = "VM0038 - Renewable Energy Generation"
        gs_method = "GS-RE-001"

    elif event.event_type == "hydro_gen":  # MicroHydro P13
        kg_avoided = event.quantity_kwh_or_kg * EMISSION_FACTOR_GRID_KWH
        tonnes_avoided = kg_avoided / 1000.0
        verra_method = "VM0038 - Renewable Energy Generation (Hydro)"
        gs_method = "GS-RE-002"

    elif event.event_type == "geothermal_saving":  # ThermalGrid P10
        # Heat displaced from natural gas boiler
        # 1 kWh thermal = ~0.34 m3 gas equivalent at 80% efficiency
        m3_gas_displaced = (event.quantity_kwh_or_kg / 3.6) * 0.34
        kg_avoided = m3_gas_displaced * EMISSION_FACTOR_NATURAL_GAS
        tonnes_avoided = kg_avoided / 1000.0
        verra_method = "AMS-I.C. - Thermal Energy for User"

    elif event.event_type == "soil_carbon":  # RegeneraFarm P03
        # Regenerative agriculture soil carbon sequestration
        # quantity = hectares under regenerative management
        ha = event.quantity_kwh_or_kg
        tonnes_sequestered = ha * SOIL_CARBON_FACTOR_HA_YR
        verra_method = "VM0042 - Methodology for Improved Agricultural Land Management"
        gs_method = "GS-AFOLU-001"

    elif event.event_type == "bio_carbon":  # BioSynth P11 (microbial carbon)
        # Microbially-enhanced soil carbon (conservative 0.5 t/ha)
        ha = event.quantity_kwh_or_kg
        tonnes_sequestered = ha * 0.5
        verra_method = "VM0042 - Improved Agricultural Land Management (Microbial)"

    elif event.event_type == "tonne_co2e_direct":  # Pre-calculated input
        tonnes_avoided = event.quantity_kwh_or_kg

    total = tonnes_avoided + tonnes_sequestered

    # Calculate market values
    estimated_values = {
        market: round(total * price, 2)
        for market, price in CARBON_PRICES.items()
    }

    return CarbonCredit(
        event=event,
        tonnes_co2e_avoided=round(tonnes_avoided, 4),
        tonnes_co2e_sequestered=round(tonnes_sequestered, 4),
        total_tonnes_co2e=round(total, 4),
        estimated_value_usd=estimated_values,
        verra_methodology=verra_method,
        gold_standard_methodology=gs_method,
    )


def calculate_portfolio_credits(events: list[CarbonEvent]) -> dict:
    """
    Aggregate carbon credits across all ECOS projects.
    Returns portfolio summary with total tonnes CO2e and market values.
    """
    credits = [calculate_carbon_credit(e) for e in events]
    total_avoided = sum(c.tonnes_co2e_avoided for c in credits)
    total_sequestered = sum(c.tonnes_co2e_sequestered for c in credits)
    total = total_avoided + total_sequestered

    return {
        "total_credits": len(credits),
        "total_tonnes_co2e_avoided": round(total_avoided, 3),
        "total_tonnes_co2e_sequestered": round(total_sequestered, 3),
        "total_tonnes_co2e": round(total, 3),
        "portfolio_value_usd": {
            market: round(total * price, 2)
            for market, price in CARBON_PRICES.items()
        },
        "credits_by_project": [
            {
                "project_code": c.event.project_code,
                "event_type": c.event.event_type,
                "total_tonnes_co2e": c.total_tonnes_co2e,
                "verra_value_usd": c.estimated_value_usd.get("verra_vcs", 0),
            }
            for c in credits
        ],
    }


# ---------------------------------------------------------------------------
# Verra / Gold Standard Registry API stubs
# Replace these with real API calls using your registry credentials.
# ---------------------------------------------------------------------------

async def submit_verra_vcs_project(
    project_name: str,
    methodology: str,
    tonnes_co2e: float,
    verification_body: str = "pending",
) -> dict:
    """
    Submit a VCS project to the Verra registry.
    Stub - replace with: POST https://registry.verra.org/mymodule/rpt/myRpt.asp
    Requires: Verra Registry Account + API key in VERRA_API_KEY env var.
    """
    api_key = os.getenv("VERRA_API_KEY")
    if not api_key:
        # Return stub response for development
        return {
            "status": "stub",
            "message": "Set VERRA_API_KEY to enable real Verra registry submission",
            "project_name": project_name,
            "methodology": methodology,
            "tonnes_co2e": tonnes_co2e,
            "estimated_value_usd": round(tonnes_co2e * CARBON_PRICES["verra_vcs"], 2),
        }
    # Production: replace with real API call
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         "https://api.verra.org/v1/projects",
    #         headers={"Authorization": f"Bearer {api_key}"},
    #         json={"name": project_name, "methodology": methodology, ...}
    #     )
    #     return response.json()
    return {"status": "not_implemented", "note": "Implement real Verra API call here"}


async def submit_gold_standard_project(
    project_name: str,
    methodology: str,
    tonnes_co2e: float,
) -> dict:
    """
    Submit a Gold Standard project.
    Stub - replace with Gold Standard API when account is provisioned.
    Requires: GOLD_STANDARD_API_KEY env var.
    """
    api_key = os.getenv("GOLD_STANDARD_API_KEY")
    if not api_key:
        return {
            "status": "stub",
            "message": "Set GOLD_STANDARD_API_KEY to enable Gold Standard submission",
            "project_name": project_name,
            "tonnes_co2e": tonnes_co2e,
            "estimated_value_usd": round(tonnes_co2e * CARBON_PRICES["gold_standard"], 2),
        }
    return {"status": "not_implemented", "note": "Implement real Gold Standard API call here"}
