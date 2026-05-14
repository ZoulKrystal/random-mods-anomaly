import os
import re

root_folder = r"C:\Users\Mati\AppData\Local\ModOrganizer\STALKER Anomaly\mods\[SlopCrystal] Shit Mutants Remover\gamedata\configs\scripts"

keywords = ["simulation_lurker", "simulation_lurker_1_2"]
param_name = "spawn_squads"

section_pattern = re.compile(r"\[(.*?)\]")

for root, dirs, files in os.walk(root_folder):
    for file in files:
        if file.endswith(".py"):
            continue
        file_path = os.path.join(root, file)

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            current_section = None
            output_blocks = []

            for line in lines:
                line_stripped = line.strip()

                # Detect section
                section_match = section_pattern.match(line_stripped)
                if section_match:
                    current_section = section_match.group(1)
                    continue

                # Detect parameter
                if line_stripped.startswith(param_name) and current_section:
                    # Split values
                    parts = line_stripped.split("=", 1)
                    if len(parts) < 2:
                        continue

                    values = [v.strip() for v in parts[1].split(",")]

                    # Keep only matching keywords
                    filtered = [v for v in values if any(k in v for k in keywords)]

                    if filtered:
                        output_blocks.append(
                            f"![{current_section}]\n"
                            f"<{param_name} = {', '.join(filtered)}\n"
                        )

            # If nothing matched → delete file
            if not output_blocks:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                # Overwrite file with only processed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(output_blocks))
                print(f"Processed: {file_path}")

        except Exception as e:
            print(f"Skipped (error): {file_path} -> {e}")


# --- Empty folder cleanup (repeat until stable) ---
while True:
    deleted_any = False

    for root, dirs, files in os.walk(root_folder, topdown=False):
        if not dirs and not files:
            try:
                os.rmdir(root)
                print(f"Deleted empty folder: {root}")
                deleted_any = True
            except Exception as e:
                print(f"Skipped folder: {root} -> {e}")

    if not deleted_any:
        break