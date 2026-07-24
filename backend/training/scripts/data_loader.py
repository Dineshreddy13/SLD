import os
import pandas as pd
from pathlib import Path
import typing

# Configuration for labels to exclude from the dataset
EXCLUDED_LABELS = {"J", "Z"}

def load_data(landmarks_dir: str | Path) -> pd.DataFrame:
    """
    Loads all CSV files from the landmarks directory into a single pandas DataFrame.
    
    Args:
        landmarks_dir: Path to the directory containing the CSV files.
        
    Returns:
        pd.DataFrame containing 63 landmark features and a 'label' column.
    """
    landmarks_dir = Path(landmarks_dir)
    
    if not landmarks_dir.exists() or not landmarks_dir.is_dir():
        print(f"Warning: Landmarks directory '{landmarks_dir}' not found.")
        print("Please run 'python scripts/collect_dataset.py' to collect data first.")
        return pd.DataFrame()
        
    csv_files = list(landmarks_dir.glob("*.csv"))
    if not csv_files:
        print(f"Warning: No CSV files found in '{landmarks_dir}'.")
        print("Please run 'python scripts/collect_dataset.py' to collect data first.")
        return pd.DataFrame()
        
    dataframes = []
    
    for csv_file in csv_files:
        label = csv_file.stem
        
        if label in EXCLUDED_LABELS:
            print(f"Excluding labels: {label} (motion-based signs not supported in static model).")
            continue
            
        try:
            # Assuming the CSV has a header: image_file, x0, y0, z0, ..., x20, y20, z20
            df = pd.read_csv(csv_file)
            if df.empty:
                continue
                
            df['label'] = label
            # Drop the image_file column as it's not a feature
            if 'image_file' in df.columns:
                df = df.drop(columns=['image_file'])
                
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            
    if not dataframes:
        return pd.DataFrame()
        
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def print_summary(df: pd.DataFrame, min_samples_warning: int = 20):
    """
    Prints a summary of the loaded dataset.
    """
    if df.empty:
        print("Dataset is empty. No summary to print.")
        return
        
    print("\n" + "="*50)
    print("Dataset Summary")
    print("="*50)
    
    label_counts = df['label'].value_counts().sort_index()
    
    print(f"Total samples: {len(df)}")
    print(f"Total classes: {len(label_counts)}\n")
    
    print("Samples per class:")
    for label, count in label_counts.items():
        warning = f"  <-- WARNING: Fewer than {min_samples_warning} samples!" if count < min_samples_warning else ""
        print(f"  {label}: {count}{warning}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Test the data loader
    print("Testing data loader...")
    # base_dir is backend/
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent.parent
    datasets_dir = base_dir / "datasets" / "landmarks"
    
    df = load_data(datasets_dir)
    print_summary(df)
