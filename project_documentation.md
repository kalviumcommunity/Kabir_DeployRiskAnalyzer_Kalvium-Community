# Development Environment & Workspace Setup

Hey Data Engineer! Hey Analyst!
Welcome. Before a single line of data analysis is written, there is work that determines whether your project survives contact with a real team. This lesson is about that work - building an environment and workspace that runs identically on every machine, where every dependency is documented, and where a new teammate can be productive from their first git clone.
Every data project that ever broke on deployment, caused confusion in a team handoff, or produced results nobody could reproduce had one thing in common: the environment was not managed deliberately. Python packages were installed globally, folder structure was improvised, and the README was written as an afterthought.
This lesson fixes that. You will walk away with a workspace pattern you can apply to every data project you build, that your team can trust, and that future-you will be grateful for.

## The Real Scenario

### The Problem
A three-person analytics team works on a customer segmentation project. One member installs pandas 2.0 for a different project, which breaks the segmentation project that was written against pandas 1.5. Another member runs the notebooks on Windows while the lead analyst uses macOS, and file paths crash on one machine. A new joiner asks how to set up the project and receives a Slack message with six manually typed steps that are already out of date. The project produces results nobody can reproduce because the environment is different on every machine.

### The Solution
A deliberately managed workspace: an isolated virtual environment with all dependencies pinned in a `requirements.txt`, a folder structure every team member understands, a `.gitignore` that keeps secrets and generated files out of version control, and a README that lets any new joiner replicate the environment in four commands. This lesson builds that workspace from scratch.

## Why Isolated Environments Matter

### The Dependency Conflict Problem - and Why venv Solves It

**Without a Virtual Environment**
All packages install into a single shared Python installation. Project A needs pandas 1.5. Project B needs pandas 2.0. Installing one breaks the other. Every pip install on your system potentially breaks every project you have worked on.

**With a Virtual Environment**
Each project has its own isolated folder of installed packages. Project A has its own pandas 1.5. Project B has its own pandas 2.0. They never see each other. Installing or upgrading in one project never touches another.

**What a virtual environment actually is**
A virtual environment is a self-contained directory that holds a specific version of Python and a private collection of installed packages. It is created by Python itself using the built-in venv module. When you activate a virtual environment, every python and pip command runs against that isolated directory and nothing else.

**Why this matters for team-based data projects**
Reproducibility is the foundation of trustworthy data work. If your analysis runs on your machine with your packages but cannot be run by a colleague or by a CI server with different packages, your results are not reproducible. A virtual environment combined with a requirements.txt is the minimum viable guarantee that your environment can be recreated anywhere.

You just learned why isolated environments are essential for team-based data projects and what a virtual environment fundamentally does. Now you are going to learn exactly how to create, activate, and work inside a Python virtual environment across different operating systems.

## Creating and Activating a Python venv

### The Three Commands That Create Your Isolated World

**Step 1 - Create the virtual environment**
Run this command in your project root directory. The second `venv` is the name of the folder that will be created to hold your environment. This name is conventional - you can change it, but `venv` is what every team member expects to see.
```bash
# macOS and Linux
python3 -m venv venv
 
# Windows
python -m venv venv
```

**Step 2 - Activate the virtual environment**
Activating changes your terminal session so that all Python and pip commands now point to the isolated environment instead of the global Python installation. You will see the environment name appear at the start of your terminal prompt when it is active.
```bash
# macOS and Linux
source venv/bin/activate
 
# Windows Command Prompt
venv\Scripts\activate
 
# Windows PowerShell
venv\Scripts\Activate.ps1
```

**Step 3 - Deactivate when done**
When you finish working on the project, deactivate the environment to return your terminal to the global Python installation. This command is the same on every operating system.
```bash
deactivate
```

**Active environment prompt**
When your venv is active, your terminal prompt changes. You will see the environment name in parentheses before your usual prompt, like this:
`(venv) your-machine:project $`

**What lives inside the venv folder**
The venv folder contains a copy of Python, a pip executable, and all packages you install. It is large and machine-specific - never commit it to version control. That is what `requirements.txt` is for.

**Always activate before installing packages**
If you run pip install without activating your venv first, the package installs into your global Python - exactly the problem you were solving. Make activating the first thing you do when you open a terminal for any project.

You just learned how to create, activate, and deactivate a Python virtual environment on every major operating system, and what the activated prompt looks like. Now you are going to learn how to structure your project folders so your team always knows where to find data, scripts, notebooks, and outputs.

## Designing a Data Project Folder Structure

### A Folder Convention Every Data Team Member Understands Immediately

**The standard data project layout**
```
customer-analytics/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── scripts/
├── output/
├── venv/              ← never committed
├── .env               ← never committed
├── .gitignore
├── requirements.txt
└── README.md
```

**data/raw/**
Source data exactly as received - never modify files here.
`customer_transactions.csv`, `sales_2024.xlsx`, `survey_responses.json`. These files are the source of truth for your analysis. If you transform raw data in place, you permanently lose the ability to retrace your steps. Raw is sacred.

**data/processed/**
Cleaned and transformed data ready for analysis.
`cleaned_customers.csv`, `merged_sales.csv`. Every script and notebook reads from here, not from raw. Any team member can regenerate processed data from raw using your cleaning scripts - which means processed files are reproducible and do not need to be committed if they are large.

**notebooks/**
Jupyter notebooks for exploration and reporting - numbered in order.
`01_exploratory_analysis.ipynb`, `02_feature_engineering.ipynb`, `03_final_report.ipynb`. Number notebooks so they communicate logical order. Notebooks are for thinking and presenting - not for production code. Complex reusable logic belongs in scripts.

**scripts/**
Python scripts for repeatable, automatable operations.
`clean_data.py`, `train_model.py`, `generate_report.py`. Scripts are meant to be run the same way every time, by any team member, without modification. This is your pipeline code - it should be clean, documented, and runnable from the command line.

**output/**
Generated files - reports, figures, predictions, exports.
`report.pdf`, `figures/churn_by_segment.png`, `predictions.csv`. Output is always regenerable from your scripts and data. Never treat output as source-of-truth - treat the scripts that produce it as source-of-truth. Large output files are typically gitignored.

You just learned the standard data project folder structure and the engineering reasoning behind every directory. Now you are going to learn how to document and manage your project dependencies using `requirements.txt` so any teammate can recreate your exact environment.

## Managing Dependencies with requirements.txt

### The File That Makes Your Environment Reproducible Anywhere

**What requirements.txt contains**
A plain text file listing every package your project depends on, one per line, with the exact or compatible version. This is the instruction file - when a teammate runs `pip install -r requirements.txt`, they get exactly your environment.
```text
pandas==2.1.4
numpy==1.26.2
matplotlib==3.8.2
seaborn==0.13.0
jupyter==1.0.0
scikit-learn==1.3.2
python-dotenv==1.0.0
openpyxl==3.1.2
```

**How to generate it with pip freeze**
`pip freeze` prints all installed packages in your current environment with their exact versions. Redirect that output to `requirements.txt` to capture your environment at any moment.
```bash
# Activate your venv first, then run:
pip freeze > requirements.txt
 
# To verify what was captured:
cat requirements.txt
```
Run this command every time you install a new package. Commit the updated requirements.txt immediately - an out-of-date requirements.txt is almost as bad as no requirements.txt.

**How a teammate uses it**
A new team member clones the repository, creates their own virtual environment, activates it, and then installs everything from requirements.txt in one command. Their environment is now identical to yours.
```bash
git clone https://github.com/team/customer-analytics.git
cd customer-analytics
python3 -m venv venv
source venv/bin/activate          # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**`==` (exact version)**
`pandas==2.1.4` installs exactly 2.1.4 and nothing else. Maximum reproducibility. The team always uses the same version. Recommended for production and team projects.

**`>=` (compatible version)**
`pandas>=2.0.0` installs 2.0.0 or any newer version. More flexible but less reproducible. Different teammates may get different versions. Use for library packages that tolerate wider ranges.

You just learned how requirements.txt captures your environment, how to generate it with pip freeze, and how teammates use it to replicate your setup exactly. Now you are going to learn which files must never go into version control and how to configure `.gitignore` to keep your repository clean and your secrets safe.

## Version Control Hygiene with .gitignore

### Keeping Secrets, Machines, and Clutter Out of Your Repository

**The .gitignore file in your project root**
A `.gitignore` file tells Git which files and folders to never track. Once a pattern is in `.gitignore`, Git ignores matching files entirely - they never appear in `git status`, never get staged, and never get committed. This is how you prevent sensitive and machine-specific files from accidentally ending up in your repository.
```text
# Virtual environment - machine-specific, never commit
venv/
.venv/
 
# Secrets and credentials - NEVER commit these
.env
*.key
*.pem
 
# Python cache files - auto-generated, not useful to teammates
__pycache__/
*.pyc
*.pyo
 
# Jupyter notebook checkpoints - auto-saved drafts, not needed in repo
.ipynb_checkpoints/
 
# macOS system files - irrelevant to teammates on other systems
.DS_Store
 
# Large output files - regenerable from scripts
output/*.csv
output/*.pdf
 
# Distribution and build artifacts
*.egg-info/
dist/
build/
```

**Why venv/ must be excluded**
The venv folder is large (hundreds of megabytes), machine-specific (compiled for your exact OS and CPU), and entirely regenerable from requirements.txt. Committing it would make your repository enormous, break for teammates on different systems, and make it impossible to track actual code changes in version history.

**Why .env must be excluded - this one is critical**
The `.env` file stores secrets: database passwords, API keys, internal service credentials. Committing a `.env` file to a public repository has caused real security incidents at real companies. Git history is permanent - removing a committed secret requires rewriting history, which breaks everyone who cloned the repository. Add `.env` to `.gitignore` before writing a single secret into it.

**Why .ipynb_checkpoints/ must be excluded**
Jupyter auto-saves notebook snapshots into a hidden `.ipynb_checkpoints` folder every few minutes. These checkpoints are personal draft saves - not the notebook itself. Committing them creates noise in pull requests, causes merge conflicts between teammates, and bloats repository size with redundant content.

You just learned what belongs in .gitignore, why each category of file must be excluded, and especially why the .env file must never reach version control. Now you are going to learn the final piece: writing a README that lets any team member replicate your workspace from scratch without asking a single question.

## README Documentation for Team Handoff

### The First File Anyone Reads - Make It Do Real Work

**What a README must answer**
A README for a data project must answer four questions for a new team member: what does this project do, how do I set up the environment, what is in each folder, and how do I run the analysis. If any of these four questions requires asking someone, the README is incomplete.

**A standard README structure for data projects**
```markdown
# Customer Segmentation Analysis
 
Segments customers by purchase behaviour using K-means clustering
on the 2024 transaction dataset. Outputs include segment profiles
and an interactive HTML report.
 
## Setup
 
1. Clone the repository
   git clone https://github.com/team/customer-analytics.git
   cd customer-analytics
 
2. Create and activate a virtual environment
   python3 -m venv venv
   source venv/bin/activate    # Windows: venv\Scripts\activate
 
3. Install dependencies
   pip install -r requirements.txt
 
4. Configure environment variables
   Copy .env.example to .env and fill in your database credentials
 
## Project Structure
 
data/raw/       Source data - never modified
data/processed/ Cleaned data ready for analysis
notebooks/      Jupyter exploration and reporting notebooks
scripts/        Repeatable Python scripts
output/         Generated reports and figures
 
## Running the Analysis
 
python scripts/clean_data.py          # Produces data/processed/
python scripts/run_segmentation.py    # Produces output/
jupyter notebook notebooks/           # Open interactive notebooks
```

**README test - The 4-command rule**
A good README passes this test: give it to someone who has never seen the project and ask them to set it up. If they can do it in four commands or fewer without asking a question, your README works. If they need to ask anything, update the README before moving on.

**Include a .env.example file**
Commit a `.env.example` that shows every required environment variable with placeholder values. Never commit the real `.env`. This gives teammates the structure they need without exposing any secrets. It is the correct pattern for all projects that use configuration variables.

## Bonus Resources
These go deeper on everything covered here. All optional - pick what you are most curious about.
- Python venv documentation - the official reference for creating and managing virtual environments including options, directory structure, and platform-specific behaviour
- gitignore.io - generate a .gitignore file for any combination of operating system, language, and IDE in seconds, covering every common pattern your project needs
- Cookiecutter Data Science - a well-established opinionated project template for data science teams with the folder structure, conventions, and reasoning used at professional analytics organisations
