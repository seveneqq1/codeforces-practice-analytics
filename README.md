# Codeforces Practice & Analytics Dashboard

A Streamlit dashboard that turns a Codeforces submission history into focused practice.

## Features

- **Rating vs. time-to-solve heat map** based on the interval between a problem's first submission and first accepted submission.
- **Topic diagnostics** showing success rate and submission efficiency for every Codeforces tag.
- **Personalized problem sets** targeting weak topics within ±100 of a chosen rating.
- **Mock contest timer** with configurable contest lengths, pause, and reset controls.
- Five-minute API caching to be respectful of the public Codeforces API.

## Launch the app

After downloading or cloning the repository:

- **macOS:** double-click `Launch Practice Lab.command`.
- **Windows:** double-click `Launch Practice Lab.bat`.

The launcher creates an isolated Python environment, installs anything missing, and opens the dashboard. The first launch can take a minute; later launches are faster. Python 3 must be installed.

If macOS blocks the launcher, right-click it, choose **Open**, then confirm once.

## Terminal option

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then enter any public Codeforces handle in the sidebar. No API key is required.

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
