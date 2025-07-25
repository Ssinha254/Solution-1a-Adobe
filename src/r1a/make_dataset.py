import os
from pathlib import Path

def ensure_dirs():
    for d in ['data/raw', 'data/weak', 'data/gold', 'data/splits']:
        Path(d).mkdir(parents=True, exist_ok=True)
    print('Ensured dataset directories exist.')

if __name__ == '__main__':
    ensure_dirs() 