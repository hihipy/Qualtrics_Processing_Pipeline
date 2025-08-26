# Qualtrics Processing Pipeline

An automated Python pipeline to clean, validate, and prepare raw Qualtrics survey data for analysis. This script transforms messy Excel exports into a complete, documented, and analysis-ready package.

---

## The Challenge: The Hidden Work of Survey Data

Anyone who has worked with survey data knows that the real work begins *after* the data is collected. Raw exports from platforms like Qualtrics are a fantastic starting point, but they come with hidden challenges that can take hours or even days of tedious, manual work to overcome:

- **Mixed-in Test Data**: Preview and test responses are often included, which can skew results if not carefully removed.
- **Inconsistent Data Types**: Numbers and dates are often formatted as text, leading to errors when you try to perform calculations or create plots.
- **Cryptic Headers**: Column names like `Q5_3_TEXT` are meaningless without a legend, making analysis slow and difficult to interpret.
- **Lack of Documentation**: The raw file provides no context, making it hard to trust the data or reproduce the cleaning process later.

This manual cleaning process is not only time-consuming but also prone to human error, potentially compromising the integrity of your analysis.

---

## The Solution: An Automated Cleaning & Documentation Pipeline

This Jupyter Notebook provides a robust, one-click solution to these challenges. It acts as an intelligent pipeline that ingests a raw Qualtrics Excel file and automatically produces a complete, professional-grade analysis package.



The pipeline handles all the tedious "data janitor" work, allowing you to move directly from data collection to valuable analysis and insight.

---

## Why a Jupyter Notebook?

The choice of a Jupyter Notebook over a standard Python (`.py`) file was deliberate to make the process more transparent, interactive, and user-friendly.

- **Step-by-Step Transparency**: The notebook format breaks the entire cleaning pipeline into logical, sequential cells. This allows you to run each step individually and observe how the data is transformed, rather than running a single "black box" script.
- **Interactivity and Verification**: After running a cell, you can easily inspect the dataframes and intermediate outputs. This makes it simple to verify that each step of the cleaning process is working as expected.
- **Integrated Documentation**: Notebooks allow for a rich combination of executable code, explanatory text (like this!), and outputs. This turns the tool into an interactive document where the "how" and "why" are explained right alongside the code.
- **Accessibility for All Users**: The visual, step-by-step nature of notebooks makes them more approachable for a broad audience, including researchers and analysts who may not be expert programmers.

---

## Who is this for?

This tool is designed for anyone who works with survey data, including:

- **Data Analysts** who need to quickly move from raw data to actionable insights.
- **Researchers & Academics** who require a reproducible and well-documented cleaning process for their studies.
- **Survey Administrators** who need to provide clean, easy-to-use datasets to their teams.
- **Students & Aspiring Analysts** who want a real-world example of a best-practice data cleaning workflow.

---

## Key Features & Benefits

- **✨ User-Friendly GUI Interface**
  - **Benefit**: No need to edit code. Simple pop-up windows guide you to select your input file and output folder, making the tool accessible to users of all technical levels.

- **🤖 Automated Data Cleaning & Validation**
  - **Benefit**: Saves you hours of manual work and eliminates the risk of human error by automatically removing test data and standardizing values.

- **🧠 Intelligent Data Typing**
  - **Benefit**: Prevents common analysis errors by ensuring that numbers are treated as numbers, dates as dates, and categorical data as factors. Your charts and calculations will work on the first try.

- **📝 Comprehensive Documentation Suite**
  - **Benefit**: Builds trust and transparency. The pipeline doesn't just give you a clean file; it generates a codebook, a data quality report, and processing metadata, so you and your stakeholders know exactly what was done to the data.

---

## Getting Started: A Step-by-Step Guide

Getting from a raw export to an analysis-ready dataset takes just a few clicks.

1.  **Prepare Your Environment**: Make sure you have the necessary Python libraries installed. These are standard tools for data analysis.
    ```bash
    pip install pandas numpy openpyxl
    ```
2.  **Run the Pipeline**: Open the **`Qualtrics_Processing_Pipeline.ipynb`** file in a Jupyter environment (like Jupyter Lab or VS Code) and choose "Run All Cells" from the menu.

3.  **Select Your Input File**: A window will pop up. Navigate to and select the raw Qualtrics Excel file (`.xlsx` or `.xls`) you want to process.

4.  **Choose Your Output Folder**: A second window will appear. Choose the folder where you want to save your clean files. If you press "Cancel," the script will helpfully create a new folder named `outputs` for you.

5.  **Review Your Package!**: That's it! Navigate to your chosen output folder to find your complete set of analysis-ready files.

---

## The Final Product: Your Analysis-Ready Package 📊

The pipeline produces five meticulously crafted files to support every stage of your analysis.

- **`qualtrics_analysis_ready.csv`**: **Your Primary Dataset.** This is the file you'll load into your analysis software (like R, Python, Tableau, or Excel). It contains only the clean, genuine responses with corrected data types and helpful quality flags.
- **`qualtrics_codebook_comprehensive.csv`**: **Your Recipe Card.** This data dictionary translates cryptic column names into human-readable question text and provides essential metadata for each variable, such as the response rate.
- **`qualtrics_data_quality_report.json`**: **Your Quality Seal.** This report gives you a complete overview of the data's health, highlighting any potential issues and detailing every cleaning operation that was performed.
- **`qualtrics_variable_summaries.xlsx`**: **Your Head Start.** This Excel file contains pre-calculated descriptive statistics (like mean, median, and counts), completing the first step of exploratory data analysis for you.
- **`qualtrics_processing_metadata.json`**: **Your Audit Trail.** This file documents the entire pipeline run, ensuring your workflow is transparent, reproducible, and easy to report on.

---

## License

Qualtrics Processing Pipeline © 2025 – Distributed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).