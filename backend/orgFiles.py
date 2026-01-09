import os
import shutil

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TESTS_DIR = os.path.join(BASE_DIR, "tests")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# Create folders if they don't exist
os.makedirs(TESTS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

def is_test_file(filename: str) -> bool:
    """
    Detects common Python test file naming patterns:
    - test_something.py
    - something_test.py
    """
    if not filename.endswith(".py"):
        return False

    name = filename.lower()
    return name.startswith("test_") or name.endswith("_test.py")

def is_markdown_file(filename: str) -> bool:
    return filename.lower().endswith(".md")

def main():
    moved_any = False

    for filename in os.listdir(BASE_DIR):
        src_path = os.path.join(BASE_DIR, filename)

        # Skip directories and this script itself
        if os.path.isdir(src_path):
            continue

        if filename == os.path.basename(__file__):
            continue

        # Move test files
        if is_test_file(filename):
            dest_path = os.path.join(TESTS_DIR, filename)
            print(f"Moving test file: {filename} -> tests/")
            shutil.move(src_path, dest_path)
            moved_any = True

        # Move markdown files
        elif is_markdown_file(filename):
            dest_path = os.path.join(DOCS_DIR, filename)
            print(f"Moving markdown file: {filename} -> docs/")
            shutil.move(src_path, dest_path)
            moved_any = True

    if not moved_any:
        print("No files needed to be moved.")
    else:
        print("File organization complete.")

if __name__ == "__main__":
    main()
