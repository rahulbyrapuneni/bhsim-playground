"""BHSim Playground — runs the real published bhsim library."""
from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
from bhsim import BHSimulator

from python_editor import example_code, parse_editor, DEFAULTS

from data_utils import (
    TABLES, appointment_summary, overview, preview,
    relationship_preview, zip_csv_export, data_dictionary,
)

st.set_page_config(page_title="BHSim | Python Playground", page_icon="🧩", layout="wide")

st.markdown("""<style>
.block-container {max-width: 1150px; padding-top: 2rem}
h1,h2,h3 {letter-spacing: -0.025em}
[data-testid="stMetricValue"] {font-size: 1.8rem}
</style>""", unsafe_allow_html=True)

st.title("BHSim Python Playground")
st.caption("Run the actual open-source Python library in your browser.")
st.markdown(
    "Generate connected fictional behavioral health data, inspect the records, "
    "and use the same Python code in your own project. No real patient information is used."
)

mode = st.radio("Choose how to use Python", ["Guided settings", "Python editor"], horizontal=True,
                help="Guided settings create the Python example for you. The editor accepts changes to supported settings only.")

if "editor_text" not in st.session_state:
    st.session_state["editor_text"] = example_code(DEFAULTS)

if mode == "Guided settings":
    with st.sidebar:
        st.header("Simulation settings")
        st.caption("Choose the size and time period for your fictional dataset.")
        clients = st.number_input("Individuals", min_value=1, max_value=2000, value=1000, step=50,
                                  help="Number of fictional individuals to generate.")
        employees = st.number_input("Employees", min_value=1, max_value=250, value=80, step=5,
                                    help="Number of fictional staff members.")
        history_months = st.number_input("History (months)", min_value=1, max_value=24, value=12,
                                         help="How many months of past appointments to simulate.")
        future_days = st.number_input("Future appointments (days)", min_value=0, max_value=90, value=30,
                                      help="How many days into the future to schedule appointments.")
        with st.expander("Advanced settings"):
            reference_date = st.date_input("Reference date", value=date(2026, 10, 10),
                                           help="Anchor date for historical and future appointments.")
            seed = st.number_input("Random seed", min_value=0, max_value=2_147_483_647, value=42,
                                   help="Use the same seed and settings for reproducible data.")
        st.caption("Limits protect the public demo from oversized jobs; local BHSim installations can use other supported configurations.")
    params = {
        "clients": int(clients), "employees": int(employees),
        "history_months": int(history_months), "future_days": int(future_days),
        "reference_date": reference_date.isoformat(), "seed": int(seed),
    }
    st.code(example_code(params), language="python")
    st.caption("This is the Python code for your chosen settings. Switch to Python editor to edit the code directly.")
    valid_code = True
else:
    st.markdown("### Edit BHSim Python code")
    st.caption("Change the six BHSimulator arguments in the code below. For safety, this public demo doesn't run arbitrary Python commands.")
    editor_text = st.text_area("Python code", key="editor_text", height=340,
                               help="Edit literal BHSimulator settings. Imports and calls are fixed for server safety.")
    try:
        params = parse_editor(editor_text)
        st.success("Python settings validated. Generate to run the real BHSim package.")
        valid_code = True
    except ValueError as exc:
        st.warning(str(exc))
        params = None
        valid_code = False
    st.caption("Only the validated constructor settings are sent to BHSimulator; submitted source code is never executed.")

clicked = st.button("Generate dataset", type="primary", use_container_width=True, disabled=not valid_code)
if clicked:
    st.session_state.pop("dataset", None)
    with st.spinner("Running BHSim and validating the generated data…"):
        try:
            with tempfile.TemporaryDirectory(prefix="bhsim-playground-") as temp:
                db_path = Path(temp) / "behavioral_health.db"
                csv_dir = Path(temp) / "output"
                sim = BHSimulator(**params)
                sim.generate(db_path)
                validation = sim.validate()
                if not validation.get("valid", False):
                    st.error("The generated dataset did not pass validation.")
                    st.json(validation)
                else:
                    sim.to_csv(csv_dir)
                    db_bytes = db_path.read_bytes()
                    csv_zip = zip_csv_export(csv_dir)
                    st.session_state["dataset"] = {
                        "db": db_bytes,
                        "csv": csv_zip,
                        "params": params.copy(),
                        "validation": validation,
                    }
                    st.success("Dataset generated and validated with BHSim.")
        except (ValueError, RuntimeError, OSError, OverflowError) as exc:
            if "staff capacity" in str(exc).lower():
                st.error("This configuration has too few available staff for the simulated appointments. Increase Employees, reduce Individuals, or shorten the history period and try again.")
            else:
                st.error(f"BHSim could not generate this configuration: {exc}")
        except Exception as exc:
            st.error("Generation encountered an unexpected error. Try smaller settings or report the issue on GitHub.")
            st.caption(f"Error type: {type(exc).__name__}")

stored = st.session_state.get("dataset")
if not stored:
    st.info("Select your settings and click **Generate dataset** to explore real BHSim output.")
    st.markdown("**Install locally:** `pip install bhsim` · [Source code](https://github.com/rahulbyrapuneni/bhsim) · [PyPI](https://pypi.org/project/bhsim/)")
    st.stop()

if params is not None and stored["params"] != params:
    st.warning("The settings have changed since this dataset was generated. Click Generate dataset to apply them.")

db = stored["db"]
counts = overview(db)
st.subheader("Your generated dataset")
cols = st.columns(3)
for index, (title, key) in enumerate([
    ("Individuals", "individuals"), ("Employees", "employees"),
    ("Programs", "programs"), ("Enrollments", "individual_programs"),
    ("Visits", "visits"), ("Assessments", "assessments"),
]):
    cols[index % 3].metric(title, f"{counts[key]:,}")
st.caption("Counts come directly from the SQLite database generated by BHSim.")

explore, links, dictionary, quality, downloads = st.tabs(["Explore tables", "Connected records", "Field guide", "Validation", "Download"])
with explore:
    st.markdown("### Browse the generated records")
    label = st.selectbox("Choose a table or view", list(TABLES.keys()))
    limit = st.select_slider("Rows to preview", options=[10, 20, 30, 50, 100], value=30)
    columns, rows = preview(db, TABLES[label], limit)
    st.dataframe(pd.DataFrame(rows, columns=columns), use_container_width=True, hide_index=True)
    st.caption("These are actual rows generated by BHSim. The preview is limited to keep the page responsive.")
with links:
    st.markdown("### How the records connect")
    st.markdown("Each appointment connects an individual, a behavioral health program, and an employee using database IDs.")
    columns, rows = relationship_preview(db)
    st.dataframe(pd.DataFrame(rows, columns=columns), use_container_width=True, hide_index=True)
    st.markdown("### Appointment outcomes")
    columns, rows = appointment_summary(db)
    st.dataframe(pd.DataFrame(rows, columns=columns), use_container_width=True, hide_index=True)
with dictionary:
    st.markdown("### Explore the database schema")
    st.caption("This field guide reads column types, keys, and relationships from your generated database. Plain-language descriptions are preliminary; the full versioned data dictionary will be part of a future BHSim library release.")
    selected = st.selectbox("Table or view", list(TABLES.keys()), key="field_guide_table")
    fields = data_dictionary(db, TABLES[selected])
    st.dataframe(pd.DataFrame(fields), use_container_width=True, hide_index=True)
    st.caption("Example: sex codes M/F/X are simulated designations; X represents other/unspecified in this demo, not a gender identity classification.")
with quality:
    st.markdown("### Built-in BHSim validation")
    result = stored["validation"]
    if result.get("valid"):
        st.success("Passed: no issues reported by BHSim's built-in validator.")
    else:
        st.error("Validation issues reported.")
    st.json(result)
    st.caption("Validation checks data integrity and supported business rules; it does not establish clinical realism.")
    st.markdown("**Reproducibility:** Running the same BHSim version with the same settings and seed produces the same generated dataset.")
with downloads:
    st.markdown("### Use the generated data in your own tools")
    a, b = st.columns(2)
    with a:
        st.download_button("Download SQLite database", data=stored["db"],
                           file_name="behavioral_health.db", mime="application/octet-stream", use_container_width=True)
    with b:
        st.download_button("Download CSV files (ZIP)", data=stored["csv"],
                           file_name="bhsim_csv.zip", mime="application/zip", use_container_width=True)
    st.caption("Files are generated temporarily. The playground does not ask for or upload real patient records.")

st.divider()
st.markdown("**BHSim is a Python library, not a clinical application.** [Install from PyPI](https://pypi.org/project/bhsim/) · [GitHub](https://github.com/rahulbyrapuneni/bhsim) · [Report an issue](https://github.com/rahulbyrapuneni/bhsim/issues)")
