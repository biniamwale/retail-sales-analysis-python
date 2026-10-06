from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).parent / "results"
DATA_PATH = OUTPUT_DIR / "fictional_store_sales.csv"
RNG = np.random.default_rng(42)  # fixed seed: the fictional data is reproducible
