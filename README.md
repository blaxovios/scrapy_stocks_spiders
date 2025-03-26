# List of modules doing various executions

### Installation

1. Python version 3.12 required.
2. Secondly, create a virtual environment for Python 3 with `python3.12 -m venv venv` and then activate with `source venv/bin/activate`.
3. Then, we need to install dependencies based on [pyproject.toml](pyproject.toml) file. Use `pip install uv` and then `uv pip install --upgrade eager -e .`. Another way to install required dependencies is by using `uv pip install -r requirements.txt`. 
⚠️ Be aware that if you use the existing requirements file to install dependencies, you may have compatibility issues due to different machines.

### Exclude from git large files

To avoid pushing files larger than 100 MB, use `find . -size +100M | cat >> .gitignore` and `find . -size +100M | cat >> .git/info/exclude`.

### Memory-Testing

It uses [memray](https://github.com/bloomberg/memray/blob/main/README.md) to profile memory. Very useful to optimize code and reduce memory usage thus <u>reducing google cloud costs</u>.

run in terminal :

```bash
python3 -m memray run -o data/static/html/memstats.bin src/handle_xls.py
```

Then, generate the flamegraph from the .bin file:
```
memray flamegraph data/static/html/memstats.bin
```

For more information on how to use see [Usage](https://github.com/bloomberg/memray/blob/main/README.md#usage).

### Troubles encountered and solutions

There is a specific order of packages that need to be downloaded and install manually (if anaconda is not used) prior to using geopandas.
This can be better explained [here](https://towardsdatascience.com/geopandas-installation-the-easy-way-for-windows-31a666b3610f) and in the [gps_to_map.py](gps_to_map.py) file.

### Notes

Since this project consists of many python modules that do various things and/or communicate between them, required libraries and packages may have conflicts in different machines and operating systems.

### Purpose

The purpose of this project is to keep a list of modules that help through productivity and can be easily maintained throughout, due too its lack of dependency between its modules.
Statistics calculation, copy-pasting, scraping, file conversions, information extraction from files, data manipulation and even more function can be found and used.
This is an on going project that supports my personal work but also can help others.