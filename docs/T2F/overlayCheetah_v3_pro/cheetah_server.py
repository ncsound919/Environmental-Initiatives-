#!/usr/bin/env python3
"""
Cheetah Server — FastAPI bridge exposing Cheetah V3 Pro+ (agent, audit,
Recourse) over HTTP.

This is the server Deepseek Harness `cheetah.ts` expects at CHEETAH_URL
(default http://127.0.0.1:4120) with `GET /health`, `POST /generate`,
`POST /build`. Those three endpoints are implemented compatibly; everything
else is new in v4:

- POST /agent/read, /agent/search, /agent/plan  (repo-aware coding agent)
- POST /audit                                    (security + correctness)
- POST /recourse/verify, /recourse/heal, /recourse/promote, GET /recourse/status

Run:  python cheetah_server.py            (serves :4120)
      python cheetah_server.py --port 4120
Requires: fastapi, uvicorn (both in requirements.txt).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from cheetah_agent import Workspace, run_coding_task
from cheetah_audit import audit_files, audit_workspace
from cheetah_scaffold import build_scaffold, bootstrap_scaffold, SHAPES
from cheetah_schema import build_crud_plan, FRAMEWORKS as SCHEMA_FRAMEWORKS
from cheetah_component import (
    generate_component, generate_components_for_model,
    PRIMITIVES as COMPONENT_PRIMITIVES, MODEL_KINDS as COMPONENT_MODEL_KINDS,
)
from cheetah_fixes import plan_fixes, apply_fixes
from cheetah_tests import synthesize_tests_for_file
from cheetah_templates import generate_for_goal, generate_template, KINDS
from cheetah_context import build_context
from cheetah_jev import decide_scaffold
from cheetah_gates import GATES, detect_toolchain, verify_workspace
from recourse_bridge import (
    DEFAULT_RECOURSE_URL, PromotionLedger, RecourseClient,
    full_promotion_pipeline,
)

VERSION = "4.1.0-server"
DEFAULT_PORT = 4120

if FASTAPI_AVAILABLE:
    app = FastAPI(title="Overlay Cheetah V3 Pro+",
                  version=VERSION)

    # -- compat models (cheetah.ts) --------------------------------------
    class GenerateRequest(BaseModel):
        name: str = "axiom-build"
        project_type: str = "Full-Stack Platform"
        description: str = ""
        enrich: bool = False

    class BuildRequest(BaseModel):
        yaml_content: str
        target_dir: str = "out"

    # -- agent / audit / recourse models -----------------------------------
    class AgentReadRequest(BaseModel):
        root: str
        path: str

    class AgentSearchRequest(BaseModel):
        root: str
        pattern: str
        glob: str = "**/*.py"
        limit: int = 100

    class AgentPlanRequest(BaseModel):
        root: str
        plan: List[Dict[str, Any]]

    class AuditRequest(BaseModel):
        files: Optional[Dict[str, str]] = None
        root: Optional[str] = None
        glob: str = "**/*.py"
        strict: bool = True
        run_tests: bool = False

    class VerifyRequest(BaseModel):
        sourceCode: str
        testSuiteCode: str = ""
        domain: str = "coding"

    class HealRequest(BaseModel):
        toolName: str
        brokenCode: str
        faultHint: str = ""

    class PromoteRequest(BaseModel):
        toolName: str
        sourceCode: str
        testSuiteCode: str = ""

    # -- deterministic toolchain models (v4.1) --------------------------------
    class ScaffoldRequest(BaseModel):
        goal: str
        name: Optional[str] = None
        shape: Optional[str] = None
        schema_text: Optional[str] = None

    class ScaffoldJevRequest(BaseModel):
        goal: str
        name: Optional[str] = None
        shape: Optional[str] = None
        strict: Optional[bool] = None
        tests: Optional[bool] = None

    class SchemaRequest(BaseModel):
        goal: str
        schema_text: str
        framework: str = "express"
        name: Optional[str] = None

    class ComponentRequest(BaseModel):
        kind: str
        name: Optional[str] = None

    class ComponentsRequest(BaseModel):
        model: Dict[str, Any]
        kinds: Optional[List[str]] = None

    class BootstrapRequest(BaseModel):
        root: str
        shape: str
        name: str = "app"
        timeout: Optional[float] = None

    class FixRequest(BaseModel):
        root: str
        apply: bool = False

    class TestsRequest(BaseModel):
        root: str
        entry: str

    class TemplateRequest(BaseModel):
        name: str = "widget"
        kind: Optional[str] = None
        entity: Optional[str] = None
        goal: Optional[str] = None

    class ContextRequest(BaseModel):
        root: str
        goal: str
        max_files: int = 8

    class RootRequest(BaseModel):
        root: str

    class WorkspaceVerifyRequest(BaseModel):
        root: str
        gates: Optional[List[str]] = None
        timeout: Optional[float] = None

    # -- compat endpoints ----------------------------------------------------
    @app.get("/health")
    def health() -> Dict[str, Any]:
        recourse = RecourseClient().reachable()
        return {"status": "ok", "service": "cheetah-v3-pro+",
                "version": VERSION,
                "recourse_online": recourse.get("online", False),
                "recourse_url": DEFAULT_RECOURSE_URL}

    @app.post("/generate")
    def generate(req: GenerateRequest) -> Dict[str, Any]:
        safe = "".join(c if c.isalnum() or c in ("-", "_", " ") else ""
                       for c in req.name).strip()[:40] or "axiom-build"
        task_id = safe.lower().replace(" ", "_")
        # Real deterministic boilerplate: the scaffold's files are embedded in the
        # YAML so a caller can materialize them (`files[].rendered`).
        plan = build_scaffold(req.description or req.name, name=safe)
        yaml_lines = [
            f"# Generated by Cheetah V3 Pro+ {VERSION}",
            f"task_id: vibe_build_{task_id}",
            f"project_type: \"{req.project_type}\"",
            f"shape: {plan['shape']}",
            "description: |",
            f"  {(req.description or '')[:2000]}",
            "files:",
        ]
        for f in plan["files"]:
            yaml_lines.append(f"  - output: {f['output']}")
            rendered = f["rendered"].replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            yaml_lines.append(f'    rendered: "{rendered}"')
        yaml_lines.append("build:\n  validate: true\n  profile: true")
        yaml_text = "\n".join(yaml_lines) + "\n"
        out_dir = Path(__file__).resolve().parent / "out"
        out_dir.mkdir(exist_ok=True)
        saved = out_dir / f"generated_{task_id}.yaml"
        saved.write_text(yaml_text, encoding="utf-8")
        return {"yaml": yaml_text, "saved_to": str(saved),
                "shape": plan["shape"], "files": plan["files"]}

    # -- deterministic toolchain (v4.1) ---------------------------------------
    @app.post("/scaffold")
    def scaffold(req: ScaffoldRequest) -> Dict[str, Any]:
        plan = build_scaffold(req.goal, name=req.name, shape=req.shape, schema=req.schema_text)
        return {"ok": True, **plan, "shapes": list(SHAPES)}

    @app.post("/schema")
    def schema(req: SchemaRequest) -> Dict[str, Any]:
        """Contract-first CRUD plan from the entity DSL (deterministic, zero tokens)."""
        return build_crud_plan(req.goal, req.schema_text, framework=req.framework, name=req.name)

    @app.post("/component")
    def component(req: ComponentRequest) -> Dict[str, Any]:
        """One deterministic component (primitive or model-driven)."""
        return generate_component(req.kind, req.name)

    @app.post("/components")
    def components(req: ComponentsRequest) -> Dict[str, Any]:
        """Model-driven Form/List/Detail screens for one model."""
        return {"ok": True, "files": generate_components_for_model(req.model, kinds=req.kinds),
                "primitives": list(COMPONENT_PRIMITIVES),
                "model_kinds": list(COMPONENT_MODEL_KINDS)}

    @app.post("/scaffold/bootstrap")
    def scaffold_bootstrap(req: BootstrapRequest) -> Dict[str, Any]:
        """Toolchain-backed scaffold: shell out to create-vite/npm init when
        available (honest SKIP offline), then align via cheetah_fixes."""
        return bootstrap_scaffold(req.root, req.shape, name=req.name,
                                  timeout_sec=req.timeout or 120.0)

    @app.post("/scaffold/jev")
    def scaffold_jev(req: ScaffoldJevRequest) -> Dict[str, Any]:
        """Decision-gated scaffold: JEV decides (shape/strict/tests), Cheetah
        renders deterministic files. Returns the decision ledger; source is
        'localjev' when JEV answered, 'offline' when it fell back."""
        plan = decide_scaffold(req.goal, name=req.name, shape=req.shape,
                               strict=req.strict, tests=req.tests)
        return {"ok": True, **plan, "shapes": list(SHAPES)}

    @app.post("/fix")
    def fix(req: FixRequest) -> Dict[str, Any]:
        result = apply_fixes(req.root) if req.apply else plan_fixes(req.root)
        return {"ok": True, **result}

    @app.post("/tests")
    def tests(req: TestsRequest) -> Dict[str, Any]:
        result = synthesize_tests_for_file(req.root, req.entry)
        return {"ok": bool(result.get("path")), **result}

    @app.post("/template")
    def template(req: TemplateRequest) -> Dict[str, Any]:
        if req.goal and not req.kind:
            files = generate_for_goal(req.goal, req.name)
            return {"ok": bool(files), "files": files, "kinds": list(KINDS)}
        t = generate_template(req.kind or "react-component", req.name,
                              {"entity": req.entity or req.name})
        return {"ok": bool(t.get("path")), "files": [t] if t.get("path") else [],
                "kinds": list(KINDS), "note": t.get("note")}

    @app.post("/context")
    def context(req: ContextRequest) -> Dict[str, Any]:
        return {"ok": True, **build_context(req.root, req.goal, max_files=req.max_files)}

    # -- open-source toolchain gates (v4.2) -------------------------------------
    @app.post("/toolchain")
    def toolchain(req: RootRequest) -> Dict[str, Any]:
        """Detect the workspace's real verification tooling (package manager,
        declared scripts, python/ts tooling)."""
        return detect_toolchain(req.root)

    @app.post("/verify")
    def verify(req: WorkspaceVerifyRequest) -> Dict[str, Any]:
        """Run the open-source gate battery against a workspace. Each gate
        (test/typecheck/lint/format/build) is delegated to the real tool and
        reports PASS/FAIL/SKIP/ERROR/TIMEOUT — never a fabricated pass."""
        result = verify_workspace(req.root, gates=req.gates, timeout=req.timeout)
        return {"ok": True, "passed": result["passed"],
                "root": result["root"], "toolchain": result["toolchain"],
                "gates": result["gates"], "counts": result["counts"],
                "available_gates": list(GATES)}

    @app.post("/build")
    def build(req: BuildRequest) -> Dict[str, Any]:
        import yaml as _yaml
        try:
            spec = _yaml.safe_load(req.yaml_content)
        except Exception as exc:
            return {"ok": False, "error": f"YAML validation failed: {exc}",
                    "files": []}
        out_dir = (Path(__file__).resolve().parent / req.target_dir)
        try:
            out_dir.resolve().relative_to(Path(__file__).resolve().parent.resolve())
        except ValueError:
            return {"ok": False, "error": "target_dir escapes cheetah root",
                    "files": []}
        out_dir.mkdir(parents=True, exist_ok=True)
        written: List[str] = []
        for item in (spec.get("files") or [] if isinstance(spec, dict) else []):
            rel = str(item.get("output", "")).lstrip("/\\")
            if not rel or ".." in rel:
                continue
            dest = (out_dir / rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(item.get("rendered", "") or "", encoding="utf-8")
            written.append(str(dest))
        if not written:
            fallback = out_dir / "generated_template_pro.yaml"
            fallback.write_text(req.yaml_content, encoding="utf-8")
            written.append(str(fallback))
        return {"ok": True, "files": written}

    # -- agent -----------------------------------------------------------------
    @app.post("/agent/read")
    def agent_read(req: AgentReadRequest) -> Dict[str, Any]:
        return Workspace(Path(req.root)).read_file(req.path)

    @app.post("/agent/search")
    def agent_search(req: AgentSearchRequest) -> Dict[str, Any]:
        return Workspace(Path(req.root)).search(req.pattern, req.glob,
                                                req.limit)

    @app.post("/agent/plan")
    def agent_plan(req: AgentPlanRequest) -> Dict[str, Any]:
        return run_coding_task(req.root, req.plan)

    # -- audit -------------------------------------------------------------------
    @app.post("/audit")
    def audit(req: AuditRequest) -> Dict[str, Any]:
        if req.files:
            return audit_files(req.files, strict=req.strict)
        if req.root:
            return audit_workspace(req.root, glob=req.glob,
                                   strict=req.strict,
                                   run_tests=req.run_tests)
        return {"ok": False, "passed": False,
                "error": "provide files{} or root"}

    # -- recourse ------------------------------------------------------------------
    @app.get("/recourse/status")
    def recourse_status() -> Dict[str, Any]:
        client = RecourseClient()
        reach = client.reachable()
        local_tools = PromotionLedger()._load().get("tools", {})
        return {"recourse": reach, "local_promotions": len(local_tools)}

    @app.post("/recourse/verify")
    def recourse_verify(req: VerifyRequest) -> Dict[str, Any]:
        client = RecourseClient()
        remote = client.verify(req.sourceCode, req.testSuiteCode,
                               domain=req.domain)
        local = audit_files({"candidate.js": req.sourceCode})
        return {"remote": remote, "local_audit": local}

    @app.post("/recourse/heal")
    def recourse_heal(req: HealRequest) -> Dict[str, Any]:
        return RecourseClient().heal(req.toolName, req.brokenCode,
                                     req.faultHint)

    @app.post("/recourse/promote")
    def recourse_promote(req: PromoteRequest) -> Dict[str, Any]:
        audit_report = audit_files({f"{req.toolName}": req.sourceCode})
        return full_promotion_pipeline(req.toolName, req.sourceCode,
                                       req.testSuiteCode, audit_report)


def main() -> int:
    parser = argparse.ArgumentParser(description="Cheetah V3 Pro+ server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    if not FASTAPI_AVAILABLE:
        print("ERROR: fastapi/uvicorn not installed. Run: "
              "pip install fastapi uvicorn", file=sys.stderr)
        return 2
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
