"""Strict parser for an editable BHSim example; never execute submitted code."""
from __future__ import annotations

import ast
from datetime import date

LIMITS = {
    "clients": (1, 2000),
    "employees": (1, 250),
    "history_months": (1, 24),
    "future_days": (0, 90),
    "seed": (0, 2_147_483_647),
}
DEFAULTS = {
    "clients": 1000,
    "employees": 80,
    "history_months": 12,
    "future_days": 30,
    "reference_date": "2026-10-10",
    "seed": 42,
}


def example_code(params: dict) -> str:
    return f'''from bhsim import BHSimulator

sim = BHSimulator(
    clients={params["clients"]},
    employees={params["employees"]},
    history_months={params["history_months"]},
    future_days={params["future_days"]},
    reference_date="{params["reference_date"]}",
    seed={params["seed"]},
)

sim.generate("behavioral_health.db")
print(sim.validate())
sim.to_csv("output")'''


def parse_editor(code: str) -> dict:
    """Allow edits only to literal BHSimulator constructor arguments in our example.

    The code is parsed with AST and never compiled/evaluated/executed. Other
    expressions, imports, side effects, or modifications to workflow are rejected.
    """
    if len(code) > 10_000:
        raise ValueError("Code is too long for this playground")
    try:
        parsed = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"Python syntax error on line {exc.lineno}: {exc.msg}") from None
    expected = ast.parse(example_code(DEFAULTS))
    if len(parsed.body) != len(expected.body):
        raise ValueError("Only the BHSimulator settings can be edited in this playground")
    # The four statements other than the BHSimulator constructor must remain exact.
    for index in (0, 2, 3, 4):
        if ast.dump(parsed.body[index]) != ast.dump(expected.body[index]):
            raise ValueError("Keep the import, generation, validation, and export lines unchanged")
    statement = parsed.body[1]
    if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
        raise ValueError("Keep the 'sim = BHSimulator(...)' assignment unchanged")
    if not isinstance(statement.targets[0], ast.Name) or statement.targets[0].id != "sim":
        raise ValueError("Keep the variable name 'sim' unchanged")
    call = statement.value
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "BHSimulator" or call.args:
        raise ValueError("Use BHSimulator(...) with named settings")
    values = {}
    for keyword in call.keywords:
        if keyword.arg not in (*LIMITS.keys(), "reference_date") or keyword.arg in values:
            raise ValueError("Only the six supported BHSimulator settings are allowed")
        if not isinstance(keyword.value, ast.Constant):
            raise ValueError("Settings must use literal numbers or a quoted date")
        values[keyword.arg] = keyword.value.value
    if set(values) != set(DEFAULTS):
        raise ValueError("Include all six settings from the provided example")
    for name, (lower, upper) in LIMITS.items():
        value = values[name]
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f"{name} must be a whole number between {lower:,} and {upper:,}")
    value = values["reference_date"]
    if not isinstance(value, str):
        raise ValueError('reference_date must be a quoted date such as "2026-10-10"')
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError:
        raise ValueError('reference_date must use YYYY-MM-DD') from None
    return values
