import sqlite3
import tempfile
from pathlib import Path

import pytest

from data_utils import overview, preview, appointment_summary, relationship_preview


def test_helpers_on_actual_bhsim_database():
    from bhsim import BHSimulator
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "data.db"
        sim = BHSimulator(clients=10, employees=2, history_months=1, seed=42)
        sim.generate(db)
        assert sim.validate()["valid"]
        payload = db.read_bytes()
        counts = overview(payload)
        assert counts["individuals"] == 10
        assert counts["employees"] == 2
        columns, rows = preview(payload, "visits")
        assert "visit_id" in columns
        assert len(rows) <= 30
        columns, rows = relationship_preview(payload)
        assert "individual" in columns and "program" in columns
        columns, rows = appointment_summary(payload)
        assert "visit_status" in columns
        with pytest.raises(ValueError):
            preview(payload, "visits; DROP TABLE visits")


def test_field_guide_reads_schema():
    from bhsim import BHSimulator
    from data_utils import data_dictionary
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "dict.db"
        BHSimulator(clients=10, employees=2, history_months=1, seed=42).generate(db)
        entries = data_dictionary(db.read_bytes(), "individuals")
        assert any(col["Column"] == "sex" for col in entries)
        with pytest.raises(ValueError):
            data_dictionary(db.read_bytes(), "unknown_table")
