from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CATALOGUE_DIR = PROJECT_ROOT / "data" / "catalogue"

CATALOGUE_FILENAME = "products_dummy_v1.1.xlsx"

CATALOGUE_PATH = CATALOGUE_DIR / CATALOGUE_FILENAME