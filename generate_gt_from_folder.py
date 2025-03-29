import os
import shutil
import argparse
from pathlib import Path
import sys
from typing import Set, Tuple, List


def get_image_files(input_dir: str, extensions: Set[str]) -> List[Tuple[str, str, str]]:
    """
    Get all image files with specified extensions from the input directory.

    Args:
        input_dir: Path to the input directory containing subfolders
        extensions: Set of valid image extensions

    Returns:
        List of tuples containing (file_path, base_name, extension)
    """
    image_files = []
    for root, _, files in os.walk(input_dir):
        # Skip the root directory itself
        if root == input_dir:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            base, ext = os.path.splitext(file)
            if ext.lower() in extensions:
                image_files.append((file_path, base, ext.lower()))
    return image_files


def generate_gt_from_folders(input_dir: str, output_dir: str, verbose: bool = True) -> int:
    """
    Generate .gt.txt files for images based on their parent folder names and
    organize them in the Tesseract training directory structure.

    Args:
        input_dir: Path to the main input directory containing subfolders
        output_dir: Path to the output directory (GROUND_TRUTH_DIR)
        verbose: Whether to print progress messages

    Returns:
        Number of files processed
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.gif'}

    # Get all image files
    image_files = get_image_files(input_dir, image_extensions)

    if not image_files:
        print("Error: No image files found in subdirectories!", file=sys.stderr)
        return 0

    total_files = 0
    processed_files = []

    for file_path, base_name, ext in image_files:
        # Get the folder name (last part of the path)
        folder_name = os.path.basename(os.path.dirname(file_path))

        # Create destination filenames
        dest_base = base_name
        dest_image = os.path.join(output_dir, f"{dest_base}{ext}")
        txt_filepath = os.path.join(output_dir, f"{dest_base}.gt.txt")

        # Handle duplicate filenames
        counter = 1
        while os.path.exists(dest_image) or os.path.exists(txt_filepath):
            dest_base = f"{base_name}_{counter}"
            dest_image = os.path.join(output_dir, f"{dest_base}{ext}")
            txt_filepath = os.path.join(output_dir, f"{dest_base}.gt.txt")
            counter += 1

        # Write the ground truth file
        try:
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(folder_name)

            # Copy image to output directory
            shutil.copy2(file_path, dest_image)

            total_files += 1
            processed_files.append((os.path.basename(file_path), folder_name))

            if verbose:
                print(f"Processed: {os.path.basename(file_path)} -> {folder_name}")

        except (IOError, OSError) as e:
            print(f"Error processing {file_path}: {str(e)}", file=sys.stderr)

    if verbose:
        print(f"\nDone! Processed {total_files} image files.")

    return total_files


def main():
    parser = argparse.ArgumentParser(
        description='Generate .gt.txt files from folder names for Tesseract training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  generate-gt-from-folder-name.py input_dir output_dir
  generate-gt-from-folder-name.py data/images data/ground-truth --quiet
""")

    parser.add_argument(
        'input_dir',
        help='Input directory containing subfolders with images'
    )
    parser.add_argument(
        'output_dir',
        help='Output directory (GROUND_TRUTH_DIR)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    # Validate input directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist!", file=sys.stderr)
        sys.exit(1)

    # Remove any trailing slashes for consistency
    input_dir = args.input_dir.rstrip('/\\')
    output_dir = args.output_dir.rstrip('/\\')

    if not args.quiet:
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir}")
        print("Processing...\n")

    processed_count = generate_gt_from_folders(input_dir, output_dir, not args.quiet)

    if processed_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()