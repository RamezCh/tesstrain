import os
import shutil
import argparse
from pathlib import Path
import sys
from typing import Set, List, Tuple


def get_image_files(input_dir: str, extensions: Set[str]) -> List[Tuple[Path, str, str]]:
    """
    Get all image files with specified extensions from the input directory.
    """
    image_files = []
    for entry in os.scandir(input_dir):
        if entry.is_dir():
            for file in os.scandir(entry.path):
                file_path = Path(file.path)
                if file_path.suffix.lower() in extensions:
                    image_files.append((file_path, file_path.stem, file_path.suffix.lower()))
    return image_files


def generate_gt_from_folders(input_dir: str, output_dir: str, verbose: bool = True) -> int:
    """
    Generate .gt.txt files for images based on their parent folder names and
    organize them in the Tesseract training directory structure.
    """
    print("Ground-Truth generation beginning...")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_extensions = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.gif'}
    image_files = get_image_files(input_dir, image_extensions)

    total_files = 0
    existing_files = set(output_dir.glob("*"))

    for file_path, base_name, ext in image_files:
        folder_name = file_path.parent.name
        dest_base = base_name
        dest_image = output_dir / f"{dest_base}{ext}"
        txt_filepath = output_dir / f"{dest_base}.gt.txt"

        counter = 1
        while dest_image in existing_files or txt_filepath in existing_files:
            dest_base = f"{base_name}_{counter}"
            dest_image = output_dir / f"{dest_base}{ext}"
            txt_filepath = output_dir / f"{dest_base}.gt.txt"
            counter += 1

        try:
            txt_filepath.write_text(folder_name, encoding='utf-8')
            shutil.copy2(file_path, dest_image)
            existing_files.add(dest_image)
            existing_files.add(txt_filepath)
            total_files += 1
            if verbose:
                print(f"Processed: {file_path.name} -> {folder_name}")
        except (IOError, OSError) as e:
            print(f"Error processing {file_path}: {str(e)}", file=sys.stderr)

    if verbose:
        print(f"\nDone! Processed {total_files} image files.")
    return total_files


def main():
    parser = argparse.ArgumentParser(description='Generate .gt.txt files from folder names for Tesseract training')
    parser.add_argument('input_dir', help='Input directory containing subfolders with images')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')
    args = parser.parse_args()

    processed_count = generate_gt_from_folders(args.input_dir.rstrip('/\\'), args.output_dir.rstrip('/\\'),
                                               not args.quiet)
    if processed_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()