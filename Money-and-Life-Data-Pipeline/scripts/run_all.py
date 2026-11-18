"""Run all prepared Python data modules, with clear errors for missing inputs."""
from pathlib import Path
import subprocess
import sys

SCRIPTS = [
    "clean_02A_wages.py",
    "clean_02B_employment.py",
    "clean_03_rent.py",
    "validate_04B.py",
    "clean_04C_bankofcanada.py",
    "clean_04D_charts.py",
    "clean_04E_housing.py",
]


def main():
    folder = Path(__file__).resolve().parent
    for script in SCRIPTS:
        print(f"\n=== {script} ===", flush=True)
        subprocess.run([sys.executable, str(folder / script)], check=True)
    print("\nAll Python modules completed successfully.")


if __name__ == "__main__":
    main()
