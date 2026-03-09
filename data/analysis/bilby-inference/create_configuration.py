from utils.path_utils import get_path_to_config_file
from pathlib import Path
import yaml

def update_slurm_extra_lines_in_ini():
    """
    For every file in ./configuration (relative to this script) ending with
    '*-no-slurm-extra-lines.ini', update the single line that starts with
    'slurm-extra-lines =' to include:
      - partition=<cluster_partition>
      - and, if email is not None/empty: mail-type=All mail-user=<email>

    Write the modified file next to the original, with the suffix
    '-no-slurm-extra-lines' removed from the filename.
    """
    # Load config.yaml (path returned as string)
    cfg_path = get_path_to_config_file()
    with Path(cfg_path).open("r") as f:
        config = yaml.safe_load(f) or {}

    email = config.get("email")
    partition = config.get("cluster_partition")
    if not partition:
        raise KeyError("config.yaml must define 'cluster_partition'")

    parts = [f"partition={partition}"]
    if email not in (None, ""):
        parts += ["mail-type=All", f"mail-user={email}"]
    replacement_value = " ".join(parts)

    script_dir = Path(__file__).resolve().parent
    ini_dir = script_dir / "configuration"

    for ini_path in sorted(ini_dir.glob("*-no-slurm-extra-lines.ini")):
        lines = ini_path.read_text().splitlines(keepends=True)

        matches = 0
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith("slurm-extra-lines ="):
                matches += 1
                indent = line[: len(line) - len(stripped)]
                newline = "\n" if line.endswith("\n") else ""
                lines[i] = f"{indent}slurm-extra-lines = {replacement_value}{newline}"

        out_name = ini_path.name.replace("-no-slurm-extra-lines", "").replace("__", "_")
        out_path = ini_path.with_name(out_name)
        out_path.write_text("".join(lines))

update_slurm_extra_lines_in_ini()