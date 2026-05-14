import re
from pathlib import Path

TARGET = "."  # current folder

# Matches section headers
section_pattern = re.compile(r'^\[(.+?)\]$')

# Matches condlists
cond_pattern = re.compile(r'^(condlist_)(\d+)\s*=\s*(.*)$')


def process_section(section_lines):
    condlists = []

    # Find condlists
    for i, line in enumerate(section_lines):
        m = cond_pattern.match(line.strip())

        if m:
            prefix, num, content = m.groups()

            condlists.append({
                "line_index": i,
                "num": int(num),
                "content": content
            })

    if not condlists:
        return section_lines

    # Find _dead condlist
    dead_idx = None

    for i, c in enumerate(condlists):
        if "_dead}" in c["content"]:
            dead_idx = i
            break

    if dead_idx is None:
        return section_lines

    # Keep only condlists AFTER the _dead one
    remaining = condlists[dead_idx + 1:]

    if not remaining:
        return section_lines

    # Build new section
    new_section = []

    # Convert [section] -> ![section]
    first = section_lines[0]

    if first.startswith("["):
        new_section.append("!" + first)
    else:
        new_section.append(first)

    # Re-number remaining condlists
    start_num = condlists[dead_idx]["num"]

    for offset, c in enumerate(remaining):
        new_num = start_num + offset
        new_section.append(f"condlist_{new_num} = {c['content']}")

    # Add final !condlist_X
    final_num = start_num + len(remaining)
    new_section.append(f"!condlist_{final_num}")

    return new_section


def process_file(file_path):
    lines = file_path.read_text(encoding="cp1251").splitlines()

    sections = []
    current = []

    for line in lines:
        if section_pattern.match(line.strip()) and current:
            sections.append(current)
            current = []

        current.append(line)

    if current:
        sections.append(current)

    output = []

    for section in sections:
        output.extend(process_section(section))

    file_path.write_text("\n".join(output), encoding="cp1251")
    print(f"Processed: {file_path}")


path = Path(TARGET)

if path.is_file():
    process_file(path)

elif path.is_dir():
    for file in path.rglob("*.ltx"):
        process_file(file)

print("Done.")