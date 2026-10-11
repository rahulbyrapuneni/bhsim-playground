# BHSim Python Playground

A small, public browser demo for [BHSim](https://github.com/rahulbyrapuneni/bhsim), the Python library for generating synthetic behavioral health data.

This app **imports `BHSimulator` from the published `bhsim` package**. It does not simulate output in JavaScript or use a prebuilt sample database.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The playground offers two modes:

- **Guided settings:** Change individuals, employees, history months, future days, reference date, and random seed using standard form controls. The corresponding Python source is displayed.
- **Python editor:** Edit those six parameters directly in a Python code example. The playground checks the example's exact structure with Python's AST parser and passes only the validated configuration to the real `BHSimulator`. **It does not execute arbitrary user-supplied Python code.**

After generating a dataset, explore SQLite tables and connected records, inspect validation results, and download the database or CSV exports. The **Field guide** tab shows the actual SQLite columns, types, primary/foreign keys, and a few plain-language descriptions. This is a starter field guide, **not yet an official, complete data dictionary**; a versioned dictionary belongs in a later release of the core BHSim package.

The Python editor has deliberate restrictions for public hosting: you can change supported literal values in the `BHSimulator(...)` call, not arbitrary imports, control flow, file paths, database queries, or Python statements.

## Deploy to Streamlit Community Cloud

1. Create a separate GitHub repository (for example, `bhsim-playground`) and push the contents of this directory to its root.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and create an app from that repository.
3. Use `main` as the branch and `app.py` as the entrypoint.
4. Once deployed, add the public URL to the main BHSim README under **Try BHSim in your browser** and to the GitHub About section if desired.

The app pins `bhsim==1.0.1` for reproducible deployments. Update the pin deliberately when a newer stable release is available and tested. Streamlit hosting limits may vary; the demo intentionally caps user input sizes.

## About the example

The generated data is entirely fictional and should not be used for clinical decisions, diagnoses, patient care, reimbursement, or official quality reporting. The app displays results from BHSim's built-in validation, which checks supported integrity rules rather than statistical or clinical representativeness.

License for BHSim: [MIT](https://github.com/rahulbyrapuneni/bhsim/blob/main/LICENSE).
