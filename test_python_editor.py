import pytest
from python_editor import DEFAULTS, example_code, parse_editor


def test_valid_edits_are_parsed_without_execution():
    changed = {**DEFAULTS, "clients": 150, "employees": 20, "seed": 99}
    assert parse_editor(example_code(changed)) == changed


@pytest.mark.parametrize("code", [
    'import os\nos.system("echo unsafe")',
    example_code(DEFAULTS).replace('clients=1000', 'clients=__import__("os").system("id")'),
    example_code(DEFAULTS).replace('clients=1000', 'clients=-1'),
    example_code(DEFAULTS).replace('sim.generate("behavioral_health.db")', 'sim.generate("/etc/passwd")'),
    example_code(DEFAULTS) + '\nopen("secret", "w")',
    example_code(DEFAULTS).replace('seed=42', 'seed=True'),
    example_code(DEFAULTS).replace('seed=42', 'seed=42, seed=43'),
    example_code(DEFAULTS).replace('reference_date="2026-10-10"', 'reference_date="yesterday"'),
])
def test_rejects_unapproved_code(code):
    with pytest.raises(ValueError):
        parse_editor(code)
