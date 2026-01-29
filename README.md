# Qualtrics Processing Pipeline

A Python pipeline that transforms raw Qualtrics Excel exports into a complete, documented, analysis-ready package. Handles test data removal, data type correction, and generates reports and codebooks automatically.

### The Challenge

Anyone who has worked with survey data knows that the real work begins after the data is collected. Raw exports from platforms like Qualtrics are a good starting point, but they come with challenges that can take hours of manual work to overcome:

- **Mixed-in Test Data:** Preview and test responses are often included, which can skew your results if not carefully removed.
- **Inconsistent Data Types:** Numbers and dates are often formatted as text, leading to errors when you try to perform calculations or create plots.
- **Cryptic Headers:** Column names like `Q5_3_TEXT` are meaningless without a legend, making your analysis slow and difficult to interpret.
- **Lack of Documentation:** The raw file provides no context, making it hard to trust the data or reproduce your cleaning process later.

This manual cleaning is not only time-consuming but also prone to human error, potentially compromising the integrity of your analysis.

### The Solution

This Jupyter Notebook provides a one-click solution to these challenges. It acts as a pipeline that ingests a raw Qualtrics Excel file and automatically produces a complete analysis package.

The pipeline handles all the tedious "data janitor" work, allowing you to move directly from data collection to analysis.

#### Why a Jupyter Notebook?

The choice of a Jupyter Notebook was deliberate to make the process transparent, interactive, and user-friendly.

- **Step-by-Step Transparency:** The notebook breaks the entire pipeline into logical, sequential cells. This allows you to run each step individually and observe how the data is transformed, rather than running a single "black box" script.
- **Interactivity and Verification:** After running a cell, you can easily inspect the dataframes and intermediate outputs. This makes it simple to verify that each step of the cleaning process is working as expected.
- **Integrated Documentation:** Notebooks allow for a rich combination of executable code, explanatory text, and outputs. This turns the tool into an interactive document where the "how" and "why" are explained alongside the code.

### Features

- **User-Friendly GUI:** Pop-up windows guide you to select your input file and output folder.
- **Automated Data Cleaning:** Automatically removes test data, standardizes values, and creates data quality flags.
- **Intelligent Data Typing:** Ensures numbers, dates, and categories are correctly formatted to prevent common analysis errors.
- **HTML Report:** Generates a single, shareable report with data quality metrics and response summaries.
- **NLP-Ready JSON Export:** Creates a structured JSON file for sentiment analysis or topic modeling.

### Getting Started

#### First, You'll Need Jupyter Notebook

If you're new to Python or data analysis, the easiest way to get started is by installing the **Anaconda Distribution**. It's a free, all-in-one package that includes Python, Jupyter Notebook, and all the essential data science libraries.

1. **Download Anaconda:** Go to the [Anaconda Distribution page](https://www.anaconda.com/products/distribution) and download the installer for your operating system (Windows, macOS, or Linux).
2. **Install Anaconda:** Run the installer, following the on-screen instructions. We recommend sticking with the default settings.
3. **Launch Jupyter Notebook:** Once installed, open the **Anaconda Navigator** application. From the Navigator's home screen, you'll see an icon for Jupyter Notebook. Click "Launch." A new tab will open in your web browser with the Jupyter file navigator.

#### Running the Pipeline

1. **Prepare Your Environment:**

   The required libraries (pandas, numpy, openpyxl) are included with the Anaconda installation, so you're all set.

2. **Run the Pipeline:**

   From the Jupyter Notebook browser tab, navigate to where you saved the `Qualtrics_Processing_Pipeline.ipynb` file and click on it to open. Once it's open, select "Run All Cells" from the "Cell" or "Run" menu at the top.

3. **Select Your Input File:**

   A window will pop up. Navigate to and select the raw Qualtrics Excel file (.xlsx or .xls) you want to process.

4. **Choose Your Output Folder:**

   A second window will appear. Choose the folder where you want to save your clean files.

5. **Review Your Output:**

   Navigate to your chosen output folder to find your complete set of analysis-ready files.

### Output Files

The pipeline produces a complete package of files to support every stage of your analysis.

| File Name                            | Description                                                  |
| ------------------------------------ | ------------------------------------------------------------ |
| `comprehensive_summary_report.html`  | **Primary Report.** HTML document with key stats, quality checks, and response patterns. Open this first. |
| `analysis_ready_data.csv / .xlsx`    | **Clean Dataset.** The file to load into your analysis software (R, Python, Tableau, etc.). Contains clean data with corrected types. |
| `sentiment_analysis_data.json`       | **NLP-Ready Dataset.** Structured JSON file for sentiment analysis, topic modeling, or other text-based analysis. This is the input for the `simple_sentiment_analyzer.py` script. |
| `comprehensive_codebook.csv / .xlsx` | **Data Dictionary.** Translates cryptic column names like `q5` into the full, human-readable question text. |
| `variable_summaries.xlsx`            | **Descriptive Statistics.** Excel file with pre-calculated statistics (mean, median, counts) for all your variables. |

### License

Qualtrics Processing Pipeline © 2025

Distributed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/deed.en).
