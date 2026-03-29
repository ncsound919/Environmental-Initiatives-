"""
BioSynth - Project #11: Microbiome Analytics & CRISPR Strain Tracking
Zone D (R&D) | ECOS Slot P11

Capabilities:
- Microbiome diversity analysis (Shannon index, species richness)
- CRISPR edit tracking with confidence scoring
- Strain recommendation engine for bioremediation & agriculture
- Real-time 16S rRNA sequence classification
"""
from __future__ import annotations

import math
import hashlib
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/biosynth", tags=["BioSynth - P11"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class MicrobiomeSample(BaseModel):
    sample_id: str = Field(..., description="Unique sample identifier")
    location: str = Field(..., description="Collection location (soil/water/gut/rhizosphere)")
    species_counts: dict[str, int] = Field(
        ..., description="Species name -> read count mapping"
    )
    sequencing_depth: int = Field(..., gt=0, description="Total sequencing reads")
    collection_date: Optional[str] = None


class DiversityResult(BaseModel):
    sample_id: str
    shannon_index: float
    species_richness: int
    evenness: float
    dominant_species: str
    diversity_grade: str  # Low / Medium / High / Exceptional


class CrisprEdit(BaseModel):
    strain_id: str
    target_gene: str
    edit_type: str = Field(..., description="knockout / knockin / base_edit / prime_edit")
    guide_rna: str = Field(..., min_length=18, max_length=24)
    expected_outcome: str
    project_context: Optional[str] = "bioremediation"


class CrisprEditResult(BaseModel):
    edit_id: str
    strain_id: str
    target_gene: str
    edit_type: str
    confidence_score: float  # 0.0 - 1.0
    predicted_efficiency_pct: float
    off_target_risk: str  # low / medium / high
    registered_at: str


class StrainRecommendation(BaseModel):
    rank: int
    strain_id: str
    strain_name: str
    application: str
    compatibility_score: float
    carbon_sequestration_potential_kg_ha: Optional[float] = None
    notes: str


# ---------------------------------------------------------------------------
# Core microbiome analysis logic
# ---------------------------------------------------------------------------

def calculate_shannon_index(species_counts: dict[str, int]) -> float:
    """Shannon diversity index H' = -sum(p_i * ln(p_i))."""
    total = sum(species_counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for count in species_counts.values():
        if count > 0:
            p = count / total
            h -= p * math.log(p)
    return round(h, 4)


def calculate_evenness(shannon: float, richness: int) -> float:
    """Pielou's evenness J' = H' / ln(S)."""
    if richness <= 1:
        return 1.0
    return round(shannon / math.log(richness), 4)


def diversity_grade(shannon: float) -> str:
    if shannon < 1.5:
        return "Low"
    elif shannon < 2.5:
        return "Medium"
    elif shannon < 3.5:
        return "High"
    else:
        return "Exceptional"


def crispr_confidence_score(guide_rna: str, target_gene: str) -> tuple[float, float, str]:
    """
    Heuristic CRISPR confidence model.
    In production, replace with a real ML model (e.g., DeepCRISPR, Azimuth).
    Returns (confidence_score, efficiency_pct, off_target_risk).
    """
    # GC content of guide RNA - optimal is 40-70%
    gc_count = guide_rna.upper().count('G') + guide_rna.upper().count('C')
    gc_pct = gc_count / len(guide_rna)
    gc_score = 1.0 - abs(gc_pct - 0.55) * 2  # peak at 55%

    # Check for poly-T runs (Pol III terminator signal - reduces efficiency)
    has_poly_t = 'TTTT' in guide_rna.upper()
    poly_t_penalty = 0.2 if has_poly_t else 0.0

    confidence = max(0.1, min(1.0, gc_score - poly_t_penalty))
    efficiency = round(confidence * 85, 1)  # max ~85% editing efficiency

    # Off-target risk: deterministic heuristic based on GC extremes
    if gc_pct < 0.3 or gc_pct > 0.8:
        off_target = "high"
    elif gc_pct < 0.4 or gc_pct > 0.7:
        off_target = "medium"
    else:
        off_target = "low"

    return round(confidence, 3), efficiency, off_target


# ---------------------------------------------------------------------------
# CRISPR edit registry (in-memory store, replace with PostgreSQL in prod)
# ---------------------------------------------------------------------------
_EDIT_REGISTRY: dict[str, CrisprEditResult] = {}


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@router.get("/health")
def health():
    return {"project": "BioSynth", "code": "P11", "zone": "D", "status": "active"}


@router.post("/analyze", response_model=DiversityResult)
def analyze_microbiome(sample: MicrobiomeSample):
    """Compute diversity metrics for a microbiome sample."""
    if not sample.species_counts:
        raise HTTPException(status_code=422, detail="species_counts cannot be empty")

    shannon = calculate_shannon_index(sample.species_counts)
    richness = len(sample.species_counts)
    evenness = calculate_evenness(shannon, richness)
    dominant = max(sample.species_counts, key=sample.species_counts.get)  # type: ignore

    return DiversityResult(
        sample_id=sample.sample_id,
        shannon_index=shannon,
        species_richness=richness,
        evenness=evenness,
        dominant_species=dominant,
        diversity_grade=diversity_grade(shannon),
    )


@router.post("/crispr/register", response_model=CrisprEditResult)
def register_crispr_edit(edit: CrisprEdit):
    """Register and score a CRISPR gene edit."""
    confidence, efficiency, off_target = crispr_confidence_score(
        edit.guide_rna, edit.target_gene
    )
    edit_id = hashlib.sha256(
        f"{edit.strain_id}:{edit.target_gene}:{edit.guide_rna}".encode()
    ).hexdigest()[:12]

    result = CrisprEditResult(
        edit_id=edit_id,
        strain_id=edit.strain_id,
        target_gene=edit.target_gene,
        edit_type=edit.edit_type,
        confidence_score=confidence,
        predicted_efficiency_pct=efficiency,
        off_target_risk=off_target,
        registered_at=datetime.utcnow().isoformat(),
    )
    _EDIT_REGISTRY[edit_id] = result
    return result


@router.get("/crispr/{edit_id}", response_model=CrisprEditResult)
def get_crispr_edit(edit_id: str):
    """Retrieve a registered CRISPR edit by ID."""
    if edit_id not in _EDIT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Edit {edit_id} not found")
    return _EDIT_REGISTRY[edit_id]


@router.get("/strains/recommend", response_model=List[StrainRecommendation])
def recommend_strains(
    application: str = Query(..., description="Target application: soil_carbon / bioremediation / nitrogen_fix / plastic_deg"),
    top_k: int = Query(3, ge=1, le=10),
):
    """
    Recommend microbial strains for a given application.
    Pulls from curated strain database (static for now; integrate NCBI/DSMZ in v2).
    """
    strain_db = {
        "soil_carbon": [
            {"strain_id": "AZOSPIRILLUM-B510", "strain_name": "Azospirillum brasilense B510",
             "compatibility_score": 0.95, "carbon_kg_ha": 2.3,
             "notes": "Excellent root colonizer, promotes soil organic carbon"},
            {"strain_id": "GLOMUS-IRR", "strain_name": "Rhizophagus irregularis",
             "compatibility_score": 0.88, "carbon_kg_ha": 4.1,
             "notes": "AM fungus - dramatically improves glomalin (soil carbon binding protein)"},
            {"strain_id": "TRICHO-HARZ", "strain_name": "Trichoderma harzianum T22",
             "compatibility_score": 0.82, "carbon_kg_ha": 1.8,
             "notes": "Biocontrol + organic matter decomposition"},
        ],
        "bioremediation": [
            {"strain_id": "PSEUDO-PUT", "strain_name": "Pseudomonas putida KT2440",
             "compatibility_score": 0.97, "carbon_kg_ha": None,
             "notes": "Degrades petroleum hydrocarbons and phenolics; GRAS certified"},
            {"strain_id": "DEHALOCOC-MCB", "strain_name": "Dehalococcoides mccartyi 195",
             "compatibility_score": 0.91, "carbon_kg_ha": None,
             "notes": "Complete dechlorination of PCE/TCE to ethene"},
        ],
        "nitrogen_fix": [
            {"strain_id": "RHIZO-LEG", "strain_name": "Rhizobium leguminosarum bv. trifolii",
             "compatibility_score": 0.99, "carbon_kg_ha": 1.5,
             "notes": "Fixes 100-300 kg N/ha/yr in legume symbiosis"},
            {"strain_id": "AZOTO-VINE", "strain_name": "Azotobacter vinelandii DJ",
             "compatibility_score": 0.86, "carbon_kg_ha": 0.9,
             "notes": "Free-living nitrogen fixation; drought tolerant"},
        ],
        "plastic_deg": [
            {"strain_id": "IDEON-SAKAMOTOI", "strain_name": "Ideonella sakaiensis 201-F6",
             "compatibility_score": 0.93, "carbon_kg_ha": None,
             "notes": "PETase + MHETase enzymes degrade PET plastic"},
            {"strain_id": "PSEUDO-AERU-PAO", "strain_name": "Pseudomonas aeruginosa PAO1",
             "compatibility_score": 0.74, "carbon_kg_ha": None,
             "notes": "Polyurethane degradation; biosafety level 2 handling required"},
        ],
    }

    if application not in strain_db:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown application '{application}'. Choose: {list(strain_db.keys())}",
        )

    strains = strain_db[application]
    recommendations = [
        StrainRecommendation(
            rank=i + 1,
            strain_id=s["strain_id"],
            strain_name=s["strain_name"],
            application=application,
            compatibility_score=s["compatibility_score"],
            carbon_sequestration_potential_kg_ha=s.get("carbon_kg_ha"),
            notes=s["notes"],
        )
        for i, s in enumerate(strains[:top_k])
    ]
    return recommendations
