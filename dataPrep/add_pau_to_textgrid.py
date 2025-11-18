"""
Post-process MFA TextGrid files to replace empty strings with 'pau' for silence intervals.

Usage:
    python add_pau_to_textgrid.py \
        --input-dir /Users/derekvawdrey/Documents/MFA/aligned_output \
        --output-dir /path/to/output
"""

import argparse
from pathlib import Path


def process_textgrid(input_path: Path, output_path: Path) -> None:
    """Replace empty strings with 'pau' in phones tier only."""
    content = input_path.read_text(encoding="utf-8")
    
    # Split content into lines for processing
    lines = content.split('\n')
    modified_lines = []
    in_phones_tier = False
    
    for line in lines:
        # Check if we're entering the phones tier
        if 'name = "phones"' in line:
            in_phones_tier = True
            modified_lines.append(line)
        # Check if we're leaving the phones tier (entering a new item or end of file)
        elif in_phones_tier and line.strip().startswith('item ['):
            in_phones_tier = False
            modified_lines.append(line)
        # If we're in the phones tier, replace empty text with "pau"
        elif in_phones_tier and 'text = ""' in line:
            modified_lines.append(line.replace('text = ""', 'text = "pau"'))
        else:
            modified_lines.append(line)
    
    modified_content = '\n'.join(modified_lines)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(modified_content, encoding="utf-8")


def process_directory(input_dir: Path, output_dir: Path, overwrite: bool = False) -> None:
    """Process all TextGrid files in a directory."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    textgrid_files = list(input_dir.rglob("*.TextGrid"))
    
    if not textgrid_files:
        print(f"No TextGrid files found in {input_dir}")
        return
    
    print(f"Found {len(textgrid_files)} TextGrid files")
    
    for input_file in textgrid_files:
        # Preserve directory structure relative to input_dir
        relative_path = input_file.relative_to(input_dir)
        output_file = output_dir / relative_path
        
        if not overwrite and output_file.exists():
            continue
        
        process_textgrid(input_file, output_file)
    
    print(f"Processed {len(textgrid_files)} files. Output written to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Replace empty strings with 'pau' in MFA TextGrid files"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Input directory containing TextGrid files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for processed TextGrid files"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files"
    )
    
    args = parser.parse_args()
    process_directory(args.input_dir, args.output_dir, args.overwrite)


if __name__ == "__main__":
    main()

