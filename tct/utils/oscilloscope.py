import pandas as pd
from glob import glob
import os
import re

def folder2pd(folder):
    r = re.compile('([0-9]+)\.txt')
    all_fns = glob(os.path.join(folder, '*.txt'))
    data = {}
    for fn in all_fns:
        isample = int(r.search(fn).group(1))
        data[isample] = pd.read_csv(fn, skiprows=4, index_col='Time')
    data = pd.concat(data, names=['sample']).sort_index()
    return data
