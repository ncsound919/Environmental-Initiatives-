"""Deterministic component library for Overlay Cheetah V3 Pro+.

Why this exists: the historical ``react-component`` template emitted one 8-line
stub and relied on an LLM to build UI. But UI primitives and model-driven CRUD
screens are *mechanical*: given a name (or a data model) they can be generated
completely and correctly with zero LLM tokens.

Two tiers:

1. Primitives (``COMPONENTS``) — complete, real React + Tailwind components:
   Button, Card, Input, Badge, Table. Never stubs.
2. Model-driven screens (``generate_components_for_model``) — from the field
   metadata of a cheetah_schema model, emit ``{Model}Form`` (controlled state,
   per-field inputs incl. select for enums, checkbox for bools),
   ``{Model}List`` (typed Table), ``{Model}Detail`` (key/value card). Each is
   complete and typed — an LLM is only needed for *business* logic, never the
   envelope.

Honesty contract: generated components are deterministic and self-contained
(React + Tailwind classes, no state library). No IMPL_MARK — these are finished
mechanical artifacts. Stdlib only.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

VERSION = "4.2.0-components"

PRIMITIVES = ("button", "card", "input", "badge", "table")
MODEL_KINDS = ("form", "list", "detail")


def _pascal(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name or "Model")
    out = "".join(p[:1].upper() + p[1:] for p in parts if p)
    return out or "Model"


def _camel(name: str) -> str:
    p = _pascal(name)
    return p[:1].lower() + p[1:]


# ---------------------------------------------------------------------------
# Primitives — complete, real, mechanical.
# ---------------------------------------------------------------------------

_BUTTON = """import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
}

export default function Button({ variant = "primary", className = "", ...rest }: ButtonProps) {
  const base = "rounded px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50";
  const styles = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };
  return <button className={`${base} ${styles[variant]} ${className}`} {...rest} />;
}
"""

_CARD = """import React from "react";

export interface CardProps {
  title?: string;
  children: React.ReactNode;
}

export default function Card({ title, children }: CardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      {title ? <h3 className="mb-2 text-sm font-semibold text-gray-700">{title}</h3> : null}
      {children}
    </div>
  );
}
"""

_INPUT = """import React from "react";

export default function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  );
}
"""

_BADGE = """import React from "react";

export interface BadgeProps {
  tone?: "gray" | "green" | "red" | "blue";
  children: React.ReactNode;
}

const tones = {
  gray: "bg-gray-100 text-gray-700",
  green: "bg-green-100 text-green-700",
  red: "bg-red-100 text-red-700",
  blue: "bg-blue-100 text-blue-700",
};

export default function Badge({ tone = "gray", children }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  );
}
"""

_TABLE = """import React from "react";

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

export interface TableProps<T> {
  columns: Column<T>[];
  rows: T[];
  keyOf: (row: T) => string;
  empty?: string;
}

export default function Table<T>({ columns, rows, keyOf, empty = "No rows" }: TableProps<T>) {
  if (rows.length === 0) {
    return <p className="py-6 text-center text-sm text-gray-500">{empty}</p>;
  }
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((c) => (
              <th key={c.key} className="px-3 py-2 text-left font-medium text-gray-600">{c.header}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((row) => (
            <tr key={keyOf(row)} className="hover:bg-gray-50">
              {columns.map((c) => (
                <td key={c.key} className="px-3 py-2 text-gray-800">{c.render ? c.render(row) : String((row as Record<string, unknown>)[c.key] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
"""


def _primitive(kind: str) -> Dict[str, Any]:
    content = {
        "button": _BUTTON,
        "card": _CARD,
        "input": _INPUT,
        "badge": _BADGE,
        "table": _TABLE,
    }[kind]
    return {"path": f"src/components/ui/{kind}.tsx", "content": content,
            "note": f"React + Tailwind primitive: {kind} (complete, deterministic)"}


# ---------------------------------------------------------------------------
# Model-driven screens
# ---------------------------------------------------------------------------

def _input_type(fld: Dict[str, Any]) -> str:
    t = fld.get("type", "string")
    if t in ("int", "float"):
        return "number"
    if t == "bool":
        return "checkbox"
    if t == "datetime":
        return "datetime-local"
    return "text"


def _select_options(fld: Dict[str, Any]) -> List[str]:
    vals = fld.get("options") or []
    return [str(v) for v in vals]


def _form_fields(model: Dict[str, Any]) -> List[str]:
    """One label + control per non-pk field (controlled component state)."""
    out: List[str] = []
    for f in model.get("fields", []):
        if f.get("pk"):
            continue
        name = f.get("name", "field")
        qname = repr(name)
        opts = _select_options(f)
        if opts:
            out.append(
                f'      <label className="block text-sm font-medium text-gray-700">{name}</label>\n'
                f'      <select\n'
                f'        name="{name}"\n'
                f'        value={{String(values[{qname}] ?? "")}}\n'
                f'        onChange={{set({qname})}}\n'
                f'        className="w-full rounded border border-gray-300 px-3 py-2 text-sm"\n'
                f"      >\n"
                + "".join(f'        <option value="{o}">{o}</option>\n' for o in opts)
                + f"      </select>\n"
            )
        elif f.get("type") == "bool":
            out.append(
                f'      <label className="flex items-center gap-2 text-sm font-medium text-gray-700">\n'
                f'        <input type="checkbox" name="{name}" checked={{Boolean(values[{qname}])}} onChange={{set({qname})}} />\n'
                f"        {name}\n"
                f"      </label>\n"
            )
        else:
            out.append(
                f'      <label className="block text-sm font-medium text-gray-700">{name}</label>\n'
                f'      <input\n'
                f'        name="{name}"\n'
                f'        type="{_input_type(f)}"\n'
                f'        value={{String(values[{qname}] ?? "")}}\n'
                f'        onChange={{set({qname})}}\n'
                f'        className="w-full rounded border border-gray-300 px-3 py-2 text-sm"\n'
                f"      />\n"
            )
    return out


def _model_form(model: Dict[str, Any]) -> Dict[str, Any]:
    c = _pascal(model.get("name", "Model"))
    fields = _form_fields(model)
    body = "\n".join(fields) or "      <p className=\"text-sm text-gray-500\">No editable fields.</p>\n"
    content = (
        "import React from \"react\";\n"
        "import Input from \"./ui/input\";\n"
        "import Button from \"./ui/button\";\n\n"
        f"export interface {c}FormProps {{\n"
        "  onSubmit: (values: Record<string, string | boolean | number>) => void;\n"
        "}\n\n"
        f"export default function {c}Form({{ onSubmit }}: {c}FormProps) {{\n"
        "  const [values, setValues] = React.useState<Record<string, string | boolean | number>>({});\n"
        "  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>\n"
        "    setValues((v) => ({\n"
        "      ...v,\n"
        '      [key]: e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked : e.target.value,\n'
        "    }));\n"
        "  return (\n"
        '    <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); onSubmit(values); }}>\n'
        f"{body}"
        '      <Button type="submit">Save</Button>\n'
        "    </form>\n"
        "  );\n"
        "}\n"
    )
    return {"path": f"src/components/{c}Form.tsx", "content": content,
            "note": f"Model-driven create form for {c} (controlled state, zero tokens)"}


def _model_list(model: Dict[str, Any]) -> Dict[str, Any]:
    c = _pascal(model.get("name", "Model"))
    cols = ",\n".join(
        f'      {{ key: "{f.get("name", "x")}", header: "{f.get("name", "x")}" }}'
        for f in model.get("fields", [])
    )
    columns_jsx = "[\n" + cols + "\n    ]"
    content = (
        "import React from \"react\";\n"
        "import Table from \"./ui/table\";\n\n"
        f"export interface {c}Row {{\n"
        + "".join(f"  {f.get('name', 'x')}: {_ts_field_type(f)};\n" for f in model.get("fields", []))
        + "}\n\n"
        f"export default function {c}List({{ rows }}: {{ rows: {c}Row[] }}) {{\n"
        f"  return (\n"
        f"    <Table columns={{{columns_jsx}}} rows={{rows}} keyOf={{(r) => r.id}} "
        f"empty=\"No {c.lower()}s yet\" />\n"
        "  );\n"
        "}\n"
    )
    return {"path": f"src/components/{c}List.tsx", "content": content,
            "note": f"Model-driven list for {c} (typed table, zero tokens)"}


def _model_detail(model: Dict[str, Any]) -> Dict[str, Any]:
    c = _pascal(model.get("name", "Model"))
    rows = "\n".join(
        f"      <div className=\"flex justify-between py-1\">\n"
        f"        <dt className=\"text-sm text-gray-500\">{f.get('name', 'x')}</dt>\n"
        f"        <dd className=\"text-sm font-medium text-gray-900\">{{String(row.{f.get('name', 'x')} ?? \"\")}}</dd>\n"
        f"      </div>\n"
        for f in model.get("fields", [])
    )
    content = (
        "import React from \"react\";\n"
        "import Card from \"./ui/card\";\n\n"
        f"export interface {c}DetailProps {{\n"
        f"  row: Record<string, unknown> & {{ id: string }};\n"
        "}\n\n"
        f"export default function {c}Detail({{ row }}: {c}DetailProps) {{\n"
        "  return (\n"
        f"    <Card title=\"{c}\">\n"
        f"      <dl className=\"divide-y divide-gray-100\">\n"
        f"{rows}"
        f"      </dl>\n"
        "    </Card>\n"
        "  );\n"
        "}\n"
    )
    return {"path": f"src/components/{c}Detail.tsx", "content": content,
            "note": f"Model-driven detail view for {c} (zero tokens)"}


def _ts_field_type(fld: Dict[str, Any]) -> str:
    t = fld.get("type", "string")
    base = {"string": "string", "int": "number", "float": "number",
            "bool": "boolean", "datetime": "string", "uuid": "string"}.get(t, "string")
    return base


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_component(kind: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Generate one component. Primitives are name-independent; model kinds are
    driven by ``model`` in the return only via generate_components_for_model."""
    if kind in PRIMITIVES:
        return _primitive(kind)
    if kind in MODEL_KINDS:
        model = {"name": name or "Model",
                 "fields": [{"name": "id", "type": "string", "pk": True},
                            {"name": "name", "type": "string"}]}
        return generate_components_for_model(model, kinds=[kind])[0]
    return {"path": "", "content": "", "note": f"unknown component kind: {kind}"}


def generate_components_for_model(model: Dict[str, Any],
                                  kinds: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Emit model-driven Form/List/Detail screens for a cheetah_schema model.

    ``model``: {"name": "User", "fields": [{"name", "type", "pk", "options": [...]}]}
    ```
    """
    requested = list(kinds) if kinds else list(MODEL_KINDS)
    out: List[Dict[str, Any]] = []
    for kind in requested:
        if kind == "form":
            out.append(_model_form(model))
        elif kind == "list":
            out.append(_model_list(model))
        elif kind == "detail":
            out.append(_model_detail(model))
    return out


def components_for_models(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Emit primitives + model-driven screens for a list of models."""
    out: List[Dict[str, Any]] = [_primitive(k) for k in PRIMITIVES]
    for model in models:
        out.extend(generate_components_for_model(model))
    return out