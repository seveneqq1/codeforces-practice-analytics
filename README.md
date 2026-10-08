# Codeforces Practice & Analytics Dashboard

A Streamlit dashboard that turns a Codeforces submission history into focused practice.

# macOS — copy these commands into Terminal

Install [Python 3](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) first. Then open **Terminal**, paste this entire block, and press Return:

```bash
git clone https://github.com/seveneqq1/codeforces-practice-analytics.git
cd codeforces-practice-analytics
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

# Windows — copy these commands into PowerShell

Install [Python 3](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) first. Then open **PowerShell**, paste this entire block, and press Enter:

```powershell
git clone https://github.com/seveneqq1/codeforces-practice-analytics.git
cd codeforces-practice-analytics
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

The dashboard should open automatically at `http://localhost:8501`. Enter any public Codeforces handle in the sidebar; no API key is required. Press `Ctrl+C` in the terminal to stop it.

## Open it again later

You only need the full setup once. On macOS, open Terminal in the project folder and run:

```bash
.venv/bin/python -m streamlit run app.py
```

On Windows, open PowerShell in the project folder and run:

```powershell
.venv\Scripts\python -m streamlit run app.py
```

## Features

- **Rating vs. time-to-solve heat map** based on the interval between a problem's first submission and first accepted submission.
- **Topic diagnostics** showing success rate and submission efficiency for every Codeforces tag.
- **Personalized problem sets** targeting weak topics within ±100 of a chosen rating.
- **Mock contest timer** with configurable contest lengths, pause, and reset controls.
- Five-minute API caching to be respectful of the public Codeforces API.

## Development

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

## How analytics are calculated

Codeforces does not provide active working time. The dashboard estimates solve time as the elapsed time between the first recorded submission and the first accepted submission for each problem. Problems accepted on their first submission therefore show a zero-minute estimate.

Weak topics are ranked by problem-level success rate, attempts per solve, and sample size. Recommendations exclude solved problems, require at least one selected weak tag, and stay inside the chosen rating window.

## Privacy

The app requests only public profile, submission, and problemset data from the official Codeforces API. It does not store handles or submission histories outside Streamlit's in-memory cache.

## License

MIT
