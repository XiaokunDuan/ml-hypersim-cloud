import argparse
import os
import re

def fix_vrscene_autosave(input_file, output_file):
    """
    Reads a .vrscene file, finds any enabled auto_save features with empty
    file paths, disables them, and writes to a new file.
    """
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        return

    print(f"[INFO] Reading from: {input_file}")
    with open(input_file, 'r') as f:
        lines = f.readlines()

    new_lines = []
    lines_to_modify = {} # Dictionary to store line indices that need modification

    # First pass: identify which auto_save settings need to be disabled
    for i, line in enumerate(lines):
        # Find lines like "  auto_save = 1;"
        if "auto_save = 1;" in line.strip():
            # Now, look ahead for the corresponding auto_save_file
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Find lines like '  auto_save_file = "";' or '  auto_save_file = (null);'
                match = re.search(r'auto_save_file\s*=\s*(""\s*);', next_line)
                if match:
                    print(f"[FOUND] Line {i+1}: Found enabled auto_save with an empty file path.")
                    print(f"         L{i+1}: {line.strip()}")
                    print(f"         L{i+2}: {next_line}")
                    # Mark this auto_save line to be changed to "auto_save = 0;"
                    lines_to_modify[i] = re.sub(r'auto_save\s*=\s*1;', 'auto_save = 0;', line)
                    print(f"[ACTION] Will change line {i+1} to: {lines_to_modify[i].strip()}")

    # Second pass: build the new file content with modifications
    for i, line in enumerate(lines):
        if i in lines_to_modify:
            new_lines.append(lines_to_modify[i])
        else:
            new_lines.append(line)

    print(f"[INFO] Writing fixed scene to: {output_file}")
    with open(output_file, 'w') as f:
        f.writelines(new_lines)
    
    if not lines_to_modify:
        print("[INFO] No problematic auto_save settings were found.")
    else:
        print(f"[SUCCESS] Fixed {len(lines_to_modify)} problematic auto_save setting(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix V-Ray scene files with empty auto_save paths.")
    parser.add_argument("--in_file", required=True, help="Input .vrscene file.")
    parser.add_argument("--out_file", required=True, help="Output .vrscene file.")
    args = parser.parse_args()
    
    fix_vrscene_autosave(args.in_file, args.out_file)
    