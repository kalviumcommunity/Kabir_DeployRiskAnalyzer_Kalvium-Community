# Agent Instructions

This project strictly follows the Data Project Workspace setup guide documented in `project_documentation.md`.

As an AI Agent working on this project, please adhere to the following rules:

1. **Virtual Environments**: Always assume the existence of a Python virtual environment (typically `venv/`). Ensure all Python package installations and script executions happen within the context of this environment.
2. **Directory Structure**: 
   - Never modify data in `data/raw/`.
   - Place cleaned/transformed data in `data/processed/`.
   - Keep notebooks in `notebooks/` and reusable logic/scripts in `scripts/`.
   - Outputs should go to `output/`.
3. **Dependencies**: Any newly introduced library MUST be added to `requirements.txt` with appropriate version pinning (`==` for exact, `>=` for compatible).
4. **Environment Variables**: Never hardcode secrets. Always use `.env` files and add placeholder entries to `.env.example`.
5. **Version Control**: Do not commit large files (datasets in `data/`), secrets (`.env`), or environments (`venv/`). Ensure `.gitignore` is updated if new auto-generated or sensitive file types are introduced.
6. **Documentation**: When adding new features or setup steps, ensure `README.md` is updated and maintains the "4-command rule" for onboarding.
