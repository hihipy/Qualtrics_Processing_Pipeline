# Qualtrics Processing Pipeline

[![Link Check](https://github.com/hihipy/qualtrics-processing-pipeline/actions/workflows/links.yml/badge.svg)](https://github.com/hihipy/qualtrics-processing-pipeline/actions/workflows/links.yml)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**Built with**

[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org)
[![Marimo](https://img.shields.io/badge/Marimo-1C7361?style=flat&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAADYAAAA4AQMAAACMgZnuAAAABlBMVEX%2F%2F%2F%2F%2F%2F%2F9VfPVsAAAAAXRSTlMAQObYZgAAARpJREFUeNp1zr1PU3EcRvHP%2Ff6gbUKwuhEx0DAYJkOiiSYQXgZGEhd2RuOibowdHBwd3eRfYNPJS%2BLAyAQdCLkkDhAYSofSGi51uHUyTifPc5aD%2BgWCVw3g1nuS9Oj7r55ksndzU%2BJJ4Zwwu%2BdljmUm3uCY9EI4pnxL1sGWqHVw0g67eCBNbR%2Fy%2BzYedtHfS9NR4Fm01uF13MH9TmyAlg%2BQLUZRRcUCjD7rgS%2FRHf8VfsYE6I63f1iCIuI%2F%2Fi%2BP2rAUX6uO8X8XjbzyVU9htQVHcVrt1OgPyDox%2FIRY0jxErYj%2BNeo7UT7G9HqK5mZu8ansW84VTlekM7xrDuZW8Lw9GgwwU2QHBWpr9%2FVcJn0c%2FjgQysvhPpgf4Q%2BkZFJVMy0tZgAAAABJRU5ErkJggg%3D%3D)](https://marimo.io)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org)
[![openpyxl](https://img.shields.io/badge/openpyxl-2E7D32?style=flat&logoColor=white)](https://openpyxl.readthedocs.io)
[![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Tkinter](https://img.shields.io/badge/Tkinter-FFD43B?style=flat&logo=python&logoColor=black)](https://docs.python.org/3/library/tkinter.html)

A Python pipeline that turns raw [Qualtrics](https://www.qualtrics.com) Excel exports into a documented, analysis-ready package. It removes test data, corrects data types, and generates reports and codebooks automatically. Ships as both a [Jupyter](https://jupyter.org) notebook and a [marimo](https://marimo.io) notebook.

---

## The Problem

Anyone who has worked with survey data knows the real work begins after the data is collected. Raw exports from platforms like Qualtrics are a good starting point, but they come with a few recurring problems:

- **Mixed-in test data:** Preview and test responses are often included, and they skew your results if they aren't carefully removed.
- **Inconsistent data types:** Numbers and dates are often formatted as text, which causes errors when you try to run calculations or build plots.
- **Cryptic headers:** Column names like `Q5_3_TEXT` are meaningless without a legend, which makes analysis slow and hard to interpret.
- **No documentation:** The raw file gives you no context, so it's hard to trust the data or reproduce your cleaning steps later.

Doing this by hand takes time, and it's easy to introduce mistakes that compromise the analysis.

---

## The Solution

This project ingests a raw Qualtrics Excel file and produces a documented analysis package. It handles the tedious data-janitor work so you can go straight from collecting data to analyzing it.

The same pipeline logic is available in two notebook formats. Pick whichever fits how you work.

| | `qualtrics_processing_pipeline.ipynb` | `qualtrics_processing_pipeline.py` |
| --- | --- | --- |
| Format | Jupyter notebook (JSON) | marimo notebook (plain Python) |
| Editor | [Jupyter Notebook](https://jupyter.org), [JupyterLab](https://jupyterlab.readthedocs.io), [VS Code](https://code.visualstudio.com) | [`marimo edit`](https://docs.marimo.io/guides/editor_features/) |
| Picking your files | Two [Tkinter](https://docs.python.org/3/library/tkinter.html) pop-up dialogs | Upload button and a folder dropdown in the notebook |
| Execution order | Whatever you ran last | [Dataflow graph](https://docs.marimo.io/guides/editor_features/dataflow/), automatic |
| Run headlessly | Needs [nbconvert](https://nbconvert.readthedocs.io) or [papermill](https://papermill.readthedocs.io) | `python qualtrics_processing_pipeline.py` |
| Git diffs | Noisy, outputs and metadata included | Clean, it is a real Python file |
| Setup | Ships with [Anaconda](https://www.anaconda.com/products/distribution) | `pip install marimo` |

### Why a Notebook at All

A notebook keeps the process transparent, interactive, and easy to follow.

- **Step-by-step transparency:** The pipeline is broken into logical, sequential cells. You can run each step on its own and watch how the data changes, rather than running a single black-box script.
- **Interactivity and verification:** After running a cell, you can inspect the dataframes and intermediate outputs, which makes it simple to confirm each cleaning step is working as expected.
- **Integrated documentation:** Notebooks combine executable code, explanatory text, and outputs, which turns the tool into an interactive document where the "how" and "why" sit alongside the code.

### What marimo Adds

[marimo](https://github.com/marimo-team/marimo) is a reactive Python notebook stored as an ordinary `.py` file. Per the [marimo documentation](https://docs.marimo.io) (validated here against marimo 0.23.16), it differs from Jupyter in a few ways that matter for a multi-step cleaning pipeline:

- **No stale state.** marimo builds a [dataflow graph](https://docs.marimo.io/guides/editor_features/dataflow/) from the code. Change the cleaning step and every step downstream of it reruns. There is no way to end up looking at output from a cell that no longer matches its inputs.
- **One definition per name.** A variable can only be assigned in one cell, so you never have two versions of `df` in play depending on what you clicked last. The [key concepts guide](https://docs.marimo.io/getting_started/key_concepts/) covers the constraints this imposes.
- **It is a Python file.** `git diff` shows the code you changed, not a wall of JSON. The file imports and runs like any other module.
- **Two run modes from one file.** `marimo edit` opens the interactive editor. `python qualtrics_processing_pipeline.py` runs the whole pipeline start to finish with no editor and no browser.
- **Interactive controls instead of pop-ups.** File selection uses `mo.ui` elements rendered in the notebook, so changing the input file re-runs every downstream step against the new data automatically.

The marimo team's [post on notebooks as dataflow graphs](https://marimo.io/blog/dataflow) explains the design, and the [FAQ](https://docs.marimo.io/faq/) covers the common friction points when moving over from Jupyter.

The tradeoff is that the marimo version is stricter. The Jupyter version lets you rerun a single cell in isolation to poke at something, which is sometimes what you want when a specific column is misbehaving.

---

## Features

- **Point-and-click file selection:** The marimo notebook gives you an upload button for the Excel file and a dropdown of common output folders, with an optional Finder dialog for anywhere else. The Jupyter notebook uses two Tkinter pop-ups.
- **Environment variable overrides:** Set `QUALTRICS_INPUT` and `QUALTRICS_OUTPUT` to bypass the controls entirely, which is what makes headless and automated runs possible.
- **Automated data cleaning:** Removes test data, standardizes values, and creates data quality flags.
- **Data typing:** Sets numbers, dates, and categories to the correct types to prevent common analysis errors.
- **HTML report:** Generates a single, shareable report with data quality metrics and response summaries.
- **NLP-ready JSON export:** Creates a structured [JSON](https://www.json.org/json-en.html) file for sentiment analysis or topic modeling.
- **Accessible typography throughout:** The notebook, the HTML report, and all three Excel workbooks are set in [Atkinson Hyperlegible Next](https://fonts.google.com/specimen/Atkinson+Hyperlegible+Next), the [Braille Institute](https://www.brailleinstitute.org) typeface designed to maximize character distinction for low-vision readers. The HTML outputs load it as a web font, so it renders whether or not the font is installed.
- **Test fixture included:** A synthetic Qualtrics export lives in `tests/` so you can confirm the pipeline works before pointing it at real data.

---

## Repository Contents

| Path | Description |
| --- | --- |
| `qualtrics_processing_pipeline.ipynb` | Jupyter version of the pipeline. |
| `qualtrics_processing_pipeline.py` | marimo version of the pipeline. Same logic, reactive execution. |
| `tests/qualtrics_test_export.xlsx` | Synthetic Qualtrics export for testing. 78 rows, 31 columns. |
| `tests/make_test_fixture.py` | Regenerates the test export at any size. Seeded, so output is reproducible. |
| `tests/verify_conversion.txt` | Verification procedure with the exact numbers each test should produce. |

---

## Getting Started

### Option A: The marimo Notebook

1. **Install marimo and the dependencies:**

```bash
   pip install marimo pandas numpy openpyxl
```

2. **Open the notebook:**

```bash
   marimo edit qualtrics_processing_pipeline.py
```

   A browser tab opens with the notebook. Nothing runs yet; the pipeline waits for an input file.

3. **Click "Add an Excel file"** and pick your raw Qualtrics export. Steps 1 through 3 run immediately.

4. **Choose an output folder** from the dropdown. It offers Downloads, Desktop, Documents, your home folder, and the notebook's own folder, and defaults to Downloads. Use the "Or pick any other folder" button for somewhere else. Step 4 writes the files.

5. **Or run it headlessly, with no browser at all:**

```bash
   QUALTRICS_INPUT=./raw_export.xlsx \
   QUALTRICS_OUTPUT=./output \
   python qualtrics_processing_pipeline.py
```

   With those two variables set, the pipeline runs start to finish and writes everything to `./output`. They also override the notebook controls when the editor is open.

Changing the input file re-runs every downstream step against the new data. Nothing is written to disk until Step 4 actually runs.

### Option B: The Jupyter Notebook

If you're new to Python or data analysis, the easiest way to get started is the **Anaconda Distribution**, a free, all-in-one package that includes [Python](https://www.python.org), Jupyter Notebook, and the essential data science libraries.

1. **Download Anaconda:** Go to the [Anaconda Distribution page](https://www.anaconda.com/products/distribution) and download the installer for your operating system (Windows, macOS, or Linux).
2. **Install Anaconda:** Run the installer and follow the on-screen instructions. The default settings are fine.
3. **Launch Jupyter Notebook:** Once installed, open the **Anaconda Navigator** application. From the home screen, click "Launch" under Jupyter Notebook. A new tab will open in your web browser with the Jupyter file navigator.
4. **Run the pipeline:** Navigate to `qualtrics_processing_pipeline.ipynb` and click it to open. Then select "Run All Cells" from the "Cell" or "Run" menu at the top.
5. **Select your input file:** A window pops up. Navigate to and select the raw Qualtrics Excel file (.xlsx or .xls) you want to process.
6. **Choose your output folder:** A second window appears. Choose the folder where you want to save your clean files.

The required libraries ([pandas](https://pandas.pydata.org), [numpy](https://numpy.org), [openpyxl](https://openpyxl.readthedocs.io)) ship with Anaconda, so no further setup is needed.

### Reviewing Your Output

Either way, open your chosen output folder and start with `comprehensive_summary_report.html`.

---

## Testing With the Included Fixture

`tests/qualtrics_test_export.xlsx` is a synthetic Qualtrics export built to exercise every branch of the pipeline. Run against it before you trust the pipeline on real data. Run from the repository root:

```bash
mkdir -p testout
QUALTRICS_INPUT=./tests/qualtrics_test_export.xlsx \
QUALTRICS_OUTPUT=./testout \
python qualtrics_processing_pipeline.py
```

The fixture is seeded, so these numbers are exact:

| Check | Expected |
| --- | --- |
| Fixture rows | 78 (1 question-text row, 77 responses) |
| Preview and spam responses removed | 6 |
| Surviving responses | 71 |
| `analysis_ready_data.csv` shape | 71 rows x 66 columns |
| Codebook variable definitions | 58 |
| Q2 matrix columns detected | 6 |
| Q5 contaminated values nulled | 16 |
| Files written to output folder | 9 |

The fixture deliberately contains 4 survey previews, 2 spam responses, 5 straight-liners, 6 partial completions, a Q2# matrix block, a date column stored as text, blank open-text answers, and a Q5 column mixing integers with free text like `about 10 hours`, `8-12`, and `n/a`. Each of those hits a different code path.

To build a larger fixture:

```bash
python tests/make_test_fixture.py tests/bigger_fixture.xlsx --rows 500
```

`tests/verify_conversion.txt` covers the rest of the procedure, including how to confirm the marimo dataflow graph builds cleanly and how to check that headless and interactive runs produce identical output.

---

## Output Files

The pipeline produces a full set of files to support every stage of your analysis.

| File Name                            | Description                                                  |
| ------------------------------------ | ------------------------------------------------------------ |
| `comprehensive_summary_report.html`  | **Primary report.** HTML document with key stats, quality checks, and response patterns. Open this first. |
| `analysis_ready_data.csv / .xlsx`    | **Clean dataset.** The file to load into your analysis software ([R](https://www.r-project.org), [Python](https://www.python.org), Tableau, etc.). Contains clean data with corrected types. |
| `sentiment_analysis_data.json`       | **NLP-ready dataset.** Structured JSON file for sentiment analysis, topic modeling, or other text-based analysis. This is the input for the `simple_sentiment_analyzer.py` script. |
| `sentiment_analysis_flattened.csv`   | **Flattened text data.** One row per response-question pair, for row-based text analysis tools. |
| `comprehensive_codebook.csv / .xlsx` | **Data dictionary.** Translates cryptic column names like `q5` into the full, human-readable question text. |
| `variable_summaries.xlsx`            | **Descriptive statistics.** Excel file with pre-calculated statistics (mean, median, counts) for all your variables. |
| `README.txt`                         | **Run manifest.** Generated alongside the outputs, recording what was produced and when. |

---

## License

This project is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to:

- Use, share, and adapt this work
- Use it at your job

Under these terms:

- **Attribution:** Credit the original author
- **NonCommercial:** No selling or commercial products
- **ShareAlike:** Derivatives must use the same license
