from __future__ import annotations

import shutil
import tempfile
import zipapp
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "dist" / "DIKWP_ESSENCE_OMEGA_OS.pyz"


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory)
        shutil.copytree(ROOT / "src" / "essence_omega_os", stage / "essence_omega_os")
        zipapp.create_archive(
            stage,
            target=TARGET,
            main="essence_omega_os.cli:main",
            interpreter="/usr/bin/env python3",
            compressed=True,
        )
    TARGET.chmod(0o755)
    print(TARGET)


if __name__ == "__main__":
    main()
