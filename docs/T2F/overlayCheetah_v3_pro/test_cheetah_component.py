"""Tests for the deterministic component library. No network, no LLM."""

from cheetah_component import (
    PRIMITIVES,
    generate_component,
    generate_components_for_model,
    components_for_models,
)

USER_MODEL = {
    "name": "User",
    "fields": [
        {"name": "id", "type": "string", "pk": True},
        {"name": "email", "type": "string"},
        {"name": "age", "type": "int", "optional": True},
        {"name": "active", "type": "bool"},
        {"name": "role", "type": "Role", "options": ["admin", "member", "guest"]},
    ],
}


def test_all_primitives_generate():
    for kind in PRIMITIVES:
        c = generate_component(kind)
        assert c["path"].endswith(f"{kind}.tsx")
        assert c["content"]
        assert "NOT IMPLEMENTED" not in c["content"]
        assert "export default" in c["content"]


def test_primitive_paths_live_in_ui_dir():
    assert generate_component("button")["path"] == "src/components/ui/button.tsx"
    assert generate_component("table")["path"] == "src/components/ui/table.tsx"


def test_model_form_is_complete_and_typed():
    c = generate_components_for_model(USER_MODEL, kinds=["form"])[0]
    assert c["path"] == "src/components/UserForm.tsx"
    content = c["content"]
    assert "NOT IMPLEMENTED" not in content
    assert "email" in content and "age" in content
    # enum renders a select; bool renders a checkbox; int renders number
    assert 'type="number"' in content
    assert 'type="checkbox"' in content
    assert '<option value="admin">admin</option>' in content
    assert "onSubmit(values)" in content


def test_model_list_columns_follow_fields():
    c = generate_components_for_model(USER_MODEL, kinds=["list"])[0]
    content = c["content"]
    assert 'key: "email"' in content
    assert 'key: "age"' in content
    assert "keyOf={(r) => r.id}" in content
    assert ",," not in content  # no double commas from join


def test_model_detail_renders_rows():
    c = generate_components_for_model(USER_MODEL, kinds=["detail"])[0]
    content = c["content"]
    assert "<dt" in content and "<dd" in content
    assert "String(row.email ?? \"\")" in content


def test_components_for_models_includes_primitives_and_screens():
    out = components_for_models([USER_MODEL])
    paths = {c["path"] for c in out}
    assert {f"src/components/ui/{k}.tsx" for k in PRIMITIVES} <= paths
    assert "src/components/UserForm.tsx" in paths
    assert "src/components/UserList.tsx" in paths
    assert "src/components/UserDetail.tsx" in paths


def test_determinism():
    a = components_for_models([USER_MODEL])
    b = components_for_models([USER_MODEL])
    assert a == b


def test_unknown_kind_is_honest():
    c = generate_component("nope")
    assert c["path"] == ""
    assert "unknown component kind" in c["note"]