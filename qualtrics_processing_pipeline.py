import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Qualtrics Processing Pipeline

        Turns a raw Qualtrics Excel export into a documented, analysis-ready package.

        Set `QUALTRICS_INPUT` and `QUALTRICS_OUTPUT` in the environment to run without
        the file dialogs. Leave them unset to get the original pop-up pickers.
        """
    )
    return


@app.cell
def _(mo):
    import json
    import os
    import re
    import warnings
    from datetime import datetime
    from pathlib import Path

    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        # Headless environment with no Tk toolkit. The file dialogs are unavailable,
        # so QUALTRICS_INPUT and QUALTRICS_OUTPUT have to supply the paths.
        tk = None
        filedialog = None

    import numpy as np
    import pandas as pd

    warnings.filterwarnings("ignore", category=UserWarning)

    if not mo.running_in_notebook():
        print(f"pandas {pd.__version__}, numpy {np.__version__}, marimo {mo.__version__}")

    mo.md(
        f"""
        **pandas** `{pd.__version__}` &middot; **numpy** `{np.__version__}` &middot; **marimo** `{mo.__version__}`
        """
    )
    return (Path, datetime, filedialog, json, np, os, pd, re, tk)


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Step 1: Load Qualtrics Excel File")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("### Universal Qualtrics Excel File Loader")
    return


@app.cell
def _(Path, filedialog, np, pd, re, tk):
    # Step 1: Universal Qualtrics Excel File Loader with Question Name Mapping
    # This code is designed to work with any Qualtrics export regardless of survey content
    # ENHANCED: Now captures and preserves the mapping between column IDs and question text


    def load_qualtrics_export(file_path=None, sheet_name=0):
        """
        Load a Qualtrics Excel export file with a GUI selector and robust error handling.
        ENHANCED: Now captures question name mapping from row 0.

        Parameters:
        -----------
        file_path : str or Path, optional
            Path to the Excel file. If None, a GUI file selector will open.
        sheet_name : str or int, default 0
            Sheet name or index to load from the Excel file

        Returns:
        --------
        dict : Contains 'raw_data' (DataFrame), 'file_info' (dict), 'quality_check' (dict),
               and 'question_mapping' (dict) mapping column names to question text
        """

        print("=== Step 1: Loading Qualtrics Export ===")

        # If no file_path is provided, open a GUI file selector
        if file_path is None:
            root = tk.Tk()
            root.withdraw()  # Hide the main tkinter window

            print("Opening file selector...")
            file_path = filedialog.askopenfilename(
                title="Select the Qualtrics Excel Export",
                filetypes=[("Excel Files", "*.xlsx *.xls"), ("All files", "*.*")]
            )

            if not file_path:  # Handle case where user closes the dialog
                raise FileNotFoundError("No file selected. Please run the script again.")

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Loading: {file_path.name}")

        # Load the Excel file with error handling
        try:
            # First, get sheet information
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            print(f"Available sheets: {sheet_names}")

            # Determine which sheet to load
            if isinstance(sheet_name, str) and sheet_name not in sheet_names:
                print(f"Warning: Sheet '{sheet_name}' not found. Using first sheet: '{sheet_names[0]}'")
                sheet_name = 0
            elif isinstance(sheet_name, int) and sheet_name >= len(sheet_names):
                print(f"Warning: Sheet index {sheet_name} out of range. Using first sheet: '{sheet_names[0]}'")
                sheet_name = 0

            actual_sheet = sheet_names[sheet_name] if isinstance(sheet_name, int) else sheet_name
            print(f"Loading sheet: '{actual_sheet}'")

            # Load the data
            raw_df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

        except Exception as e:
            raise Exception(f"Failed to load Excel file: {str(e)}")

        # File information
        file_info = {
            'filename': file_path.name,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'sheet_loaded': actual_sheet,
            'available_sheets': sheet_names,
            'raw_shape': raw_df.shape
        }

        print(f"File loaded successfully:")
        print(f"  Size: {file_info['file_size_mb']:.1f} MB")
        print(f"  Dimensions: {raw_df.shape[0]:,} rows x {raw_df.shape[1]:,} columns")

        # Quality checks to identify Qualtrics structure
        quality_check = analyze_qualtrics_structure(raw_df)

        # ENHANCED: Extract question mapping
        question_mapping = extract_question_mapping(raw_df, quality_check)

        return {
            'raw_data': raw_df,
            'file_info': file_info,
            'quality_check': quality_check,
            'question_mapping': question_mapping  # NEW: Added question mapping
        }

    def extract_question_mapping(df, quality_check):
        """
        Extract the mapping between column IDs and question text from row 0.
        NEW FUNCTION: Creates a comprehensive mapping for later use.

        Parameters:
        -----------
        df : pandas.DataFrame
            Raw Qualtrics data
        quality_check : dict
            Quality check results from structure analysis

        Returns:
        --------
        dict : Comprehensive question mapping with structure:
               {
                   'column_to_question': {column_id: question_text},
                   'has_question_text': bool,
                   'question_text_source': str,
                   'mapping_quality': str
               }
        """

        print("\n=== Extracting Question Mapping ===")

        mapping = {
            'column_to_question': {},
            'has_question_text': False,
            'question_text_source': 'none',
            'mapping_quality': 'not_available',
            'question_categories': {}
        }

        # Check if we have question text in row 0
        if quality_check.get('is_qualtrics_format') and len(df) > 0:
            row_0 = df.iloc[0]

            # Create the mapping for each column
            for col in df.columns:
                if col in row_0.index:
                    question_text = row_0[col]

                    # Handle various data types and null values
                    if pd.notna(question_text):
                        question_text_str = str(question_text).strip()

                        # Only map if we have meaningful text
                        if question_text_str and len(question_text_str) > 0:
                            mapping['column_to_question'][col] = question_text_str

                            # Categorize the question
                            if col.startswith('Q') or col.startswith('q'):
                                category = 'survey_question'
                            elif col in quality_check.get('standard_qualtrics_columns', []):
                                category = 'metadata'
                            else:
                                category = 'other'

                            if category not in mapping['question_categories']:
                                mapping['question_categories'][category] = []
                            mapping['question_categories'][category].append(col)
                    else:
                        # No question text for this column - use column name as fallback
                        mapping['column_to_question'][col] = col
                else:
                    # Column not in row 0 - use column name
                    mapping['column_to_question'][col] = col

            # Assess the quality of the mapping
            total_columns = len(df.columns)
            mapped_with_text = sum(1 for k, v in mapping['column_to_question'].items()
                                  if k != v and len(v) > len(k))

            if mapped_with_text > total_columns * 0.7:
                mapping['has_question_text'] = True
                mapping['question_text_source'] = 'row_0'
                mapping['mapping_quality'] = 'high'
                print(f"[SUCCESS] High quality question mapping extracted from row 0")
                print(f"  {mapped_with_text}/{total_columns} columns have descriptive question text")
            elif mapped_with_text > total_columns * 0.3:
                mapping['has_question_text'] = True
                mapping['question_text_source'] = 'row_0_partial'
                mapping['mapping_quality'] = 'medium'
                print(f"[SUCCESS] Partial question mapping extracted from row 0")
                print(f"  {mapped_with_text}/{total_columns} columns have descriptive question text")
            else:
                mapping['has_question_text'] = False
                mapping['question_text_source'] = 'column_names_only'
                mapping['mapping_quality'] = 'low'
                print(f"[WARNING] Limited question text available - using column names")
                print(f"  Only {mapped_with_text}/{total_columns} columns have descriptive text")
        else:
            # No row 0 or not Qualtrics format - use column names
            for col in df.columns:
                mapping['column_to_question'][col] = col
            mapping['question_text_source'] = 'column_names_only'
            print("[WARNING] No question text row found - using column names as labels")

        # Print mapping summary
        print(f"\nQuestion Mapping Summary:")
        for category, columns in mapping['question_categories'].items():
            print(f"  {category.replace('_', ' ').title()}: {len(columns)} columns")

        # Show sample mappings
        print(f"\nSample Question Mappings (first 3):")
        sample_count = 0
        for col, question in list(mapping['column_to_question'].items())[:10]:
            if col != question and col.startswith(('Q', 'q')):
                question_preview = question[:80] + "..." if len(question) > 80 else question
                print(f"  {col} -> {question_preview}")
                sample_count += 1
                if sample_count >= 3:
                    break

        return mapping

    def analyze_qualtrics_structure(df):
        """
        Analyze the loaded DataFrame to identify Qualtrics-specific patterns.
        (Unchanged from original)

        Parameters:
        -----------
        df : pandas.DataFrame
            Raw loaded data

        Returns:
        --------
        dict : Quality check results and structural analysis
        """

        print("\n=== Analyzing Qualtrics Structure ===")

        # Initialize quality check results
        quality_check = {
            'is_qualtrics_format': False,
            'header_row_index': None,
            'data_start_row': None,
            'standard_qualtrics_columns': [],
            'question_columns': [],
            'total_columns': len(df.columns),
            'potential_issues': []
        }

        # Standard Qualtrics metadata columns (regardless of survey content)
        standard_columns = [
            'StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress',
            'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId',
            'RecipientLastName', 'RecipientFirstName', 'RecipientEmail',
            'ExternalReference', 'LocationLatitude', 'LocationLongitude',
            'DistributionChannel', 'UserLanguage'
        ]

        # Check if this looks like a Qualtrics export
        columns_list = df.columns.tolist()
        standard_found = [col for col in standard_columns if col in columns_list]
        quality_check['standard_qualtrics_columns'] = standard_found

        # Qualtrics exports typically have these key identifiers
        qualtrics_indicators = ['ResponseId', 'StartDate', 'EndDate', 'Status']
        indicators_found = sum(1 for indicator in qualtrics_indicators if indicator in columns_list)

        if indicators_found >= 3:
            quality_check['is_qualtrics_format'] = True
            print("[SUCCESS] Confirmed Qualtrics export format")
        else:
            quality_check['potential_issues'].append("Does not appear to be standard Qualtrics export format")
            print("[WARNING] File may not be a standard Qualtrics export")

        # Identify question columns (typically start with Q followed by number)
        question_pattern = re.compile(r'^Q\d+', re.IGNORECASE)
        question_columns = [col for col in columns_list if question_pattern.match(str(col))]
        quality_check['question_columns'] = question_columns

        print(f"Standard Qualtrics columns found: {len(standard_found)}")
        print(f"Question columns identified: {len(question_columns)}")

        # Analyze row structure for header/data separation
        if quality_check['is_qualtrics_format']:
            header_analysis = analyze_header_structure(df)
            quality_check.update(header_analysis)

        # Check for common issues
        if df.shape[0] < 2:
            quality_check['potential_issues'].append("Very few rows - may not contain response data")

        if df.isnull().all().sum() > len(df.columns) * 0.5:
            quality_check['potential_issues'].append("Many completely empty columns detected")

        # Report findings
        if quality_check['potential_issues']:
            print("\n[WARNING] Potential Issues Detected:")
            for issue in quality_check['potential_issues']:
                print(f"  - {issue}")
        else:
            print("[SUCCESS] No structural issues detected")

        return quality_check

    def analyze_header_structure(df):
        """
        Analyze the DataFrame to identify where the header row and data rows are.
        (Unchanged from original)
        """

        header_info = {
            'header_row_index': 0,  # Qualtrics question text is typically in row 0
            'data_start_row': 1,    # Response data typically starts at row 1
            'response_type_column': None,
            'preview_responses_detected': False
        }

        # Check if there's a Status column to identify preview responses
        if 'Status' in df.columns:
            header_info['response_type_column'] = 'Status'

            # Look for preview responses in first few rows
            status_values = df['Status'].head(10).dropna().unique()
            if any('preview' in str(val).lower() for val in status_values):
                header_info['preview_responses_detected'] = True
                print("[SUCCESS] Preview responses detected in Status column")

        # Verify our assumptions by checking if row 0 contains question text
        if len(df) > 0:
            row_0_sample = df.iloc[0].dropna().head(3).tolist()
            avg_text_length = np.mean([len(str(val)) for val in row_0_sample]) if row_0_sample else 0

            if avg_text_length > 50:  # Long text suggests question descriptions
                print("[SUCCESS] Row 0 appears to contain question text (header row)")
            else:
                print("[WARNING] Row 0 may not contain typical Qualtrics question text")
                header_info.setdefault('potential_issues', []).append("Row 0 structure atypical for Qualtrics")

        return header_info

    # Example usage and testing
    return (load_qualtrics_export,)


@app.cell
def _(load_qualtrics_export, mo, os):
    result = load_qualtrics_export(file_path=os.environ.get("QUALTRICS_INPUT") or None)

    raw_data = result["raw_data"]
    file_info = result["file_info"]
    quality_check = result["quality_check"]
    question_mapping_raw = result["question_mapping"]

    if not mo.running_in_notebook():
        print("\n=== Loading Summary ===")
        print(f"File: {file_info['filename']}")
        print(f"Qualtrics format: {quality_check['is_qualtrics_format']}")
        print(f"Total responses: {raw_data.shape[0]:,}")
        print(f"Total columns: {raw_data.shape[1]:,}")
        print(f"Question columns: {len(quality_check['question_columns'])}")
        print(f"Standard metadata columns: {len(quality_check['standard_qualtrics_columns'])}")

        print("\nQuestion Mapping:")
        print(f"  Mapping quality: {question_mapping_raw['mapping_quality']}")
        print(f"  Question text available: {question_mapping_raw['has_question_text']}")
        print(f"  Source: {question_mapping_raw['question_text_source']}")

        print("\n=== Data Structure Preview ===")
        print("First few column names:")
        for _i, _col in enumerate(raw_data.columns[:8]):
            print(f"  {_i}: {_col}")
        if len(raw_data.columns) > 8:
            print(f"  ... and {len(raw_data.columns) - 8} more columns")

        print("\nFirst row sample (likely question text):")
        for _col, _val in raw_data.iloc[0].head(5).items():
            _preview = str(_val)[:60] + "..." if len(str(_val)) > 60 else str(_val)
            print(f"  {_col}: {_preview}")

        print("\n[SUCCESS] Step 1 Complete: file loaded and question mapping captured")

    mo.md(
        f"""
        ### Step 1 loaded `{file_info['filename']}`

        | Metric | Value |
        | --- | --- |
        | Qualtrics format | `{quality_check['is_qualtrics_format']}` |
        | Rows | {raw_data.shape[0]:,} |
        | Columns | {raw_data.shape[1]:,} |
        | Question columns | {len(quality_check['question_columns'])} |
        | Standard metadata columns | {len(quality_check['standard_qualtrics_columns'])} |
        | Question mapping quality | `{question_mapping_raw['mapping_quality']}` |
        | Question text source | `{question_mapping_raw['question_text_source']}` |
        """
    )
    return (result,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Step 2: Data Structure Separation")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("### Extract and Analyze Data Structure with Question Mapping")
    return


@app.cell
def _(np, pd):
    # Step 2a: Extract and Analyze Data Structure with Question Mapping
    # ENHANCED: Now preserves and utilizes question mapping from Step 1


    def extract_data_structure(result_from_step1):
        """
        Analyze and extract the data structure from a Qualtrics export.
        ENHANCED: Now preserves question mapping throughout the process.

        Parameters:
        -----------
        result_from_step1 : dict
            Result dictionary from Step 1 containing raw_data, file_info, quality_check, and question_mapping

        Returns:
        --------
        dict : Contains separated codebook, response_data, structure_analysis, and preserved question_mapping
        """

        print("=== Step 2a: Extracting Data Structure ===")

        raw_df = result_from_step1['raw_data']
        quality_check = result_from_step1['quality_check']
        question_mapping = result_from_step1.get('question_mapping', {})  # NEW: Get question mapping

        # Initialize structure analysis
        structure_analysis = {
            'codebook_source': None,
            'response_data_start_row': None,
            'header_type': None,
            'total_rows_analyzed': len(raw_df),
            'metadata_columns': [],
            'question_columns': [],
            'response_types_found': [],
            'has_question_mapping': bool(question_mapping.get('column_to_question'))  # NEW
        }

        # Identify metadata vs question columns
        metadata_patterns = [
            'StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress',
            'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId',
            'RecipientLastName', 'RecipientFirstName', 'RecipientEmail',
            'ExternalReference', 'LocationLatitude', 'LocationLongitude',
            'DistributionChannel', 'UserLanguage'
        ]

        all_columns = raw_df.columns.tolist()
        metadata_cols = [col for col in all_columns if col in metadata_patterns]
        question_cols = [col for col in all_columns if col not in metadata_patterns]

        structure_analysis['metadata_columns'] = metadata_cols
        structure_analysis['question_columns'] = question_cols

        print(f"Identified {len(metadata_cols)} metadata columns")
        print(f"Identified {len(question_cols)} question/data columns")

        # Determine header structure and codebook location
        codebook_info = analyze_codebook_structure(raw_df, structure_analysis)
        structure_analysis.update(codebook_info)

        # ENHANCED: Create comprehensive codebook with question mapping
        if structure_analysis['codebook_source'] == 'row_0':
            # Traditional Qualtrics format - row 0 has question text
            codebook_df = create_enhanced_codebook(raw_df.iloc[[0]], question_mapping, all_columns)
            response_data = raw_df.iloc[1:].copy()
            print("Extracted codebook from row 0 with question mapping")

        elif structure_analysis['codebook_source'] == 'column_names':
            # Alternative format - column names are the questions
            codebook_df = create_codebook_from_columns(all_columns, question_mapping)
            response_data = raw_df.copy()
            print("Using column names as codebook (no separate question text row)")

        elif structure_analysis['codebook_source'] == 'mixed':
            # Hybrid format - some info in row 0, but not full questions
            codebook_df = create_enhanced_codebook(raw_df.iloc[[0]], question_mapping, all_columns)
            response_data = raw_df.iloc[1:].copy()
            print("Extracted partial codebook from row 0 with question mapping (mixed format)")

        else:
            # Fallback - treat as simple structure
            codebook_df = create_codebook_from_columns(all_columns, question_mapping)
            response_data = raw_df.copy()
            print("Using fallback codebook structure with question mapping")

        # Reset response data index
        response_data.reset_index(drop=True, inplace=True)

        # Analyze response types and quality
        response_analysis = analyze_response_types(response_data, structure_analysis)
        structure_analysis.update(response_analysis)

        return {
            'codebook': codebook_df,
            'response_data': response_data,
            'structure_analysis': structure_analysis,
            'metadata_columns': metadata_cols,
            'question_columns': question_cols,
            'question_mapping': question_mapping  # NEW: Preserve question mapping
        }

    def create_enhanced_codebook(codebook_row, question_mapping, all_columns):
        """
        Create an enhanced codebook that combines row 0 data with question mapping.
        NEW FUNCTION: Integrates question mapping into codebook creation.

        Parameters:
        -----------
        codebook_row : pandas.DataFrame
            Row 0 containing question text
        question_mapping : dict
            Question mapping from Step 1
        all_columns : list
            All column names

        Returns:
        --------
        pandas.DataFrame : Enhanced codebook with multiple information sources
        """

        codebook_data = []
        column_to_question = question_mapping.get('column_to_question', {})

        for col in all_columns:
            # Get question text from multiple sources
            row_0_text = None
            if len(codebook_row) > 0 and col in codebook_row.columns:
                row_0_value = codebook_row[col].iloc[0]
                if pd.notna(row_0_value):
                    row_0_text = str(row_0_value).strip()

            # Get mapped question text
            mapped_text = column_to_question.get(col, col)

            # Determine the best question text to use
            if row_0_text and len(row_0_text) > len(col):
                final_question_text = row_0_text
                text_source = 'row_0'
            elif mapped_text != col:
                final_question_text = mapped_text
                text_source = 'mapping'
            else:
                final_question_text = col
                text_source = 'column_name'

            # Determine question type
            if col.startswith(('Q', 'q')):
                question_type = 'survey_question'
            elif col in ['StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress',
                         'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId',
                         'RecipientLastName', 'RecipientFirstName', 'RecipientEmail',
                         'ExternalReference', 'LocationLatitude', 'LocationLongitude',
                         'DistributionChannel', 'UserLanguage']:
                question_type = 'metadata'
            else:
                question_type = 'other'

            codebook_data.append({
                'column_id': col,
                'question_text': final_question_text,
                'text_source': text_source,
                'question_type': question_type,
                'text_length': len(final_question_text)
            })

        codebook_df = pd.DataFrame(codebook_data)

        # Summary statistics
        print(f"\nCodebook Creation Summary:")
        source_counts = codebook_df['text_source'].value_counts()
        for source, count in source_counts.items():
            print(f"  {source}: {count} columns")

        return codebook_df

    def create_codebook_from_columns(all_columns, question_mapping):
        """
        Create a codebook when no row 0 question text is available.

        Parameters:
        -----------
        all_columns : list
            All column names
        question_mapping : dict
            Question mapping from Step 1

        Returns:
        --------
        pandas.DataFrame : Codebook based on column names and mapping
        """

        codebook_data = []
        column_to_question = question_mapping.get('column_to_question', {})

        for col in all_columns:
            mapped_text = column_to_question.get(col, col)

            # Determine question type
            if col.startswith(('Q', 'q')):
                question_type = 'survey_question'
            elif col in ['StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress',
                         'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId',
                         'RecipientLastName', 'RecipientFirstName', 'RecipientEmail',
                         'ExternalReference', 'LocationLatitude', 'LocationLongitude',
                         'DistributionChannel', 'UserLanguage']:
                question_type = 'metadata'
            else:
                question_type = 'other'

            codebook_data.append({
                'column_id': col,
                'question_text': mapped_text,
                'text_source': 'mapping' if mapped_text != col else 'column_name',
                'question_type': question_type,
                'text_length': len(mapped_text)
            })

        return pd.DataFrame(codebook_data)

    def analyze_codebook_structure(df, structure_info):
        """
        Determine how the codebook/question text is stored in this export.
        (Mostly unchanged, minor formatting updates)
        """

        print("\n--- Analyzing Codebook Structure ---")

        codebook_info = {
            'codebook_source': 'unknown',
            'header_type': 'unknown',
            'codebook_quality': 'unknown'
        }

        if len(df) == 0:
            print("Warning: No data rows to analyze")
            return codebook_info

        # Examine row 0 to see if it contains question text
        row_0 = df.iloc[0]

        # Calculate metrics to determine if row 0 has question text
        non_null_values = row_0.dropna()
        if len(non_null_values) == 0:
            print("Row 0 is completely empty")
            codebook_info['codebook_source'] = 'column_names'
            codebook_info['header_type'] = 'empty_row_0'
            return codebook_info

        # Analyze text characteristics of row 0
        avg_length = np.mean([len(str(val)) for val in non_null_values])
        max_length = max([len(str(val)) for val in non_null_values])

        # Look for question-like patterns
        question_patterns = 0
        for val in non_null_values.head(10):  # Check first 10 non-null values
            str_val = str(val).lower()
            if any(pattern in str_val for pattern in ['which of', 'please', 'identify', 'provide', '?']):
                question_patterns += 1

        print(f"Row 0 analysis:")
        print(f"  Average text length: {avg_length:.1f} characters")
        print(f"  Maximum text length: {max_length} characters")
        print(f"  Question-like patterns found: {question_patterns}")

        # Decision logic for codebook source
        if avg_length > 30 and question_patterns >= 2:
            codebook_info['codebook_source'] = 'row_0'
            codebook_info['header_type'] = 'full_questions'
            codebook_info['codebook_quality'] = 'high'
            print("[SUCCESS] Row 0 contains full question text")

        elif avg_length > 15 and max_length > 20:
            codebook_info['codebook_source'] = 'mixed'
            codebook_info['header_type'] = 'descriptive_headers'
            codebook_info['codebook_quality'] = 'medium'
            print("[SUCCESS] Row 0 contains descriptive headers (not full questions)")

        elif avg_length < 10:
            codebook_info['codebook_source'] = 'column_names'
            codebook_info['header_type'] = 'short_labels'
            codebook_info['codebook_quality'] = 'low'
            print("[SUCCESS] Row 0 contains short labels - using column names as codebook")

        else:
            codebook_info['codebook_source'] = 'mixed'
            codebook_info['header_type'] = 'mixed_format'
            codebook_info['codebook_quality'] = 'medium'
            print("[INFO] Mixed format detected - treating as partial codebook")

        return codebook_info

    def analyze_response_types(df, structure_info):
        """
        Analyze the types of responses in the data (real vs test responses).
        (Unchanged from original)
        """

        print("\n--- Analyzing Response Types ---")

        response_info = {
            'total_responses': len(df),
            'response_types_found': [],
            'test_responses': 0,
            'genuine_responses': 0,
            'response_type_column': None
        }

        if len(df) == 0:
            print("No response data to analyze")
            return response_info

        # Look for Status column to identify response types
        status_columns = [col for col in df.columns if 'status' in col.lower()]

        if status_columns:
            status_col = status_columns[0]  # Use first status column found
            response_info['response_type_column'] = status_col

            # Analyze response types
            status_counts = df[status_col].value_counts(dropna=False)
            response_info['response_types_found'] = status_counts.to_dict()

            print(f"Response types found in '{status_col}':")
            for resp_type, count in status_counts.items():
                percentage = (count / len(df)) * 100
                print(f"  {resp_type}: {count} responses ({percentage:.1f}%)")

                # Categorize as test vs genuine
                if pd.isna(resp_type):
                    continue
                elif any(keyword in str(resp_type).lower() for keyword in ['preview', 'test', 'spam']):
                    response_info['test_responses'] += count
                else:
                    response_info['genuine_responses'] += count

        else:
            print("No Status column found - assuming all responses are genuine")
            response_info['genuine_responses'] = len(df)

        # Additional data quality checks
        completion_info = analyze_completion_patterns(df)
        response_info.update(completion_info)

        return response_info

    def analyze_completion_patterns(df):
        """
        Analyze completion patterns and data quality indicators.
        (Unchanged from original)
        """

        completion_info = {
            'has_progress_data': False,
            'has_duration_data': False,
            'completion_rate_available': False,
            'data_quality_indicators': []
        }

        # Check for progress tracking
        progress_columns = [col for col in df.columns if 'progress' in col.lower()]
        if progress_columns:
            completion_info['has_progress_data'] = True
            progress_col = progress_columns[0]

            # Analyze completion rates
            if df[progress_col].notna().sum() > 0:
                completion_info['completion_rate_available'] = True
                complete_responses = (df[progress_col] == 100).sum() if (df[progress_col] == 100).any() else 0
                completion_rate = (complete_responses / len(df)) * 100
                completion_info['completion_rate'] = completion_rate
                print(f"Survey completion rate: {completion_rate:.1f}%")

        # Check for duration data
        duration_columns = [col for col in df.columns if 'duration' in col.lower()]
        if duration_columns:
            completion_info['has_duration_data'] = True
            duration_col = duration_columns[0]

            if df[duration_col].notna().sum() > 0:
                median_duration = df[duration_col].median()
                completion_info['median_duration_seconds'] = median_duration
                print(f"Median completion time: {median_duration/60:.1f} minutes")

        # Data quality flags
        if completion_info.get('completion_rate', 100) < 70:
            completion_info['data_quality_indicators'].append('Low completion rate')

        return completion_info

    # Example usage
    return (extract_data_structure,)


@app.cell
def _(extract_data_structure, mo, result):
    structure_result = extract_data_structure(result)

    codebook = structure_result["codebook"]
    response_data = structure_result["response_data"]
    structure_analysis = structure_result["structure_analysis"]

    if not mo.running_in_notebook():
        print("\n=== Step 2a Summary ===")
        print(f"Codebook source: {structure_analysis['codebook_source']}")
        print(f"Codebook shape: {codebook.shape}")
        print(f"Response data shape: {response_data.shape}")
        print(f"Total genuine responses: {structure_analysis.get('genuine_responses', 'Unknown')}")
        print(f"Total test responses: {structure_analysis.get('test_responses', 0)}")
        print(f"Question mapping preserved: {structure_analysis.get('has_question_mapping', False)}")

        if structure_analysis.get("completion_rate_available"):
            print(f"Completion rate: {structure_analysis.get('completion_rate', 0):.1f}%")

        if len(codebook) > 0:
            print("\nCodebook Quality:")
            print(f"  Total entries: {len(codebook)}")
            if "text_source" in codebook.columns:
                for _source, _count in codebook["text_source"].value_counts().items():
                    print(f"  {_source}: {_count} columns")

        print("\n[SUCCESS] Step 2a Complete: structure extracted, question mapping preserved")

    mo.md(
        f"""
        ### Step 2a separated the codebook from the responses

        | Metric | Value |
        | --- | --- |
        | Codebook source | `{structure_analysis['codebook_source']}` |
        | Codebook shape | {codebook.shape[0]:,} x {codebook.shape[1]:,} |
        | Response data shape | {response_data.shape[0]:,} x {response_data.shape[1]:,} |
        | Genuine responses | {structure_analysis.get('genuine_responses', 'Unknown')} |
        | Test responses | {structure_analysis.get('test_responses', 0)} |
        | Question mapping preserved | `{structure_analysis.get('has_question_mapping', False)}` |
        """
    )
    return (structure_result,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("### Clean and Filter Response Data")
    return


@app.cell
def _(np, pd, re):
    # Step 2b: Clean and Filter Response Data with Question Mapping Preservation
    # ENHANCED: Preserves question mapping through cleaning process


    def clean_and_filter_responses(structure_result):
        """
        Clean the response data by removing test responses and applying universal cleaning rules.
        ENHANCED: Preserves question mapping throughout the cleaning process.

        Parameters:
        -----------
        structure_result : dict
            Result from Step 2a containing codebook, response_data, structure_analysis, and question_mapping

        Returns:
        --------
        dict : Contains cleaned_data, quality_flags, cleaning_log, summary_stats, and preserved question_mapping
        """

        print("=== Step 2b: Cleaning and Filtering Response Data ===")

        response_data = structure_result['response_data'].copy()
        analysis = structure_result['structure_analysis']
        question_mapping = structure_result.get('question_mapping', {})  # NEW: Get question mapping
        codebook = structure_result.get('codebook', pd.DataFrame())  # NEW: Get codebook

        cleaning_log = []
        initial_row_count = len(response_data)

        print(f"Starting with {initial_row_count:,} total responses")
        if question_mapping:
            print(f"Question mapping preserved for {len(question_mapping.get('column_to_question', {}))} columns")

        # Step 1: Remove test/preview responses
        genuine_data = filter_test_responses(response_data, analysis, cleaning_log)

        # Step 2: Create data quality flags (before removing any data)
        flagged_data = create_quality_flags(genuine_data, analysis, cleaning_log)

        # Step 3: Apply universal cleaning rules
        cleaned_data = apply_universal_cleaning(flagged_data, cleaning_log)

        # Step 4: Standardize column names (but preserve mapping)
        final_data, updated_mapping = standardize_column_names_with_mapping(
            cleaned_data,
            structure_result['metadata_columns'],
            structure_result['question_columns'],
            cleaning_log,
            question_mapping,
            codebook
        )

        # Generate summary statistics
        summary_stats = generate_cleaning_summary(initial_row_count, final_data, cleaning_log)

        return {
            'cleaned_data': final_data,
            'cleaning_log': cleaning_log,
            'summary_stats': summary_stats,
            'original_columns': response_data.columns.tolist(),
            'final_columns': final_data.columns.tolist(),
            'question_mapping': updated_mapping,  # NEW: Preserve updated mapping
            'codebook': codebook  # NEW: Preserve codebook
        }

    def filter_test_responses(df, analysis, cleaning_log):
        """
        Remove test responses (Survey Preview, Spam, etc.) while preserving genuine responses.
        (Minor updates for better handling)
        """

        print("\n--- Filtering Test Responses ---")

        initial_count = len(df)

        # Define test response patterns (case-insensitive)
        test_patterns = [
            'survey preview', 'preview', 'test', 'spam', 'survey test'
        ]

        if analysis.get('response_type_column'):
            status_col = analysis['response_type_column']

            # Identify test responses
            test_mask = pd.Series([False] * len(df), index=df.index)

            for pattern in test_patterns:
                pattern_mask = df[status_col].astype(str).str.lower().str.contains(pattern, na=False)
                test_mask = test_mask | pattern_mask

            test_count = test_mask.sum()
            genuine_data = df[~test_mask].copy().reset_index(drop=True)

            cleaning_log.append(f"Removed {test_count} test responses based on Status column patterns")
            print(f"Removed {test_count} test responses ({test_count/initial_count*100:.1f}%)")
            print(f"Retained {len(genuine_data)} genuine responses ({len(genuine_data)/initial_count*100:.1f}%)")

        else:
            # No status column - assume all are genuine
            genuine_data = df.copy()
            cleaning_log.append("No status column found - retained all responses as genuine")
            print("No status column found - assuming all responses are genuine")

        return genuine_data

    def create_quality_flags(df, analysis, cleaning_log):
        """
        Create data quality flags without removing data - for transparent analysis.
        Enhanced with better handling of low completion rates.
        """

        print("\n--- Creating Data Quality Flags ---")

        flagged_data = df.copy()
        flags_created = 0

        # Flag 1: Survey completion status (especially important given 37% completion rate)
        if analysis.get('has_progress_data'):
            progress_cols = [col for col in df.columns if 'progress' in col.lower()]
            if progress_cols:
                progress_col = progress_cols[0]
                flagged_data['flag_incomplete'] = df[progress_col] < 100
                incomplete_count = flagged_data['flag_incomplete'].sum()
                print(f"Created flag_incomplete: {incomplete_count} responses ({incomplete_count/len(df)*100:.1f}%)")

                # Additional flag for very low completion (< 50%)
                flagged_data['flag_very_incomplete'] = df[progress_col] < 50
                very_incomplete_count = flagged_data['flag_very_incomplete'].sum()
                print(f"Created flag_very_incomplete: {very_incomplete_count} responses ({very_incomplete_count/len(df)*100:.1f}%)")
                flags_created += 2

        # Flag 2: Duration outliers
        if analysis.get('has_duration_data'):
            duration_cols = [col for col in df.columns if 'duration' in col.lower()]
            if duration_cols:
                duration_col = duration_cols[0]

                # Convert to numeric if needed
                duration_numeric = pd.to_numeric(df[duration_col], errors='coerce')

                # Flag very short responses (< 60 seconds)
                flagged_data['flag_duration_too_short'] = duration_numeric < 60
                short_count = flagged_data['flag_duration_too_short'].sum()

                # Flag very long responses (> 2 hours = 7200 seconds)
                flagged_data['flag_duration_too_long'] = duration_numeric > 7200
                long_count = flagged_data['flag_duration_too_long'].sum()

                print(f"Created flag_duration_too_short: {short_count} responses ({short_count/len(df)*100:.1f}%)")
                print(f"Created flag_duration_too_long: {long_count} responses ({long_count/len(df)*100:.1f}%)")
                flags_created += 2

        # Flag 3: Response pattern flags (straight-lining, etc.)
        pattern_flags = create_response_pattern_flags(df, cleaning_log)
        for flag_name, flag_data in pattern_flags.items():
            flagged_data[flag_name] = flag_data
            flag_count = flag_data.sum()
            print(f"Created {flag_name}: {flag_count} responses ({flag_count/len(df)*100:.1f}%)")
            flags_created += 1

        # Summary of flagging
        flag_columns = [col for col in flagged_data.columns if col.startswith('flag_')]
        if flag_columns:
            total_flagged = flagged_data[flag_columns].any(axis=1).sum()
            print(f"\nTotal flags created: {flags_created}")
            print(f"Responses with any flag: {total_flagged} ({total_flagged/len(df)*100:.1f}%)")
            print(f"Clean responses (no flags): {len(df)-total_flagged} ({(len(df)-total_flagged)/len(df)*100:.1f}%)")
        else:
            total_flagged = 0
            print(f"\nTotal flags created: {flags_created}")

        cleaning_log.append(f"Created {flags_created} quality flag types affecting {total_flagged} responses")

        return flagged_data

    def create_response_pattern_flags(df, cleaning_log):
        """
        Create flags for suspicious response patterns.
        (Unchanged from original)
        """

        pattern_flags = {}

        # Find potential rating/scale columns (likely to show straight-lining)
        question_cols = [col for col in df.columns if not any(meta in col for meta in
                        ['Date', 'Status', 'IP', 'Progress', 'Duration', 'Finished', 'Recorded', 'Response', 'Recipient', 'External', 'Location', 'Distribution', 'Language'])]

        # Look for columns that might be scales (numeric responses)
        numeric_question_cols = []
        for col in question_cols:
            # Try to convert to numeric and see if it's reasonable scale data
            numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(numeric_vals) > 0:
                unique_vals = numeric_vals.unique()
                if len(unique_vals) <= 10 and numeric_vals.min() >= 0 and numeric_vals.max() <= 10:
                    numeric_question_cols.append(col)

        # Flag potential straight-lining if we have scale columns
        if len(numeric_question_cols) >= 3:
            straightline_flags = []
            for idx, row in df.iterrows():
                scale_responses = []
                for col in numeric_question_cols[:10]:  # Check up to 10 scale columns
                    val = pd.to_numeric(row[col], errors='coerce')
                    if not pd.isna(val):
                        scale_responses.append(val)

                # Flag if 80% or more of scale responses are identical (and we have at least 3 responses)
                if len(scale_responses) >= 3:
                    most_common_val = max(set(scale_responses), key=scale_responses.count)
                    same_response_pct = scale_responses.count(most_common_val) / len(scale_responses)
                    straightline_flags.append(same_response_pct >= 0.8)
                else:
                    straightline_flags.append(False)

            pattern_flags['flag_potential_straightlining'] = pd.Series(straightline_flags, index=df.index)

        return pattern_flags

    def apply_universal_cleaning(df, cleaning_log):
        """
        Apply universal data cleaning rules that work across all surveys.
        (Unchanged from original)
        """

        print("\n--- Applying Universal Cleaning Rules ---")

        cleaned_data = df.copy()
        changes_made = 0

        # Rule 1: Standardize NA representations
        na_patterns = {
            r'^\s*n\s*a\s*$': np.nan,           # "n a", "N A", " na ", etc.
            r'^\s*n/a\s*$': np.nan,             # "n/a", "N/A", " n/a ", etc.
            r'^\s*na\s*$': np.nan,              # "na", "NA", " na ", etc.
            r'^\s*none\s*$': np.nan,            # "none", "None", " none ", etc.
            r'^\s*null\s*$': np.nan,            # "null", "Null", etc.
            r'^\s*$': np.nan                    # Empty strings and whitespace-only
        }

        initial_nulls = cleaned_data.isnull().sum().sum()

        for pattern, replacement in na_patterns.items():
            for col in cleaned_data.columns:
                if cleaned_data[col].dtype == 'object':
                    mask = cleaned_data[col].astype(str).str.match(pattern, case=False, na=False)
                    if mask.any():
                        cleaned_data.loc[mask, col] = replacement
                        changes_made += mask.sum()

        final_nulls = cleaned_data.isnull().sum().sum()
        na_changes = final_nulls - initial_nulls

        if na_changes > 0:
            print(f"Standardized NA representations: +{na_changes} null values created")
            cleaning_log.append(f"Standardized {na_changes} NA representations to null values")

        # Rule 2: Standardize Yes/No responses
        yes_no_patterns = {
            r'^\s*yes\s*\.?\s*$': 'Yes',        # "yes", "Yes.", " yes ", etc.
            r'^\s*no\s*\.?\s*$': 'No',          # "no", "No.", " no ", etc.
            r'^\s*y\s*$': 'Yes',                # "y", "Y"
            r'^\s*n\s*$': 'No'                  # "n", "N"
        }

        yes_no_changes = 0
        for pattern, replacement in yes_no_patterns.items():
            for col in cleaned_data.columns:
                if cleaned_data[col].dtype == 'object':
                    mask = cleaned_data[col].astype(str).str.match(pattern, case=False, na=False)
                    if mask.any():
                        cleaned_data.loc[mask, col] = replacement
                        yes_no_changes += mask.sum()

        if yes_no_changes > 0:
            print(f"Standardized Yes/No responses: {yes_no_changes} changes made")
            cleaning_log.append(f"Standardized {yes_no_changes} Yes/No response formats")

        print(f"Universal cleaning complete: {changes_made + yes_no_changes} total changes")

        return cleaned_data

    def standardize_column_names_with_mapping(df, metadata_cols, question_cols, cleaning_log, question_mapping, codebook):
        """
        Standardize column names while preserving the question mapping.
        FIXED: Preserves the # character for matrix questions like Q2#1_1_1
        """

        print("\n--- Standardizing Column Names ---")

        final_data = df.copy()

        # Get the original mapping
        original_mapping = question_mapping.get('column_to_question', {})

        # Create column name mapping
        column_mapping = {}
        updated_question_mapping = {'column_to_question': {}}

        for col in df.columns:
            # FIXED: Special handling for # character - treat it like a letter
            # Replace special characters EXCEPT # with underscore
            clean_name = re.sub(r'[^\w\s#]', '_', col)  # Added # to the exclusion pattern
            clean_name = re.sub(r'\s+', '_', clean_name)  # Replace spaces with underscore
            clean_name = re.sub(r'_+', '_', clean_name)  # Replace multiple underscores with single
            clean_name = clean_name.strip('_').lower()  # Remove leading/trailing underscores and lowercase

            # Ensure name is not empty
            if not clean_name:
                clean_name = f"col_{df.columns.get_loc(col)}"

            column_mapping[col] = clean_name

            # Update the question mapping with new column names
            if col in original_mapping:
                updated_question_mapping['column_to_question'][clean_name] = original_mapping[col]
            else:
                updated_question_mapping['column_to_question'][clean_name] = col

        # Apply column name changes
        final_data.rename(columns=column_mapping, inplace=True)

        # Update other parts of question_mapping
        updated_question_mapping['has_question_text'] = question_mapping.get('has_question_text', False)
        updated_question_mapping['question_text_source'] = question_mapping.get('question_text_source', 'unknown')
        updated_question_mapping['mapping_quality'] = question_mapping.get('mapping_quality', 'unknown')

        # Update question categories with new column names
        if 'question_categories' in question_mapping:
            updated_categories = {}
            for category, columns in question_mapping['question_categories'].items():
                updated_cols = [column_mapping.get(col, col) for col in columns if col in column_mapping]
                updated_categories[category] = updated_cols
            updated_question_mapping['question_categories'] = updated_categories

        # Report changes
        changes_made = sum(1 for old, new in column_mapping.items() if old != new)
        print(f"Standardized {changes_made} column names")
        print(f"Question mapping updated for {len(updated_question_mapping['column_to_question'])} columns")

        # Show examples of changes
        if changes_made > 0:
            print("Sample column name changes:")
            examples_shown = 0
            for old, new in column_mapping.items():
                if old != new and examples_shown < 5:
                    print(f"  '{old}' -> '{new}'")
                    examples_shown += 1
            if changes_made > 5:
                print(f"  ... and {changes_made - 5} more changes")

        cleaning_log.append(f"Standardized {changes_made} column names while preserving question mapping")

        return final_data, updated_question_mapping

    def generate_cleaning_summary(initial_count, final_data, cleaning_log):
        """
        Generate comprehensive summary of cleaning operations.
        Enhanced to include question mapping status.
        """

        final_count = len(final_data)
        flag_columns = [col for col in final_data.columns if col.startswith('flag_')]

        summary = {
            'initial_responses': initial_count,
            'final_responses': final_count,
            'responses_removed': initial_count - final_count,
            'removal_rate_pct': ((initial_count - final_count) / initial_count * 100) if initial_count > 0 else 0,
            'quality_flags_created': len(flag_columns),
            'flagged_responses': final_data[flag_columns].any(axis=1).sum() if flag_columns else 0,
            'clean_responses': final_count - (final_data[flag_columns].any(axis=1).sum() if flag_columns else 0),
            'cleaning_operations': len(cleaning_log),
            'total_columns': len(final_data.columns),
            'flag_columns': len(flag_columns)
        }

        return summary

    # Example usage
    return (clean_and_filter_responses,)


@app.cell
def _(clean_and_filter_responses, mo, structure_result):
    cleaning_result = clean_and_filter_responses(structure_result)

    cleaned_data = cleaning_result["cleaned_data"]
    cleaning_summary = cleaning_result["summary_stats"]
    updated_mapping = cleaning_result.get("question_mapping", {})

    _final = cleaning_summary["final_responses"] or 1

    if not mo.running_in_notebook():
        print("\n=== Step 2b Summary ===")
        print("Data cleaning completed:")
        print(f"  Initial responses: {cleaning_summary['initial_responses']:,}")
        print(f"  Final responses: {cleaning_summary['final_responses']:,}")
        print(f"  Responses removed: {cleaning_summary['responses_removed']} ({cleaning_summary['removal_rate_pct']:.1f}%)")
        print(f"  Quality flags created: {cleaning_summary['quality_flags_created']}")
        print(f"  Flagged responses: {cleaning_summary['flagged_responses']} ({cleaning_summary['flagged_responses'] / _final * 100:.1f}%)")
        print(f"  Clean responses: {cleaning_summary['clean_responses']} ({cleaning_summary['clean_responses'] / _final * 100:.1f}%)")
        print(f"  Final data shape: {cleaned_data.shape[0]:,} x {cleaned_data.shape[1]:,}")

        if updated_mapping:
            print("\nQuestion Mapping Status:")
            print("  Mapping preserved: Yes")
            print(f"  Mapped columns: {len(updated_mapping.get('column_to_question', {}))}")
            print(f"  Mapping quality: {updated_mapping.get('mapping_quality', 'unknown')}")

        print("\n[SUCCESS] Step 2b Complete: data cleaned, quality flags added, mapping preserved")

    mo.md(
        f"""
        ### Step 2b cleaned the response data

        | Metric | Value |
        | --- | --- |
        | Initial responses | {cleaning_summary['initial_responses']:,} |
        | Final responses | {cleaning_summary['final_responses']:,} |
        | Removed | {cleaning_summary['responses_removed']} ({cleaning_summary['removal_rate_pct']:.1f}%) |
        | Quality flags created | {cleaning_summary['quality_flags_created']} |
        | Flagged responses | {cleaning_summary['flagged_responses']} ({cleaning_summary['flagged_responses'] / _final * 100:.1f}%) |
        | Clean responses | {cleaning_summary['clean_responses']} ({cleaning_summary['clean_responses'] / _final * 100:.1f}%) |
        | Final shape | {cleaned_data.shape[0]:,} x {cleaned_data.shape[1]:,} |
        | Mapped columns | {len(updated_mapping.get('column_to_question', {}))} |
        """
    )
    return (cleaning_result,)


@app.cell
def _(cleaning_result, mo):
    # Quick diagnostic after Step 2b
    q2_cols_cleaned = [
        col for col in cleaning_result["cleaned_data"].columns if "q2" in col.lower()
    ]

    q2_mapping = {
        k: v
        for k, v in cleaning_result.get("question_mapping", {})
        .get("column_to_question", {})
        .items()
        if "q2" in k.lower()
    }

    if not mo.running_in_notebook():
        print(f"\nQ2 columns after cleaning: {len(q2_cols_cleaned)}")
        for _col in q2_cols_cleaned[:5]:
            print(f"  {_col}")

        print(f"\nQ2 columns in updated mapping: {len(q2_mapping)}")
        for _k, _v in list(q2_mapping.items())[:3]:
            print(f"  {_k} -> {_v[:50]}...")

    mo.md(
        f"""
        Diagnostic: **{len(q2_cols_cleaned)}** Q2 columns after cleaning,
        **{len(q2_mapping)}** of them present in the updated question mapping.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Step 3: Data Type Optimization and Validation")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("### Intelligent Data Type Detection")
    return


@app.cell
def _(pd, re):
    # Step 3a: Intelligent Data Type Detection with Question Mapping
    # ENHANCED: Uses question text to inform data type decisions and preserves mapping


    def detect_and_assign_data_types(cleaning_result):
        """
        Intelligently detect and assign appropriate data types for all columns.
        ENHANCED: Uses question mapping to inform type detection decisions.

        Parameters:
        -----------
        cleaning_result : dict
            Result from Step 2b containing cleaned_data, question_mapping, and metadata

        Returns:
        --------
        dict : Contains typed_data, type_analysis, conversion_log, validation_results, and preserved question_mapping
        """

        print("=== Step 3a: Intelligent Data Type Detection ===")

        df = cleaning_result['cleaned_data'].copy()
        question_mapping = cleaning_result.get('question_mapping', {})
        codebook = cleaning_result.get('codebook', pd.DataFrame())
        initial_dtypes = df.dtypes.to_dict()

        # Get question text mapping for informed type detection
        column_to_question = question_mapping.get('column_to_question', {})

        print(f"Using question mapping for {len(column_to_question)} columns to inform type detection")

        # Initialize tracking structures
        type_analysis = {
            'columns_analyzed': len(df.columns),
            'conversions_attempted': 0,
            'conversions_successful': 0,
            'columns_by_final_type': {},
            'problematic_columns': [],
            'mapping_informed_decisions': 0  # NEW: Track mapping-informed decisions
        }

        conversion_log = []

        # Skip flag columns and ID columns from type conversion
        skip_columns = get_columns_to_skip(df)

        # Analyze each column for optimal data type
        typed_data = df.copy()

        for col in df.columns:
            if col in skip_columns:
                conversion_log.append(f"{col}: Skipped (administrative/flag column)")
                continue

            # Get question text for this column
            question_text = column_to_question.get(col, col)

            print(f"\nAnalyzing column: {col}")
            if question_text != col and len(question_text) > len(col):
                print(f"  Question text: {question_text[:60]}...")

            # Use question-aware type detection
            type_result = analyze_column_for_type_with_context(
                df[col],
                col,
                question_text
            )

            if type_result.get('mapping_informed'):
                type_analysis['mapping_informed_decisions'] += 1

            if type_result['recommended_type'] != 'object':
                type_analysis['conversions_attempted'] += 1

                # Attempt the conversion
                conversion_success = apply_type_conversion(typed_data, col, type_result, conversion_log)

                if conversion_success:
                    type_analysis['conversions_successful'] += 1
                else:
                    type_analysis['problematic_columns'].append(col)

        # Categorize final types
        final_dtypes = typed_data.dtypes.to_dict()
        type_analysis['columns_by_final_type'] = categorize_final_types(final_dtypes)

        # Validate type assignments
        validation_results = validate_type_assignments(typed_data, conversion_log)

        print(f"\n{type_analysis['mapping_informed_decisions']} type decisions were informed by question text")

        return {
            'typed_data': typed_data,
            'type_analysis': type_analysis,
            'conversion_log': conversion_log,
            'validation_results': validation_results,
            'initial_dtypes': initial_dtypes,
            'final_dtypes': final_dtypes,
            'question_mapping': question_mapping,  # NEW: Preserve mapping
            'codebook': codebook  # NEW: Preserve codebook
        }

    def analyze_column_for_type_with_context(series, col_name, question_text):
        """
        Analyze a single column to determine the optimal data type using question context.
        NEW FUNCTION: Enhanced version that uses question text for better type detection.

        Parameters:
        -----------
        series : pandas.Series
            Column data to analyze
        col_name : str
            Name of the column
        question_text : str
            Full question text from mapping

        Returns:
        --------
        dict : Analysis results with recommended type and confidence
        """

        # Get non-null values for analysis
        non_null_data = series.dropna()

        if len(non_null_data) == 0:
            return {
                'recommended_type': 'object',
                'confidence': 'high',
                'reason': 'all_null',
                'sample_values': [],
                'mapping_informed': False
            }

        unique_values = non_null_data.unique()
        sample_values = list(unique_values[:5])

        # Use question text to inform type detection
        question_lower = question_text.lower()

        # Check for date/time indicators in question text
        datetime_keywords = ['date', 'time', 'when', 'year', 'month', 'day', 'timestamp']
        if any(keyword in question_lower for keyword in datetime_keywords):
            datetime_result = detect_datetime_type(non_null_data, col_name)
            if datetime_result['is_datetime']:
                datetime_result['mapping_informed'] = True
                datetime_result['reason'] += '_question_context'
                return {
                    'recommended_type': 'datetime',
                    'confidence': datetime_result['confidence'],
                    'reason': datetime_result['reason'],
                    'sample_values': sample_values,
                    'mapping_informed': True
                }

        # Check for year-specific questions
        year_keywords = ['year', 'founded', 'established', 'est.', 'birth', 'graduation']
        if any(keyword in question_lower for keyword in year_keywords):
            numeric_result = detect_numeric_type(non_null_data, col_name)
            if numeric_result['is_numeric']:
                # Check if values are in reasonable year range
                numeric_series = pd.to_numeric(series, errors='coerce')
                valid_nums = numeric_series.dropna()
                if len(valid_nums) > 0:
                    if valid_nums.min() > 1800 and valid_nums.max() < 2100:
                        return {
                            'recommended_type': 'float64',  # Use float for years with potential NaN
                            'confidence': 'high',
                            'reason': 'year_values_from_question_context',
                            'sample_values': sample_values,
                            'mapping_informed': True,
                            'contamination_rate': numeric_result.get('contamination_rate', 0)
                        }

        # Check for numeric indicators in question text
        numeric_keywords = ['number', 'count', 'amount', 'total', 'quantity', 'how many', 'percentage', '%', 'rate', 'score']
        if any(keyword in question_lower for keyword in numeric_keywords):
            numeric_result = detect_numeric_type(non_null_data, col_name)
            if numeric_result['is_numeric']:
                numeric_result['mapping_informed'] = True
                numeric_result['confidence'] = 'high' if numeric_result['confidence'] == 'medium' else numeric_result['confidence']
                return {
                    'recommended_type': numeric_result['numeric_subtype'],
                    'confidence': numeric_result['confidence'],
                    'reason': numeric_result['reason'] + '_question_context',
                    'sample_values': sample_values,
                    'mapping_informed': True,
                    'contamination_rate': numeric_result.get('contamination_rate', 0)
                }

        # Check for yes/no or binary questions
        binary_keywords = ['yes or no', 'y/n', 'agree', 'disagree', 'true or false', 'do you', 'have you', 'are you', 'is there']
        if any(keyword in question_lower for keyword in binary_keywords):
            boolean_result = detect_boolean_type(non_null_data, col_name)
            if boolean_result['is_boolean']:
                boolean_result['mapping_informed'] = True
                return {
                    'recommended_type': 'category',
                    'confidence': 'high',
                    'reason': boolean_result['reason'] + '_question_context',
                    'sample_values': sample_values,
                    'mapping_informed': True
                }

        # Check for scale/rating questions
        scale_keywords = ['scale', 'rating', 'satisfaction', 'likelihood', 'extent', 'strongly', 'somewhat']
        if any(keyword in question_lower for keyword in scale_keywords):
            # These are often categorical even if numeric
            categorical_result = detect_categorical_type(non_null_data, col_name)
            if categorical_result['is_categorical']:
                categorical_result['mapping_informed'] = True
                return {
                    'recommended_type': 'category',
                    'confidence': categorical_result['confidence'],
                    'reason': categorical_result['reason'] + '_scale_question',
                    'sample_values': sample_values,
                    'mapping_informed': True
                }

        # Fall back to standard detection without context
        return analyze_column_for_type_standard(series, col_name, non_null_data, unique_values, sample_values)

    def analyze_column_for_type_standard(series, col_name, non_null_data, unique_values, sample_values):
        """
        Standard type analysis without question context.
        (Extracted from original analyze_column_for_type function)
        """

        # Date/Time Detection
        datetime_result = detect_datetime_type(non_null_data, col_name)
        if datetime_result['is_datetime']:
            return {
                'recommended_type': 'datetime',
                'confidence': datetime_result['confidence'],
                'reason': datetime_result['reason'],
                'sample_values': sample_values,
                'mapping_informed': False
            }

        # Numeric Detection
        numeric_result = detect_numeric_type(non_null_data, col_name)
        if numeric_result['is_numeric']:
            return {
                'recommended_type': numeric_result['numeric_subtype'],
                'confidence': numeric_result['confidence'],
                'reason': numeric_result['reason'],
                'sample_values': sample_values,
                'contamination_rate': numeric_result.get('contamination_rate', 0),
                'mapping_informed': False
            }

        # Boolean/Binary Detection
        boolean_result = detect_boolean_type(non_null_data, col_name)
        if boolean_result['is_boolean']:
            return {
                'recommended_type': 'category',
                'confidence': boolean_result['confidence'],
                'reason': boolean_result['reason'],
                'sample_values': sample_values,
                'mapping_informed': False
            }

        # Categorical Detection
        categorical_result = detect_categorical_type(non_null_data, col_name)
        if categorical_result['is_categorical']:
            return {
                'recommended_type': 'category',
                'confidence': categorical_result['confidence'],
                'reason': categorical_result['reason'],
                'sample_values': sample_values,
                'mapping_informed': False
            }

        # Default to object (text)
        return {
            'recommended_type': 'object',
            'confidence': 'high',
            'reason': 'free_text_or_complex',
            'sample_values': sample_values,
            'mapping_informed': False
        }

    def get_columns_to_skip(df):
        """
        Identify columns that should not undergo type conversion.
        (Unchanged from original)
        """

        skip_patterns = [
            r'^flag_',           # Quality flags
            r'.*id$',            # ID columns
            r'.*address$',       # IP addresses
            r'^responseid$',     # Response IDs
            r'^ipaddress$'       # IP addresses
        ]

        skip_columns = []
        for col in df.columns:
            for pattern in skip_patterns:
                if re.match(pattern, col, re.IGNORECASE):
                    skip_columns.append(col)
                    break

        return skip_columns

    def detect_datetime_type(series, col_name):
        """
        Detect if column contains date/time data.
        (Unchanged from original)
        """

        # Check column name patterns first
        datetime_name_patterns = [r'date', r'time', r'timestamp']
        name_suggests_datetime = any(re.search(pattern, col_name, re.IGNORECASE)
                                    for pattern in datetime_name_patterns)

        if not name_suggests_datetime:
            return {'is_datetime': False, 'confidence': 'low', 'reason': 'name_pattern_mismatch'}

        # Try to parse as datetime
        try:
            parsed = pd.to_datetime(series, errors='coerce')
            success_rate = parsed.notna().sum() / len(series)

            if success_rate >= 0.8:
                return {
                    'is_datetime': True,
                    'confidence': 'high' if success_rate >= 0.95 else 'medium',
                    'reason': f'{success_rate:.0%}_successful_datetime_parsing'
                }
        except:
            pass

        return {'is_datetime': False, 'confidence': 'low', 'reason': 'datetime_parsing_failed'}

    def detect_numeric_type(series, col_name):
        """
        Detect if column contains numeric data, handling contamination.
        (Unchanged from original)
        """

        # Attempt numeric conversion
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            numeric_count = numeric_series.notna().sum()
            total_count = series.notna().sum()

            if total_count == 0:
                return {'is_numeric': False, 'confidence': 'high', 'reason': 'no_data'}

            success_rate = numeric_count / total_count
            contamination_rate = 1 - success_rate

            # High success rate - clearly numeric
            if success_rate >= 0.9:
                # Determine if integer or float
                if numeric_series.dropna().apply(lambda x: x == int(x)).all():
                    subtype = 'int64'
                else:
                    subtype = 'float64'

                return {
                    'is_numeric': True,
                    'numeric_subtype': subtype,
                    'confidence': 'high',
                    'reason': f'{success_rate:.0%}_numeric_with_{contamination_rate:.0%}_contamination',
                    'contamination_rate': contamination_rate
                }

            # Medium success rate - might be numeric with contamination
            elif success_rate >= 0.7:
                return {
                    'is_numeric': True,
                    'numeric_subtype': 'float64',  # Use float to handle mixed cases
                    'confidence': 'medium',
                    'reason': f'{success_rate:.0%}_numeric_contaminated',
                    'contamination_rate': contamination_rate
                }

            # Low success rate - not primarily numeric
            else:
                return {
                    'is_numeric': False,
                    'confidence': 'high',
                    'reason': f'only_{success_rate:.0%}_numeric'
                }

        except Exception as e:
            return {
                'is_numeric': False,
                'confidence': 'high',
                'reason': f'numeric_conversion_error: {str(e)}'
            }

    def detect_boolean_type(series, col_name):
        """
        Detect binary/boolean columns (Yes/No, True/False, etc.).
        (Unchanged from original)
        """

        unique_values = set(str(val).lower().strip() for val in series.unique())

        # Common boolean patterns
        boolean_patterns = [
            {'yes', 'no'},
            {'true', 'false'},
            {'1', '0'},
            {'y', 'n'},
            {'on', 'off'},
            {'enabled', 'disabled'}
        ]

        for pattern in boolean_patterns:
            if unique_values.issubset(pattern) and len(unique_values) >= 2:
                return {
                    'is_boolean': True,
                    'confidence': 'high',
                    'reason': f'binary_values_{list(unique_values)}'
                }

        # Single value that could be boolean (all Yes, all No, etc.)
        if len(unique_values) == 1 and list(unique_values)[0] in ['yes', 'no', 'true', 'false', '1', '0']:
            return {
                'is_boolean': True,
                'confidence': 'medium',
                'reason': f'single_boolean_value_{list(unique_values)[0]}'
            }

        return {'is_boolean': False, 'confidence': 'high', 'reason': 'not_binary_pattern'}

    def detect_categorical_type(series, col_name):
        """
        Detect categorical columns based on repetition patterns.
        (Unchanged from original)
        """

        unique_count = len(series.unique())
        total_count = len(series)

        if total_count == 0:
            return {'is_categorical': False, 'confidence': 'high', 'reason': 'no_data'}

        # Calculate repetition ratio
        repetition_ratio = total_count / unique_count if unique_count > 0 else 0

        # Categorical if:
        # 1. Few unique values with high repetition
        # 2. Reasonable number of categories (not too many, not too few)

        if unique_count <= 2:
            # Very few categories - likely categorical
            return {
                'is_categorical': True,
                'confidence': 'high',
                'reason': f'{unique_count}_unique_values_high_repetition'
            }
        elif unique_count <= 10 and repetition_ratio >= 2:
            # Moderate categories with good repetition
            return {
                'is_categorical': True,
                'confidence': 'high' if repetition_ratio >= 5 else 'medium',
                'reason': f'{unique_count}_categories_repetition_{repetition_ratio:.1f}x'
            }
        elif unique_count <= 20 and repetition_ratio >= 5:
            # More categories but very high repetition
            return {
                'is_categorical': True,
                'confidence': 'medium',
                'reason': f'{unique_count}_categories_high_repetition_{repetition_ratio:.1f}x'
            }

        return {
            'is_categorical': False,
            'confidence': 'high',
            'reason': f'too_many_unique_values_{unique_count}_or_low_repetition_{repetition_ratio:.1f}x'
        }

    def apply_type_conversion(df, col_name, type_result, conversion_log):
        """
        Apply the recommended type conversion to a column.
        Enhanced with better reporting for mapping-informed decisions.
        """

        recommended_type = type_result['recommended_type']
        mapping_note = " (informed by question text)" if type_result.get('mapping_informed') else ""

        try:
            if recommended_type == 'datetime':
                df[col_name] = pd.to_datetime(df[col_name], errors='coerce')
                conversion_log.append(f"{col_name}: Converted to datetime - {type_result['reason']}{mapping_note}")
                print(f"  [SUCCESS] Converted to datetime{mapping_note}")
                return True

            elif recommended_type in ['int64', 'float64']:
                original_nulls = df[col_name].isnull().sum()
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                new_nulls = df[col_name].isnull().sum()
                contamination_nulls = new_nulls - original_nulls

                if recommended_type == 'int64':
                    # Only convert to int if no fractional parts
                    if df[col_name].dropna().apply(lambda x: x == int(x) if pd.notna(x) else True).all():
                        df[col_name] = df[col_name].astype('Int64')  # Nullable integer
                    else:
                        recommended_type = 'float64'  # Fall back to float

                conversion_log.append(f"{col_name}: Converted to {recommended_type} - {type_result['reason']} - {contamination_nulls} values became null{mapping_note}")
                print(f"  [SUCCESS] Converted to {recommended_type} ({contamination_nulls} contaminated values -> null){mapping_note}")
                return True

            elif recommended_type == 'category':
                df[col_name] = df[col_name].astype('category')
                conversion_log.append(f"{col_name}: Converted to category - {type_result['reason']}{mapping_note}")
                print(f"  [SUCCESS] Converted to category{mapping_note}")
                return True

            else:
                conversion_log.append(f"{col_name}: Kept as object - {type_result['reason']}{mapping_note}")
                print(f"  -> Kept as object ({type_result['reason']}){mapping_note}")
                return True

        except Exception as e:
            conversion_log.append(f"{col_name}: Conversion to {recommended_type} FAILED - {str(e)}")
            print(f"  [ERROR] Conversion to {recommended_type} failed: {str(e)}")
            return False

    def categorize_final_types(dtypes_dict):
        """
        Categorize the final data types for summary reporting.
        (Unchanged from original)
        """

        type_categories = {
            'datetime': [],
            'numeric': [],
            'categorical': [],
            'text': [],
            'administrative': []
        }

        for col, dtype in dtypes_dict.items():
            dtype_str = str(dtype)

            if col.startswith('flag_') or 'id' in col.lower():
                type_categories['administrative'].append(col)
            elif 'datetime' in dtype_str:
                type_categories['datetime'].append(col)
            elif dtype_str in ['int64', 'Int64', 'float64', 'Float64']:
                type_categories['numeric'].append(col)
            elif dtype_str == 'category':
                type_categories['categorical'].append(col)
            else:
                type_categories['text'].append(col)

        return type_categories

    def validate_type_assignments(df, conversion_log):
        """
        Validate that type assignments were successful and reasonable.
        (Unchanged from original)
        """

        validation_results = {
            'datetime_columns': [],
            'numeric_columns': [],
            'categorical_columns': [],
            'potential_issues': []
        }

        for col in df.columns:
            dtype = df[col].dtype

            if pd.api.types.is_datetime64_any_dtype(dtype):
                null_pct = df[col].isnull().sum() / len(df) * 100
                validation_results['datetime_columns'].append({
                    'column': col,
                    'null_percentage': null_pct
                })

                if null_pct > 50:
                    validation_results['potential_issues'].append(f"{col}: High null rate ({null_pct:.1f}%) after datetime conversion")

            elif pd.api.types.is_numeric_dtype(dtype):
                null_pct = df[col].isnull().sum() / len(df) * 100
                validation_results['numeric_columns'].append({
                    'column': col,
                    'null_percentage': null_pct,
                    'min_value': df[col].min(),
                    'max_value': df[col].max()
                })

                if null_pct > 30:
                    validation_results['potential_issues'].append(f"{col}: High contamination ({null_pct:.1f}% null) after numeric conversion")

            elif isinstance(dtype, pd.CategoricalDtype):
                n_categories = len(df[col].cat.categories)
                validation_results['categorical_columns'].append({
                    'column': col,
                    'n_categories': n_categories
                })

                if n_categories > 20:
                    validation_results['potential_issues'].append(f"{col}: Many categories ({n_categories}) - might not be truly categorical")

        return validation_results

    # Example usage
    return (detect_and_assign_data_types,)


@app.cell
def _(cleaning_result, detect_and_assign_data_types, mo):
    typing_result = detect_and_assign_data_types(cleaning_result)

    typed_data = typing_result["typed_data"]
    type_analysis = typing_result["type_analysis"]
    type_validation = typing_result["validation_results"]

    if not mo.running_in_notebook():
        print("\n=== Step 3a Summary ===")
        print("Data type detection completed:")
        print(f"  Columns analyzed: {type_analysis['columns_analyzed']}")
        print(f"  Conversions attempted: {type_analysis['conversions_attempted']}")
        print(f"  Conversions successful: {type_analysis['conversions_successful']}")
        print(f"  Question-informed decisions: {type_analysis['mapping_informed_decisions']}")
        print(f"  Problematic columns: {len(type_analysis['problematic_columns'])}")

        print("\nFinal type distribution:")
        for _category, _columns in type_analysis["columns_by_final_type"].items():
            if _columns:
                print(f"  {_category.title()}: {len(_columns)} columns")

        if type_validation["potential_issues"]:
            print("\nPotential issues detected:")
            for _issue in type_validation["potential_issues"][:5]:
                print(f"  - {_issue}")
            if len(type_validation["potential_issues"]) > 5:
                print(f"  ... and {len(type_validation['potential_issues']) - 5} more issues")

        print(f"\nData shape: {typed_data.shape[0]:,} x {typed_data.shape[1]:,}")

        if typing_result.get("question_mapping"):
            print("\nQuestion Mapping Status:")
            print("  Mapping preserved: Yes")
            print(f"  Mapping quality: {typing_result['question_mapping'].get('mapping_quality', 'unknown')}")

        print("\n[SUCCESS] Step 3a Complete: data types detected and assigned")

    _type_rows = "\n".join(
        f"    | {category.title()} | {len(columns)} |"
        for category, columns in type_analysis["columns_by_final_type"].items()
        if columns
    )

    mo.md(
        f"""
        ### Step 3a assigned data types

        | Metric | Value |
        | --- | --- |
        | Columns analyzed | {type_analysis['columns_analyzed']} |
        | Conversions attempted | {type_analysis['conversions_attempted']} |
        | Conversions successful | {type_analysis['conversions_successful']} |
        | Question-informed decisions | {type_analysis['mapping_informed_decisions']} |
        | Problematic columns | {len(type_analysis['problematic_columns'])} |
        | Potential issues | {len(type_validation['potential_issues'])} |
        | Shape | {typed_data.shape[0]:,} x {typed_data.shape[1]:,} |

        **Final type distribution**

        | Type | Columns |
        | --- | --- |
    {_type_rows}
        """
    )
    return (typing_result,)


@app.cell
def _(mo, typing_result):
    # Quick diagnostic after Step 3a
    q2_cols_typed = [
        col for col in typing_result["typed_data"].columns if "q2#" in col.lower()
    ]

    q2_in_mapping = [
        k
        for k in typing_result.get("question_mapping", {})
        .get("column_to_question", {})
        .keys()
        if "q2#" in k.lower()
    ]

    if not mo.running_in_notebook():
        print(f"\nQ2 columns after type detection: {len(q2_cols_typed)}")
        for _col in q2_cols_typed[:5]:
            print(f"  {_col}: {typing_result['typed_data'][_col].dtype}")

        print(f"\nQ2 columns still in mapping: {len(q2_in_mapping)}")

    mo.md(
        f"""
        Diagnostic: **{len(q2_cols_typed)}** typed Q2 columns,
        **{len(q2_in_mapping)}** still present in the question mapping.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("### Data Type Validation and Optimization")
    return


@app.cell
def _(np, pd, re):
    # Step 3b: Data Type Validation and Optimization - UNIVERSAL VERSION
    # FIXED: Now truly universal for ANY Qualtrics survey without hardcoding


    def validate_and_optimize_data_types(typing_result):
        """
        Validate type assignments, handle contaminated columns, and optimize the final data structure.
        UNIVERSAL: Works with any Qualtrics survey without hardcoded assumptions.

        Parameters:
        -----------
        typing_result : dict
            Result from Step 3a containing typed_data, question_mapping, and analysis results

        Returns:
        --------
        dict : Contains optimized_data, validation_report, contamination_handling, and preserved mapping
        """

        print("=== Step 3b: Data Type Validation and Optimization ===")

        df = typing_result['typed_data'].copy()
        type_analysis = typing_result['type_analysis']
        validation_results = typing_result['validation_results']
        question_mapping = typing_result.get('question_mapping', {})
        codebook = typing_result.get('codebook', pd.DataFrame())

        # Initialize optimization tracking
        optimization_log = []
        contamination_handling = {}

        # Step 1: Handle highly contaminated numeric columns
        contaminated_columns = handle_contaminated_numerics(df, validation_results, question_mapping,
                                                           optimization_log, contamination_handling)

        # Step 2: Optimize categorical columns
        optimized_categoricals = optimize_categorical_columns(df, validation_results, optimization_log)

        # Step 3: Create summary variables for multi-part questions (dynamically detected)
        summary_variables = create_dynamic_summary_variables(df, question_mapping, optimization_log)

        # Step 4: Create data quality summaries
        quality_summaries = create_quality_summaries(df, optimization_log)

        # Step 5: Final data validation
        final_validation = perform_final_validation(df, optimization_log)

        # Generate comprehensive validation report
        validation_report = generate_validation_report(df, type_analysis, validation_results,
                                                     contamination_handling, optimization_log,
                                                     summary_variables, quality_summaries)

        return {
            'optimized_data': df,
            'validation_report': validation_report,
            'contamination_handling': contamination_handling,
            'optimization_log': optimization_log,
            'final_validation': final_validation,
            'question_mapping': question_mapping,  # Preserve mapping
            'codebook': codebook,  # Preserve codebook
            'summary_variables': summary_variables,
            'quality_summaries': quality_summaries
        }

    def handle_contaminated_numerics(df, validation_results, question_mapping, optimization_log, contamination_handling):
        """
        Handle numeric columns with high contamination rates by creating clean versions.
        UNIVERSAL: Uses question text to identify year columns dynamically.
        """

        print("\n--- Handling Contaminated Numeric Columns ---")

        contaminated_columns = []
        column_to_question = question_mapping.get('column_to_question', {})

        for col_info in validation_results.get('numeric_columns', []):
            col_name = col_info['column']
            null_pct = col_info['null_percentage']

            # If contamination is high (>20% null after conversion), create a cleaned version
            if null_pct > 20:
                contaminated_columns.append(col_name)

                print(f"Processing contaminated column: {col_name} ({null_pct:.1f}% null)")

                # Get question text to understand the column
                question_text = column_to_question.get(col_name, '').lower()

                # Check if this appears to be a year column based on question text
                year_indicators = ['year', 'founded', 'established', 'est.', 'birth', 'graduation', 'started', 'began']
                is_year_column = any(indicator in question_text for indicator in year_indicators)

                clean_col_name = f"{col_name}_clean"
                df[clean_col_name] = df[col_name].copy()

                if is_year_column:
                    # Apply year-specific validation
                    current_year = pd.Timestamp.now().year

                    # Determine reasonable range based on context
                    if any(word in question_text for word in ['birth', 'born', 'age']):
                        min_reasonable_year = current_year - 120  # Human age context
                        max_reasonable_year = current_year
                    elif any(word in question_text for word in ['founded', 'established', 'started']):
                        min_reasonable_year = 1800  # Organization context
                        max_reasonable_year = current_year
                    else:
                        min_reasonable_year = 1900  # Generic year context
                        max_reasonable_year = current_year + 5

                    # Apply range validation
                    out_of_range_mask = (df[clean_col_name] < min_reasonable_year) | (df[clean_col_name] > max_reasonable_year)
                    out_of_range_count = out_of_range_mask.sum()

                    if out_of_range_count > 0:
                        print(f"  Removing {out_of_range_count} out-of-range years (not between {min_reasonable_year}-{max_reasonable_year})")
                        df.loc[out_of_range_mask, clean_col_name] = np.nan

                    # Calculate age/duration if it's a founding year
                    if any(word in question_text for word in ['founded', 'established', 'started', 'began']):
                        age_col_name = f"{col_name}_age_years"
                        df[age_col_name] = np.where(
                            df[clean_col_name].notna(),
                            current_year - df[clean_col_name],
                            np.nan
                        )

                        # Create age categories
                        age_category_col = f"{col_name}_age_category"
                        df[age_category_col] = pd.cut(
                            df[age_col_name],
                            bins=[0, 5, 10, 20, 50, 200],
                            labels=['<5 years', '5-10 years', '10-20 years', '20-50 years', '50+ years']
                        )

                        contamination_handling[col_name] = {
                            'original_valid': df[col_name].notna().sum(),
                            'cleaned_valid': df[clean_col_name].notna().sum(),
                            'clean_column_created': clean_col_name,
                            'derived_columns': [age_col_name, age_category_col],
                            'cleaning_method': 'year_validation_with_age_calculation'
                        }

                        print(f"  Created age calculations: {age_col_name}, {age_category_col}")
                    else:
                        contamination_handling[col_name] = {
                            'original_valid': df[col_name].notna().sum(),
                            'cleaned_valid': df[clean_col_name].notna().sum(),
                            'clean_column_created': clean_col_name,
                            'cleaning_method': 'year_range_validation'
                        }

                    optimization_log.append(f"Cleaned year column {col_name} based on question context")

                else:
                    # Generic numeric cleaning for non-year columns
                    contamination_handling[col_name] = {
                        'original_valid': df[col_name].notna().sum(),
                        'cleaned_valid': df[col_name].notna().sum(),
                        'clean_column_created': clean_col_name,
                        'cleaning_method': 'preserved_as_is'
                    }

                    optimization_log.append(f"Preserved contaminated numeric column {col_name} as {clean_col_name}")

        if not contaminated_columns:
            print("No highly contaminated numeric columns found")

        return contaminated_columns

    def create_dynamic_summary_variables(df, question_mapping, optimization_log):
        """
        Dynamically create summary variables for multi-part questions.
        UNIVERSAL: Detects question series patterns without hardcoding.
        """

        print("\n--- Creating Summary Variables for Question Series ---")

        summary_variables = {}

        # Detect question series by analyzing column name patterns
        question_series = detect_question_series(df.columns)

        for series_base, related_cols in question_series.items():
            if len(related_cols) < 3:  # Skip if too few related columns
                continue

            print(f"\nProcessing question series: {series_base} ({len(related_cols)} columns)")

            # Group columns by subseries pattern
            subseries = detect_subseries(related_cols)

            # Create count variables for each subseries
            for subseries_name, cols in subseries.items():
                if cols:
                    count_col = f"{series_base}_{subseries_name}_count"
                    df[count_col] = df[cols].notna().sum(axis=1)

                    # Calculate completion rate
                    rate_col = f"{series_base}_{subseries_name}_completion_rate"
                    df[rate_col] = (df[count_col] / len(cols) * 100).round(1)

                    print(f"  Created {count_col}: Average {df[count_col].mean():.1f} responses")

            # Create overall series completion
            all_series_cols = [col for cols in subseries.values() for col in cols]
            if all_series_cols:
                overall_count = f"{series_base}_total_responses"
                df[overall_count] = df[all_series_cols].notna().sum(axis=1)

                overall_rate = f"{series_base}_overall_completion"
                df[overall_rate] = (df[overall_count] / len(all_series_cols) * 100).round(1)

                summary_variables[series_base] = {
                    'related_columns': all_series_cols,
                    'subseries': subseries,
                    'summary_columns': [col for col in df.columns if col.startswith(f"{series_base}_") and
                                       any(suffix in col for suffix in ['_count', '_completion', '_responses'])]
                }

                optimization_log.append(f"Created summary variables for {series_base} series ({len(all_series_cols)} columns)")

        if not summary_variables:
            print("No multi-part question series detected")

        return summary_variables

    def detect_question_series(columns):
        """
        Detect question series based on column naming patterns.
        FIXED: Handles the # character in matrix questions like q2#1_1_1
        """

        series_patterns = {}

        for col in columns:
            # Skip flag columns and derived columns
            if col.startswith('flag_') or any(suffix in col for suffix in ['_clean', '_binary', '_age', '_category']):
                continue

            # FIXED: Look for patterns like q2#1_1, q2_1_1, etc.
            # Handle both regular questions (q1, q2) and matrix questions (q2#)
            if '#' in col:
                # Matrix question pattern (e.g., q2#1_1_1)
                match = re.match(r'^(q\d+)#', col, re.IGNORECASE)
                if match:
                    base = match.group(1)  # This gets 'q2' from 'q2#1_1_1'
            else:
                # Regular question pattern (e.g., q1_1_text)
                match = re.match(r'^(q\d+)', col, re.IGNORECASE)
                if match:
                    base = match.group(1)

            if match:
                if base not in series_patterns:
                    series_patterns[base] = []
                series_patterns[base].append(col)

        # Filter to only keep series with multiple related columns
        return {k: v for k, v in series_patterns.items() if len(v) > 1}

    def detect_subseries(columns):
        """
        Group columns into subseries based on their naming patterns.
        FIXED: Handles matrix questions with # character
        """

        subseries = {}

        for col in columns:
            # Handle matrix questions differently
            if '#' in col:
                # For q2#1_2_1, the subseries is the part after #
                parts = col.split('#')[1].split('_')
                if len(parts) >= 1:
                    subseries_key = f"matrix_row_{parts[0]}"
            else:
                # Regular question handling
                parts = col.split('_')
                if len(parts) >= 2:
                    if len(parts) > 2 and parts[1].isdigit():
                        subseries_key = f"part_{parts[1]}"
                    else:
                        subseries_key = "main"
                else:
                    subseries_key = "main"

            if subseries_key not in subseries:
                subseries[subseries_key] = []
            subseries[subseries_key].append(col)

        return subseries

    def create_quality_summaries(df, optimization_log):
        """
        Create data quality summary variables.
        UNIVERSAL: Works with any flag columns created in Step 2b.
        """

        print("\n--- Creating Data Quality Summaries ---")

        quality_summaries = {}

        # Work with any flag columns that exist
        flag_cols = [col for col in df.columns if col.startswith('flag_')]

        if flag_cols:
            # Count total quality issues per response
            df['quality_issue_count'] = df[flag_cols].sum(axis=1)

            # Calculate quality score (inverse of issues)
            df['quality_score'] = 100 - (df['quality_issue_count'] / len(flag_cols) * 100)

            # Categorize quality level
            df['quality_level'] = pd.cut(
                df['quality_score'],
                bins=[0, 50, 75, 100],
                labels=['Poor', 'Fair', 'Good']
            )

            quality_summaries = {
                'flag_columns': flag_cols,
                'issue_count_column': 'quality_issue_count',
                'quality_score_column': 'quality_score',
                'quality_level_column': 'quality_level'
            }

            print(f"Created quality summaries from {len(flag_cols)} flag columns")
            print(f"  Average quality score: {df['quality_score'].mean():.1f}%")
            quality_dist = df['quality_level'].value_counts()
            for level, count in quality_dist.items():
                print(f"  {level} quality: {count} responses ({count/len(df)*100:.1f}%)")

            optimization_log.append(f"Created quality summaries from {len(flag_cols)} quality flags")
        else:
            print("No quality flag columns found")

        # Detect and summarize yes/no questions dynamically
        yes_no_summaries = create_yes_no_summaries(df, optimization_log)
        if yes_no_summaries:
            quality_summaries['yes_no_analysis'] = yes_no_summaries

        return quality_summaries

    def create_yes_no_summaries(df, optimization_log):
        """
        Create summaries for yes/no categorical columns.
        UNIVERSAL: Automatically detects yes/no questions without hardcoding.
        """

        yes_no_cols = []

        # Find categorical columns that appear to be yes/no questions
        for col in df.columns:
            if str(df[col].dtype) == 'category':
                categories = df[col].cat.categories.tolist()
                # Check if categories look like yes/no
                categories_lower = [str(cat).lower() for cat in categories]
                if any(yes_variant in categories_lower for yes_variant in ['yes', 'y', 'true', '1']) and \
                   any(no_variant in categories_lower for no_variant in ['no', 'n', 'false', '0']):
                    yes_no_cols.append(col)

                    # Create binary version
                    binary_col = f"{col}_binary"
                    df[binary_col] = df[col].astype(str).str.lower().str.contains('yes|y|true|1', na=False).astype(int)

        if yes_no_cols:
            # Create overall yes/no summary
            binary_cols = [f"{col}_binary" for col in yes_no_cols]
            df['yes_response_count'] = df[binary_cols].sum(axis=1)
            df['yes_response_rate'] = (df['yes_response_count'] / len(binary_cols) * 100).round(1)

            print(f"\nDetected {len(yes_no_cols)} yes/no questions")
            print(f"  Average 'Yes' responses: {df['yes_response_count'].mean():.1f}/{len(yes_no_cols)}")

            optimization_log.append(f"Created binary indicators for {len(yes_no_cols)} yes/no questions")

            return {
                'yes_no_columns': yes_no_cols,
                'binary_columns': binary_cols,
                'summary_columns': ['yes_response_count', 'yes_response_rate']
            }

        return None

    def optimize_categorical_columns(df, validation_results, optimization_log):
        """
        Optimize categorical columns by handling issues like too many categories.
        (Unchanged from original - already generic)
        """

        print("\n--- Optimizing Categorical Columns ---")

        optimized_categoricals = {}

        for col_info in validation_results.get('categorical_columns', []):
            col_name = col_info['column']
            n_categories = col_info['n_categories']

            if n_categories > 20:
                print(f"Column {col_name} has {n_categories} categories - flagged for review")

                optimized_categoricals[col_name] = {
                    'original_categories': n_categories,
                    'action': 'flagged_for_review',
                    'recommendation': 'Consider if this should be categorical or text'
                }

                optimization_log.append(f"{col_name}: Flagged - {n_categories} categories may be too many")

            elif n_categories == 1:
                print(f"Column {col_name} has only 1 category - converting to constant")

                unique_val = df[col_name].cat.categories[0]
                df[f"{col_name}_constant"] = unique_val

                optimized_categoricals[col_name] = {
                    'original_categories': 1,
                    'action': 'converted_to_constant',
                    'constant_value': unique_val
                }

                optimization_log.append(f"{col_name}: Converted to constant value '{unique_val}'")

        if not optimized_categoricals:
            print("All categorical columns are appropriately sized")

        return optimized_categoricals

    def perform_final_validation(df, optimization_log):
        """
        Perform final validation checks on the optimized data.
        UNIVERSAL: Generic validation without survey-specific assumptions.
        """

        print("\n--- Performing Final Validation ---")

        final_validation = {
            'total_columns': len(df.columns),
            'total_rows': len(df),
            'data_types': df.dtypes.value_counts().to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'null_percentages': {},
            'validation_warnings': [],
            'summary_columns_created': len([col for col in df.columns if any(suffix in col for suffix in
                                           ['_count', '_rate', '_score', '_level', '_category', '_binary', '_clean',
                                            '_completion', '_responses', '_age', '_years'])])
        }

        # Calculate null percentages for columns with high missing data
        for col in df.columns:
            null_pct = df[col].isnull().sum() / len(df) * 100
            if null_pct > 50:
                final_validation['null_percentages'][col] = null_pct

        # Generic validation warnings
        if len(final_validation['null_percentages']) > 10:
            final_validation['validation_warnings'].append(
                f"Many columns ({len(final_validation['null_percentages'])}) have >50% missing data"
            )

        if final_validation['memory_usage_mb'] > 100:
            final_validation['validation_warnings'].append(
                f"High memory usage: {final_validation['memory_usage_mb']:.1f} MB"
            )

        print(f"Final validation complete:")
        print(f"  Data shape: {df.shape[0]:,} x {df.shape[1]:,}")
        print(f"  Memory usage: {final_validation['memory_usage_mb']:.1f} MB")
        print(f"  Summary columns created: {final_validation['summary_columns_created']}")

        if final_validation['validation_warnings']:
            print(f"  Warnings: {len(final_validation['validation_warnings'])}")
            for warning in final_validation['validation_warnings']:
                print(f"    - {warning}")

        optimization_log.append(
            f"Final validation: {df.shape[0]} rows x {df.shape[1]} columns, "
            f"{final_validation['memory_usage_mb']:.1f} MB, "
            f"{final_validation['summary_columns_created']} summary columns"
        )

        return final_validation

    def generate_validation_report(df, type_analysis, validation_results, contamination_handling,
                                  optimization_log, summary_variables, quality_summaries):
        """
        Generate comprehensive validation report.
        UNIVERSAL: Generic report structure for any survey.
        """

        report = {
            'data_overview': {
                'shape': df.shape,
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                'original_columns': type_analysis['columns_analyzed'],
                'final_columns': len(df.columns)
            },
            'type_distribution': type_analysis['columns_by_final_type'],
            'contamination_summary': contamination_handling,
            'validation_issues': validation_results.get('potential_issues', []),
            'optimization_steps': len(optimization_log),
            'summary_variables': summary_variables,
            'quality_summaries': quality_summaries,
            'ready_for_analysis': len(validation_results.get('potential_issues', [])) < 5
        }

        return report

    # Example usage
    return (validate_and_optimize_data_types,)


@app.cell
def _(mo, typing_result, validate_and_optimize_data_types):
    optimization_result = validate_and_optimize_data_types(typing_result)

    optimized_data = optimization_result["optimized_data"]
    validation_report = optimization_result["validation_report"]
    contamination_handling = optimization_result["contamination_handling"]

    if not mo.running_in_notebook():
        print("\n=== Step 3b Summary ===")
        print("Data type validation and optimization completed:")
        print(f"  Final data shape: {optimized_data.shape[0]:,} x {optimized_data.shape[1]:,}")
        print(f"  Memory usage: {validation_report['data_overview']['memory_usage_mb']:.1f} MB")
        print(f"  Contaminated columns handled: {len(contamination_handling)}")
        print(f"  Optimization steps performed: {validation_report['optimization_steps']}")

        if contamination_handling:
            print("\nContamination handling results:")
            for _col, _info in contamination_handling.items():
                print(f"  {_col}:")
                print(f"    Original valid: {_info['original_valid']} values")
                print(f"    Method: {_info['cleaning_method']}")
                if "derived_columns" in _info:
                    print(f"    Created: {', '.join(_info['derived_columns'])}")

        if validation_report.get("summary_variables"):
            print("\nSummary variables created for question series:")
            for _series, _info in validation_report["summary_variables"].items():
                print(f"  {_series}: {len(_info.get('summary_columns', []))} summary columns")

        print(f"\nReady for analysis: {'Yes' if validation_report['ready_for_analysis'] else 'No'}")

        if optimization_result.get("question_mapping"):
            print("\nQuestion Mapping Status:")
            print("  Preserved through optimization: Yes")
            print(f"  Mapping quality: {optimization_result['question_mapping'].get('mapping_quality', 'unknown')}")

        print("\n[SUCCESS] Step 3b Complete: data validated and optimized for analysis")

    mo.md(
        f"""
        ### Step 3b optimized the dataset

        | Metric | Value |
        | --- | --- |
        | Final shape | {optimized_data.shape[0]:,} x {optimized_data.shape[1]:,} |
        | Memory usage | {validation_report['data_overview']['memory_usage_mb']:.1f} MB |
        | Contaminated columns handled | {len(contamination_handling)} |
        | Optimization steps | {validation_report['optimization_steps']} |
        | Summary variable groups | {len(validation_report.get('summary_variables', {}))} |
        | Ready for analysis | `{validation_report['ready_for_analysis']}` |
        """
    )
    return (optimization_result,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Step 4: Output Generation")
    return


@app.cell
def _(Path, datetime, filedialog, json, np, os, pd, re, tk):
    # Step 4: Generate Final Datasets and Documentation - ENHANCED VERSION
    # INCLUDES: JSON output for sentiment analysis and GUI folder selection


    def get_top_values_summary(series):
        """
        IMPROVED HELPER FUNCTION: More robustly summarizes a series by checking for
        comma-separated values FIRST, before checking the data type.
        """
        if series.notna().sum() == 0:
            return "No responses"

        clean_series = series.dropna().astype(str)

        if clean_series.str.contains(',').sum() > len(clean_series) * 0.05:
            top_vals = clean_series.str.split(',').explode().str.strip().value_counts().head(3)
            summary_str = ", ".join([f"'{k}' ({v})" for k, v in top_vals.items()])
            return f"[Multi-Select] {summary_str}"

        if str(series.dtype) == 'category':
            top_vals = series.value_counts().head(3)
            return ", ".join([f"'{k}' ({v})" for k,v in top_vals.items()])

        if str(series.dtype) == 'object':
            unique_count = clean_series.nunique()
            return f"[{unique_count} unique text entries]"

        return f"[{str(series.dtype)} data]"

    def create_json_for_sentiment_analysis(df, question_mapping, generated_files, export_summary, output_dir):
        """
        ENHANCED VERSION: Creates a JSON file optimized for sentiment analysis.
        Includes concatenated text, question categorization, and flattened structure option.
        """
        print("\n--- Creating JSON for Sentiment Analysis ---")

        column_to_question = question_mapping.get('column_to_question', {})

        # Structure for sentiment analysis
        sentiment_data = {
            'metadata': {
                'total_responses': len(df),
                'export_timestamp': datetime.now().isoformat(),
                'survey_completion_rate': float(df['progress'].mean()) if 'progress' in df.columns else None
            },
            'questions': {},
            'responses': [],
            'flattened_responses': []  # NEW: For tools that prefer row-based data
        }

        # Build enhanced questions dictionary with categorization
        for col in df.columns:
            if col.startswith('q') and not any(suffix in col for suffix in ['_clean', '_binary', '_count', '_rate', '_age', '_category', '_score', '_level', '_completion', '_responses']):
                question_text = column_to_question.get(col, col)

                # Determine question category
                if df[col].dtype == 'object':
                    # Check if it's likely multiple choice based on unique values
                    unique_ratio = df[col].nunique() / df[col].notna().sum() if df[col].notna().sum() > 0 else 1
                    if unique_ratio < 0.3:  # Less than 30% unique responses suggests multiple choice
                        question_category = 'multiple_choice'
                    else:
                        question_category = 'open_text'
                elif str(df[col].dtype) == 'category':
                    # Check for yes/no
                    categories = df[col].cat.categories.tolist()
                    if len(categories) <= 2 and any('yes' in str(cat).lower() or 'no' in str(cat).lower() for cat in categories):
                        question_category = 'binary_yes_no'
                    else:
                        question_category = 'categorical'
                else:
                    question_category = 'numeric'

                sentiment_data['questions'][col] = {
                    'question_id': col,
                    'question_text': question_text,
                    'response_type': 'text' if df[col].dtype == 'object' else 'categorical',
                    'question_category': question_category,  # NEW: More detailed categorization
                    'response_count': int(df[col].notna().sum()),
                    'unique_responses': int(df[col].nunique()) if df[col].dtype == 'object' else None,
                    'is_matrix_question': '#' in col  # NEW: Flag for matrix questions
                }

        # Build enhanced responses array
        for idx, row in df.iterrows():
            # Collect all text responses for concatenation
            text_responses = []
            open_text_responses = []

            response_entry = {
                'response_id': row.get('responseid', idx),
                'completion_percentage': float(row.get('progress', 0)),
                'duration_seconds': float(row.get('duration_in_seconds', 0)) if pd.notna(row.get('duration_in_seconds')) else None,
                'quality_score': float(row.get('quality_score', 0)) if 'quality_score' in row.index else None,
                'quality_level': row.get('quality_level', None) if 'quality_level' in row.index else None,
                'answers': {},
                'text_responses_concatenated': '',  # NEW: All text responses combined
                'open_text_concatenated': ''  # NEW: Only open-ended text responses
            }

            # Add all question responses
            for col in sentiment_data['questions'].keys():
                if pd.notna(row[col]):
                    answer_text = str(row[col])
                    response_entry['answers'][col] = answer_text

                    # Collect text for concatenation
                    if sentiment_data['questions'][col]['question_category'] in ['open_text', 'multiple_choice']:
                        text_responses.append(answer_text)
                        if sentiment_data['questions'][col]['question_category'] == 'open_text':
                            open_text_responses.append(answer_text)

            # Create concatenated fields
            response_entry['text_responses_concatenated'] = ' | '.join(text_responses)
            response_entry['open_text_concatenated'] = ' | '.join(open_text_responses)

            sentiment_data['responses'].append(response_entry)

            # NEW: Create flattened structure for each response-question pair
            for col, answer in response_entry['answers'].items():
                if col in sentiment_data['questions']:
                    flattened_entry = {
                        'response_id': response_entry['response_id'],
                        'question_id': col,
                        'question_text': sentiment_data['questions'][col]['question_text'],
                        'question_category': sentiment_data['questions'][col]['question_category'],
                        'answer': answer,
                        'completion_percentage': response_entry['completion_percentage'],
                        'quality_score': response_entry['quality_score'],
                        'quality_level': response_entry['quality_level']
                    }
                    sentiment_data['flattened_responses'].append(flattened_entry)

        # Add summary statistics
        sentiment_data['metadata']['question_categories'] = {}
        for category in ['open_text', 'multiple_choice', 'categorical', 'binary_yes_no', 'numeric']:
            count = sum(1 for q in sentiment_data['questions'].values() if q['question_category'] == category)
            sentiment_data['metadata']['question_categories'][category] = count

        # Save JSON file
        filepath = output_dir / 'sentiment_analysis_data.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sentiment_data, f, indent=2, ensure_ascii=False)

        # Also save flattened CSV for tools that prefer tabular data
        if sentiment_data['flattened_responses']:
            flattened_df = pd.DataFrame(sentiment_data['flattened_responses'])
            csv_filepath = output_dir / 'sentiment_analysis_flattened.csv'
            flattened_df.to_csv(csv_filepath, index=False)
            print(f"Created {csv_filepath.name}: Flattened CSV for row-based analysis tools")

        generated_files['sentiment_json'] = str(filepath)
        export_summary['files_created'].append(str(filepath))

        print(f"Created {filepath.name}: Enhanced JSON for sentiment analysis")
        print(f"  - {len(sentiment_data['questions'])} questions included")
        print(f"  - {len(sentiment_data['responses'])} responses included")
        print(f"  - {len(sentiment_data['flattened_responses'])} flattened response-question pairs")
        print(f"  - Question categories: {sentiment_data['metadata']['question_categories']}")

    def create_html_summary_report(optimization_result, structure_result, export_summary, generated_files, output_dir):
        """
        ENHANCED: Creates a comprehensive HTML report with proper handling of matrix questions (q2#).
        """
        print("\n--- Creating Comprehensive HTML Summary Report ---")

        validation_report = optimization_result['validation_report']
        df = optimization_result['optimized_data']
        question_mapping = optimization_result.get('question_mapping', {})

        html_style = """
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; color: #333; background-color: #f9f9f9;}
            h1, h2, h3 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 40px;}
            h1 { font-size: 2.5em; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; box-shadow: 0 2px 3px rgba(0,0,0,0.1); }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #3498db; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .summary-box { background-color: #ffffff; border: 1px solid #ddd; border-left: 5px solid #3498db; padding: 20px; margin: 20px 0; box-shadow: 0 2px 3px rgba(0,0,0,0.1); }
            .summary-box p { margin: 5px 0; font-size: 1.1em;}
            .warning { color: #e74c3c; font-weight: bold; }
            .bar { background-color: #3498db; height: 20px; display: inline-block; color: white; font-size: 12px; text-align: right; padding-right: 5px; box-sizing: border-box; border-radius: 3px;}
            details { border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px; background-color: #fff;}
            summary { cursor: pointer; padding: 12px; background-color: #ecf0f1; font-weight: bold; }
            details > div { padding: 15px; }
            code { background-color: #ecf0f1; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
            .q-label { font-size: 0.8em; color: #7f8c8d; margin-left: 5px; }
            .matrix-question { background-color: #e8f4f8; border-left: 3px solid #3498db; padding: 10px; margin: 10px 0; }
        </style>
        """

        html_content = f"<html><head><title>Qualtrics Processing Summary</title>{html_style}</head><body>"
        html_content += f"<h1>Qualtrics Processing Summary Report</h1>"
        html_content += f"<p><em>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>"

        html_content += "<div class='summary-box'><h2>Data Overview</h2>"
        html_content += f"<p><strong>Total Genuine Responses:</strong> {export_summary['total_responses']}</p>"
        html_content += f"<p><strong>Original Variables:</strong> {validation_report['data_overview']['original_columns']}</p>"
        html_content += f"<p><strong>Final Variables (with derived):</strong> {export_summary['total_variables']}</p>"
        if 'progress' in df.columns:
            html_content += f"<p><strong>Average Survey Completion Rate:</strong> {pd.to_numeric(df['progress'], errors='coerce').mean():.1f}%</p>"
        html_content += "</div>"

        html_content += "<h2>Data Quality Assessment</h2>"
        if 'quality_level' in df.columns:
            quality_dist = df['quality_level'].value_counts()
            html_content += "<table><tr><th>Quality Level</th><th>Count</th><th>Percentage</th></tr>"
            for level in ['Good', 'Fair', 'Poor']:
                if level in quality_dist.index:
                    count = quality_dist[level]
                    pct = (count / len(df)) * 100
                    html_content += f"<tr><td>{level}</td><td>{count}</td><td>{pct:.1f}%</td></tr>"
            html_content += "</table>"

        if validation_report['validation_issues']:
            html_content += "<h3>Potential Issues Detected:</h3><ul>"
            for issue in validation_report['validation_issues']:
                html_content += f"<li class='warning'>{issue}</li>"
            html_content += "</ul>"

        html_content += "<h2>Detailed Reports</h2>"

        # Processing log section
        trans_summary = optimization_result.get('validation_report', {}).get('summary_variables', {})
        html_content += "<details><summary>► Processing & Transformation Log</summary><div><h4>Summary of Changes</h4><ul>"
        html_content += f"<li>Test/Preview responses removed: {structure_result.get('structure_analysis', {}).get('test_responses', 0)}</li>"
        html_content += f"<li>Quality flag columns created: {len([c for c in df.columns if c.startswith('flag_')])}</li>"
        html_content += f"<li>Contaminated columns handled: {len(optimization_result.get('contamination_handling', {}))}</li>"
        if trans_summary:
            html_content += f"<li>Question series with summaries created: {len(trans_summary)}</li>"
        html_content += "</ul></div></details>"

        # Question Response Summary with proper matrix question handling
        html_content += "<details open><summary>► Question Response Summary</summary><div>"

        question_series = {}
        excluded_suffixes = ['_clean', '_binary', '_count', '_rate', '_age', '_category',
                             '_score', '_level', '_responses', '_completion', '_years',
                             '_constant', '_issue']

        for col in df.columns:
            if col.startswith('q') and not any(suffix in col for suffix in excluded_suffixes):
                # Handle matrix questions (with #) separately
                if '#' in col:
                    match = re.match(r'^(q\d+)#', col, re.IGNORECASE)
                    if match:
                        base = match.group(1)
                else:
                    match = re.match(r'^(q\d+)', col, re.IGNORECASE)
                    if match:
                        base = match.group(1)

                if match:
                    if base not in question_series:
                        question_series[base] = []
                    question_series[base].append(col)

        # Sort questions numerically
        sorted_question_series = sorted(question_series.items(), key=lambda item: int(item[0][1:]))

        column_to_question = question_mapping.get('column_to_question', {})

        for base_q, related_cols in sorted_question_series:
            # Check if this is a matrix question
            is_matrix = any('#' in col for col in related_cols)

            # Get main question text
            main_question = column_to_question.get(base_q, '')
            if not main_question and related_cols:
                main_question = column_to_question.get(related_cols[0], base_q)

            if is_matrix:
                html_content += f"<div class='matrix-question'>"
                html_content += f"<h3>{base_q.upper()}: {main_question} [Matrix Question]</h3>"
            else:
                html_content += f"<h3>{base_q.upper()}: {main_question}</h3>"

            html_content += "<table><tr><th>Sub-Question/Variable</th><th>Response Rate</th><th>Top Values Summary</th></tr>"

            # Sort columns for better display
            sorted_cols = sorted(related_cols)

            for col in sorted_cols:
                rate = (df[col].notna().sum() / len(df)) * 100
                bar_html = f"<div class='bar' style='width:{rate:.1f}%;'>{rate:.1f}%</div>"
                value_info = get_top_values_summary(df[col])
                col_type = 'Text' if str(df[col].dtype) == 'object' else 'Category'
                col_label = f"<code>{col}</code><span class='q-label'>[{col_type}]</span>"
                html_content += f"<tr><td>{col_label}</td><td>{bar_html}</td><td>{value_info}</td></tr>"

            html_content += "</table>"

            if is_matrix:
                html_content += "</div>"

        html_content += "</div></details>"
        html_content += "</body></html>"

        filepath = output_dir / 'comprehensive_summary_report.html'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        generated_files['html_summary_report'] = str(filepath)
        export_summary['files_created'].append(str(filepath))
        print(f"Created {filepath.name}: A comprehensive HTML summary with matrix question support")

    def create_readme_file(export_summary, validation_report, output_dir):
        print("\n--- Creating README ---")
        readme_content = f"""# Qualtrics Data Processing Output
    Generated: {export_summary['timestamp']}

    ## 🚀 Start Here
    For a complete overview of the processing results, data quality, and response summaries, please open the main deliverable:
    - **comprehensive_summary_report.html**

    This single HTML file contains all the summary information you need in a user-friendly format.

    ## Other Generated Files

    ### Data Files
    - **analysis_ready_data.csv**: The main, cleaned dataset for use in statistical software or programming.
    - **analysis_ready_data.xlsx**: An Excel version of the main dataset for easy viewing.
    - **sentiment_analysis_data.json**: JSON structured data for sentiment analysis and NLP processing.

    ### Detailed Documentation
    - **comprehensive_codebook.csv / .xlsx**: A complete data dictionary listing every variable, its full question text, and summary statistics.
    - **variable_summaries.xlsx**: Detailed statistical summaries for numeric, categorical, and text variables.

    ### Data Quality Notes
    - Matrix questions (like Q2) are preserved with the # symbol (e.g., q2#1_1_1)
    - Summary variables have been created for all question series
    - Quality flags are included to identify potentially problematic responses
    """

        filepath = output_dir / 'README.txt'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def generate_final_datasets(optimization_result, structure_result, export_excel_duplicates=True, output_dir=None):
        """
        Main function to generate all final datasets with GUI folder selection.
        """
        print("=== Step 4: Generating Final Datasets and Documentation ===")

        # An explicit output_dir skips the dialog, which keeps the notebook runnable
        # headlessly. Falls back to the original GUI picker when nothing is passed.
        if output_dir is not None:
            output_dir = Path(output_dir)
        else:
            root = tk.Tk()
            root.withdraw()
            output_dir_str = filedialog.askdirectory(title="Select a Folder to Save Output Files")

            if not output_dir_str:
                output_dir = Path('qualtrics_output_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
                print(f"No folder selected. Creating default folder: {output_dir}")
            else:
                output_dir = Path(output_dir_str)

        os.makedirs(output_dir, exist_ok=True)
        print(f"Files will be saved to: '{output_dir}'")

        generated_files = {}
        export_summary = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_responses': len(optimization_result['optimized_data']),
            'total_variables': len(optimization_result['optimized_data'].columns),
            'files_created': []
        }

        print(f"\nCreating final datasets...")

        # Create all outputs
        create_analysis_dataset(optimization_result['optimized_data'], generated_files, export_summary, output_dir, export_excel_duplicates)
        create_comprehensive_codebook_with_mapping(optimization_result['optimized_data'], optimization_result.get('question_mapping', {}), generated_files, export_summary, output_dir, export_excel_duplicates)
        create_variable_summaries(optimization_result['optimized_data'], generated_files, export_summary, output_dir)
        create_json_for_sentiment_analysis(optimization_result['optimized_data'], optimization_result.get('question_mapping', {}), generated_files, export_summary, output_dir)
        create_html_summary_report(optimization_result, structure_result, export_summary, generated_files, output_dir)
        create_readme_file(export_summary, optimization_result['validation_report'], output_dir)

        return {'generated_files': generated_files, 'export_summary': export_summary}

    def create_analysis_dataset(df, generated_files, export_summary, output_dir, export_excel):
        """
        Create the main analysis dataset with proper column ordering.
        """
        print("\n--- Creating Main Analysis Dataset ---")
        analysis_data = df.copy()

        # Organize columns by category
        metadata_cols = [col for col in df.columns if any(meta in col.lower() for meta in
                         ['date', 'status', 'progress', 'duration', 'finished', 'recipient',
                          'location', 'distribution', 'language', 'ipaddress', 'responseid'])]
        flag_cols = [col for col in df.columns if col.startswith('flag_')]

        # Original question columns (including matrix questions with #)
        original_question_cols = []
        for col in df.columns:
            if col.startswith('q') and not col.startswith('quality_'):
                if not any(suffix in col for suffix in ['_clean', '_constant', '_count', '_rate',
                                                        '_completion', '_responses', '_age', '_category',
                                                        '_years', '_binary', '_level', '_score', '_filled']):
                    original_question_cols.append(col)

        derived_cols = [col for col in df.columns if any(suffix in col for suffix in
                       ['_clean', '_constant', '_count', '_rate', '_completion', '_responses',
                        '_age', '_category', '_years', '_binary', '_filled', '_any_response', '_total_items'])]
        summary_cols = [col for col in df.columns if any(term in col for term in
                       ['quality_score', 'quality_level', 'quality_issue', 'yes_response'])]
        other_cols = [col for col in df.columns if col not in
                     metadata_cols + flag_cols + original_question_cols + derived_cols + summary_cols]

        ordered_columns = metadata_cols + flag_cols + original_question_cols + derived_cols + summary_cols + other_cols
        analysis_data = analysis_data[ordered_columns]

        filepath = output_dir / 'analysis_ready_data.csv'
        analysis_data.to_csv(filepath, index=False)
        generated_files['analysis_dataset'] = str(filepath)
        export_summary['files_created'].append(str(filepath))
        print(f"Created {filepath.name}: {analysis_data.shape[0]:,} rows x {analysis_data.shape[1]:,} cols")

        if export_excel:
            excel_filepath = output_dir / 'analysis_ready_data.xlsx'
            analysis_data.to_excel(excel_filepath, index=False, sheet_name='Survey Data')
            generated_files['analysis_dataset_excel'] = str(excel_filepath)
            export_summary['files_created'].append(str(excel_filepath))
            print(f"Created {excel_filepath.name}: Excel version")

    def create_comprehensive_codebook_with_mapping(df, question_mapping, generated_files, export_summary, output_dir, export_excel):
        """
        Create comprehensive codebook with proper handling of matrix questions.
        """
        print("\n--- Creating Comprehensive Codebook ---")
        column_to_question = question_mapping.get('column_to_question', {})
        codebook_data = []

        for col in df.columns:
            question_text = column_to_question.get(col, col)

            # Handle derived columns
            if not question_text or question_text == col:
                base_col = col.split('_')[0] if '_' in col else col
                if '#' in base_col:
                    base_col = base_col.split('#')[0]

                if base_col in column_to_question:
                    question_text = column_to_question[base_col]
                    if '_clean' in col: question_text += " [CLEANED VERSION]"
                    elif '_binary' in col: question_text += " [BINARY: 1=Yes, 0=No]"
                    elif '_age_years' in col: question_text += " [CALCULATED AGE IN YEARS]"
                    elif '_age_category' in col: question_text += " [AGE CATEGORIES]"
                    elif '_count' in col: question_text += " [RESPONSE COUNT]"
                    elif '_rate' in col or '_completion' in col: question_text += " [COMPLETION RATE %]"
                    elif '_score' in col: question_text += " [CALCULATED SCORE]"
                    elif '_level' in col: question_text += " [CATEGORY LEVEL]"
                    elif '_filled' in col: question_text += " [NUMBER OF FILLED ITEMS]"
                    elif '_any_response' in col: question_text += " [HAS ANY RESPONSE IN MATRIX]"
                    elif '_total_items' in col: question_text += " [TOTAL ITEMS ANSWERED]"

            # Mark matrix questions
            if '#' in col:
                question_text = f"[MATRIX] {question_text}"

            codebook_entry = {
                'variable_name': col,
                'question_text': question_text,
                'variable_type': str(df[col].dtype),
                'valid_responses': df[col].notna().sum(),
                'missing_responses': df[col].isnull().sum(),
                'value_information': get_detailed_value_information(df[col], str(df[col].dtype))
            }
            codebook_data.append(codebook_entry)

        codebook_df = pd.DataFrame(codebook_data)

        filepath = output_dir / 'comprehensive_codebook.csv'
        codebook_df.to_csv(filepath, index=False)
        generated_files['codebook'] = str(filepath)
        export_summary['files_created'].append(str(filepath))
        print(f"Created {filepath.name} with {len(codebook_df)} variable definitions")

        if export_excel:
            excel_filepath = output_dir / 'comprehensive_codebook.xlsx'
            codebook_df.to_excel(excel_filepath, index=False, sheet_name='Codebook')
            generated_files['codebook_excel'] = str(excel_filepath)
            export_summary['files_created'].append(str(excel_filepath))
            print(f"Created {excel_filepath.name}: Excel version")

    def create_variable_summaries(df, generated_files, export_summary, output_dir):
        """
        Create detailed variable summary statistics.
        """
        print("\n--- Creating Variable Summary Statistics ---")
        filepath = output_dir / 'variable_summaries.xlsx'

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Numeric variables
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if not numeric_cols.empty:
                df[numeric_cols].describe().to_excel(writer, sheet_name='Numeric Variables')

            # Categorical variables
            categorical_cols = df.select_dtypes(include=['category']).columns
            if not categorical_cols.empty:
                cat_summary_list = []
                for col in categorical_cols:
                    counts = df[col].value_counts()
                    cat_summary_list.append({
                        'Variable': col,
                        'Categories': len(counts),
                        'Top Category': counts.index[0] if not counts.empty else 'N/A',
                        'Top Count': counts.iloc[0] if not counts.empty else 0
                    })
                pd.DataFrame(cat_summary_list).to_excel(writer, sheet_name='Categorical Variables', index=False)

            # Text variables
            text_cols = df.select_dtypes(include=['object']).columns
            if not text_cols.empty:
                text_summary_list = []
                for col in text_cols:
                    text_summary_list.append({
                        'Variable': col,
                        'Non-null Responses': df[col].notna().sum(),
                        'Unique Values': df[col].nunique(),
                        'Average Length': df[col].astype(str).str.len().mean()
                    })
                pd.DataFrame(text_summary_list).to_excel(writer, sheet_name='Text Variables', index=False)

        generated_files['variable_summaries'] = str(filepath)
        export_summary['files_created'].append(str(filepath))
        print(f"Created {filepath.name}: Variable summaries by type")

    def get_detailed_value_information(series, dtype):
        """
        Get detailed information about values in a series.
        """
        if series.notna().sum() == 0:
            return "All missing values"

        try:
            if 'datetime' in dtype:
                return f"Date range: {series.min().strftime('%Y-%m-%d')} to {series.max().strftime('%Y-%m-%d')}"
            elif 'int' in dtype.lower() or 'float' in dtype.lower():
                return f"Range: {series.min():.2f} to {series.max():.2f}, Mean: {series.mean():.2f}"
            elif 'category' in dtype:
                n_cats = len(series.cat.categories)
                top_3 = series.value_counts().head(3).to_dict()
                return f"{n_cats} categories, Top 3: {top_3}"
            else:
                return f"{series.nunique()} unique text responses"
        except Exception:
            return "Unable to summarize values"

    # Example usage
    return (generate_final_datasets,)


@app.cell
def _(generate_final_datasets, mo, optimization_result, os, structure_result):
    final_result = generate_final_datasets(
        optimization_result,
        structure_result,
        export_excel_duplicates=True,
        output_dir=os.environ.get("QUALTRICS_OUTPUT") or None,
    )

    files_created = final_result["export_summary"]["files_created"]

    if not mo.running_in_notebook():
        print("\n\n=== Processing Complete ===")
        print(f"{len(files_created)} files were generated.")
        print("\nStart by opening 'comprehensive_summary_report.html' in a web browser.")
        print("For sentiment analysis, use 'sentiment_analysis_data.json'")

    _file_list = "\n".join(f"    - `{name}`" for name in files_created)

    mo.md(
        f"""
        ### Processing complete: {len(files_created)} files generated

    {_file_list}

        Open `comprehensive_summary_report.html` first. Use
        `sentiment_analysis_data.json` as the input for text analysis.
        """
    )
    return


if __name__ == "__main__":
    app.run()
