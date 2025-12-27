"""
STAAD.Pro Node Data Validator and File Generator
IIT Delhi Research Project - Structural Engineering Automation

This script:
1. Reads node data from CSV or Excel files
2. Validates the data for errors
3. Generates a STAAD.Pro input file if validation passes
"""

import pandas as pd
import os
import sys


def read_node_data(file_path):
    """
    Read node data from CSV or Excel file.
    
    Args:
        file_path: Path to the input file (CSV or Excel)
    
    Returns:
        DataFrame containing node data, or None if error occurs
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"ERROR: File '{file_path}' not found!")
            return None
        
        # Read Excel file (.xlsx, .xls)
        if file_path.endswith(('.xlsx', '.xls')):
            print(f"Reading Excel file: {file_path}")
            df = pd.read_excel(file_path)
        
        # Read CSV file
        elif file_path.endswith('.csv'):
            print(f"Reading CSV file: {file_path}")
            df = pd.read_csv(file_path)
        
        else:
            print(f"ERROR: Unsupported file format. Please use .csv, .xlsx, or .xls")
            return None
        
        print(f"Nodes read successfully: {len(df)} rows found")
        return df
    
    except Exception as e:
        print(f"ERROR: Failed to read file - {str(e)}")
        return None


def validate_node_data(df):
    """
    Validate node data for errors.
    
    Checks for:
    - Missing columns
    - Duplicate node IDs
    - Duplicate coordinates
    - Missing/empty values
    - Non-numeric coordinates
    
    Args:
        df: DataFrame containing node data
    
    Returns:
        True if validation passes, False otherwise
    """
    print("\n" + "="*60)
    print("VALIDATION REPORT")
    print("="*60)
    
    validation_passed = True
    
    # Check 1: Required columns exist
    required_columns = ['node_id', 'x', 'y', 'z']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"\n❌ ERROR: Missing required columns: {missing_columns}")
        print(f"   Available columns: {list(df.columns)}")
        validation_passed = False
        return False
    
    print("\n✓ Required columns found")
    
    # Check 2: Remove rows with any missing values and report
    initial_count = len(df)
    df_clean = df.dropna(subset=required_columns)
    missing_count = initial_count - len(df_clean)
    
    if missing_count > 0:
        print(f"\n❌ ERROR: Found {missing_count} row(s) with missing values")
        print("   Rows with missing data will be skipped")
        validation_passed = False
    else:
        print("\n✓ No missing values found")
    
    # Check 3: Check for duplicate node IDs
    duplicate_ids = df_clean[df_clean.duplicated(subset=['node_id'], keep=False)]
    
    if len(duplicate_ids) > 0:
        print(f"\n❌ ERROR: Found {len(duplicate_ids)} row(s) with duplicate node IDs:")
        duplicate_id_list = duplicate_ids['node_id'].unique()
        for dup_id in duplicate_id_list:
            print(f"   Node ID {dup_id} appears {len(duplicate_ids[duplicate_ids['node_id'] == dup_id])} times")
        validation_passed = False
    else:
        print("\n✓ No duplicate node IDs found")
    
    # Check 4: Check for duplicate coordinates (same x, y, z)
    duplicate_coords = df_clean[df_clean.duplicated(subset=['x', 'y', 'z'], keep=False)]
    
    if len(duplicate_coords) > 0:
        print(f"\n❌ ERROR: Found {len(duplicate_coords)} row(s) with duplicate coordinates:")
        for idx, row in duplicate_coords.iterrows():
            print(f"   Node ID {row['node_id']}: ({row['x']}, {row['y']}, {row['z']})")
        validation_passed = False
    else:
        print("\n✓ No duplicate coordinates found")
    
    # Check 5: Check if coordinates are numeric
    non_numeric_errors = []
    
    for col in ['x', 'y', 'z']:
        # Try to convert to numeric, invalid values become NaN
        numeric_series = pd.to_numeric(df_clean[col], errors='coerce')
        non_numeric = df_clean[numeric_series.isna()]
        
        if len(non_numeric) > 0:
            non_numeric_errors.append({
                'column': col,
                'count': len(non_numeric),
                'node_ids': non_numeric['node_id'].tolist()
            })
    
    if non_numeric_errors:
        print(f"\n❌ ERROR: Found non-numeric coordinate values:")
        for error in non_numeric_errors:
            print(f"   Column '{error['column']}': {error['count']} invalid value(s)")
            print(f"   Affected Node IDs: {error['node_ids']}")
        validation_passed = False
    else:
        print("\n✓ All coordinates are numeric")
    
    # Final validation result
    print("\n" + "="*60)
    if validation_passed:
        print("✓ VALIDATION PASSED - All checks successful")
        print(f"✓ Valid nodes: {len(df_clean)}")
    else:
        print("❌ VALIDATION FAILED - Please fix errors before generating STAAD file")
    print("="*60 + "\n")
    
    return validation_passed


def generate_staad_file(df, output_filename="model.std"):
    """
    Generate STAAD.Pro input file from validated node data.
    
    Args:
        df: DataFrame containing validated node data
        output_filename: Name of output STAAD file (default: "model.std")
    
    Returns:
        True if file generated successfully, False otherwise
    """
    try:
        # Ensure coordinates are numeric
        df['x'] = pd.to_numeric(df['x'], errors='coerce')
        df['y'] = pd.to_numeric(df['y'], errors='coerce')
        df['z'] = pd.to_numeric(df['z'], errors='coerce')
        
        # Remove any rows with NaN (shouldn't happen if validation passed)
        df_clean = df.dropna(subset=['x', 'y', 'z'])
        
        # Sort by node_id for better readability
        df_sorted = df_clean.sort_values('node_id')
        
        # Open file for writing
        with open(output_filename, 'w') as f:
            # Write STAAD.Pro header
            f.write("STAAD SPACE\n")
            f.write("START JOB INFORMATION\n")
            f.write("ENGINEER DATE 01-Jan-2025\n")
            f.write("END JOB INFORMATION\n")
            f.write("UNIT METER KN\n")
            f.write("\n")
            
            # Write node coordinates section
            f.write("JOINT COORDINATES\n")
            
            # Write each node in STAAD format: node_id x y z
            for idx, row in df_sorted.iterrows():
                node_id = int(row['node_id'])
                x = float(row['x'])
                y = float(row['y'])
                z = float(row['z'])
                
                # STAAD format: node_id x y z
                f.write(f"{node_id} {x:.6f} {y:.6f} {z:.6f}\n")
            
            f.write("END JOINT COORDINATES\n")
        
        print(f"STAAD file generated successfully: {output_filename}")
        print(f"Total nodes written: {len(df_sorted)}")
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to generate STAAD file - {str(e)}")
        return False


def main():
    """
    Main function to run the automation script.
    """
    print("\n" + "="*60)
    print("STAAD.Pro Node Data Validator and File Generator")
    print("IIT Delhi Research Project")
    print("="*60 + "\n")
    
    # Get input file path from user
    # You can modify this to accept command line arguments or hardcode the path
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter the path to your node data file (CSV or Excel): ").strip()
    
    # Step 1: Read node data
    df = read_node_data(input_file)
    
    if df is None:
        print("\nProgram terminated due to file reading error.")
        return
    
    # Step 2: Validate node data
    validation_passed = validate_node_data(df)
    
    if not validation_passed:
        print("\nValidation failed. Please fix errors in your data file and try again.")
        return
    
    # Step 3: Generate STAAD file
    output_file = "model.std"
    success = generate_staad_file(df, output_file)
    
    if success:
        print(f"\n✓ SUCCESS: Automation completed successfully!")
        print(f"✓ Output file: {output_file}")
    else:
        print("\n❌ ERROR: Failed to generate STAAD file.")


# Run the program
if __name__ == "__main__":
    main()