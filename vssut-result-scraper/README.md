# VSSUT Result Scraper

This project scrapes student results from the VSSUT examination results portal, extracts student name, SGPA, and CGPA, generates ranked leaderboards, saves them to Excel, and prints the top students in the terminal.

## Project structure

```text
vssut-result-scraper/
|-- scraper.py
|-- parser.py
|-- ranking.py
|-- config.py
|-- requirements.txt
|-- README.md
`-- results/
    |-- sgpa_ranking.xlsx
    `-- cgpa_ranking.xlsx
```

## Installation

```bash
pip install requests beautifulsoup4 pandas lxml openpyxl tqdm
```

Or install from the project file:

```bash
pip install -r requirements.txt
```

## Run the scraper

From the project directory:

```bash
python scraper.py
```

Optional CLI arguments:

```bash
python scraper.py --delay 1 --workers 1 --top 10 --output-dir results
```

## Output

The script:

- scans the configured registration number ranges
- fetches each result page from the VSSUT portal
- extracts student name, registration number, SGPA, and CGPA
- creates one dataset ranked by SGPA and another ranked by CGPA
- saves the datasets to `results/sgpa_ranking.xlsx` and `results/cgpa_ranking.xlsx`
- prints the top students in the terminal for both rankings

## Registration ranges

The current ranges are defined in `config.py`:

```python
RANGE1_START = 2402040001
RANGE1_END = 2402040117

RANGE2_START = 2402041118
RANGE2_END = 2402041156

RANGE3_START = 2402081001
RANGE3_END = 2402081078
```

Change these constants in `config.py` to scrape a different registration window.

## Notes about the VSSUT portal

The live VSSUT page currently expects these query parameters:

- `rid`
- `ccid`
- `rollno`
- `Name`

This project is preconfigured with the verified `rid` for the supplied ranges:

```python
RESULT_RID = "c20ad4d76fe97759aa27a0c99bff6710"
```

If VSSUT publishes a new result page, update `RESULT_RID` in `config.py`.

## Error handling

The scraper safely handles:

- connection errors
- invalid registration numbers
- missing or malformed SGPA values
- missing or malformed CGPA values

Invalid or missing records are skipped and reported in the final summary.

## Bonus features included

- CLI arguments for delay, workers, top count, and output file
- optional threaded scraping with `--workers`

Use threading carefully and respectfully to avoid overloading the site.
