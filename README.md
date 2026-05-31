# qualtrics-processing-pipeline

[![Link Check](https://github.com/hihipy/qualtrics-processing-pipeline/actions/workflows/links.yml/badge.svg)](https://github.com/hihipy/qualtrics-processing-pipeline/actions/workflows/links.yml)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**Built with**

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org)
[![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org)
[![openpyxl](https://img.shields.io/badge/openpyxl-2E7D32?style=flat&logoColor=white)](https://openpyxl.readthedocs.io)
[![Tkinter](https://img.shields.io/badge/Tkinter-FFD43B?style=flat&logo=python&logoColor=black)](https://docs.python.org/3/library/tkinter.html)

A Python pipeline that turns raw Qualtrics Excel exports into a documented, analysis-ready package. It removes test data, corrects data types, and generates reports and codebooks automatically.

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

This Jupyter notebook ingests a raw Qualtrics Excel file and produces a documented analysis package. It handles the tedious data-janitor work so you can go straight from collecting data to analyzing it.

### Why a Jupyter Notebook?

A notebook keeps the process transparent, interactive, and easy to follow.

- **Step-by-step transparency:** The notebook breaks the pipeline into logical, sequential cells. You can run each step on its own and watch how the data changes, rather than running a single black-box script.
- **Interactivity and verification:** After running a cell, you can inspect the dataframes and intermediate outputs, which makes it simple to confirm each cleaning step is working as expected.
- **Integrated documentation:** Notebooks combine executable code, explanatory text, and outputs, which turns the tool into an interactive document where the "how" and "why" sit alongside the code.

---

## Features

- **Pop-up file selection:** Windows guide you to choose your input file and output folder.
- **Automated data cleaning:** Removes test data, standardizes values, and creates data quality flags.
- **Data typing:** Sets numbers, dates, and categories to the correct types to prevent common analysis errors.
- **HTML report:** Generates a single, shareable report with data quality metrics and response summaries.
- **NLP-ready JSON export:** Creates a structured JSON file for sentiment analysis or topic modeling.

---

## Getting Started

### First, You'll Need Jupyter Notebook

If you're new to Python or data analysis, the easiest way to get started is the **Anaconda Distribution**, a free, all-in-one package that includes Python, Jupyter Notebook, and the essential data science libraries.

1. **Download Anaconda:** Go to the [Anaconda Distribution page](https://www.anaconda.com/products/distribution) and download the installer for your operating system (Windows, macOS, or Linux).
2. **Install Anaconda:** Run the installer and follow the on-screen instructions. The default settings are fine.
3. **Launch Jupyter Notebook:** Once installed, open the **Anaconda Navigator** application. From the home screen, click "Launch" under Jupyter Notebook. A new tab will open in your web browser with the Jupyter file navigator.

### Running the Pipeline

1. **Set up your environment:**

   The required libraries (pandas, numpy, openpyxl) ship with Anaconda, so you're all set.

2. **Run the pipeline:**

   In the Jupyter browser tab, navigate to where you saved the `qualtrics_processing_pipeline.ipynb` file and click it to open. Then select "Run All Cells" from the "Cell" or "Run" menu at the top.

3. **Select your input file:**

   A window will pop up. Navigate to and select the raw Qualtrics Excel file (.xlsx or .xls) you want to process.

4. **Choose your output folder:**

   A second window will appear. Choose the folder where you want to save your clean files.

5. **Review your output:**

   Open your chosen output folder to find the finished, analysis-ready files.

---

## Output Files

The pipeline produces a full set of files to support every stage of your analysis.

| File Name                            | Description                                                  |
| ------------------------------------ | ------------------------------------------------------------ |
| `comprehensive_summary_report.html`  | **Primary report.** HTML document with key stats, quality checks, and response patterns. Open this first. |
| `analysis_ready_data.csv / .xlsx`    | **Clean dataset.** The file to load into your analysis software (R, Python, Tableau, etc.). Contains clean data with corrected types. |
| `sentiment_analysis_data.json`       | **NLP-ready dataset.** Structured JSON file for sentiment analysis, topic modeling, or other text-based analysis. This is the input for the `simple_sentiment_analyzer.py` script. |
| `comprehensive_codebook.csv / .xlsx` | **Data dictionary.** Translates cryptic column names like `q5` into the full, human-readable question text. |
| `variable_summaries.xlsx`            | **Descriptive statistics.** Excel file with pre-calculated statistics (mean, median, counts) for all your variables. |

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
