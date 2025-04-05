# User Inerface in Python [UI](UI/)

## Directions

> `pip install virtualenv` if you don't have it installed (most likely you do if you have python3).

### Linux

1. Create a virtual environment

   ```bash
   python3 -m venv .venv
   ```

2. Activate the virtual environment

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

### Windows

1. Create a virtual environment

   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment

   ```bash
   .venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

> To deactivate the virtual environment, run `deactivate` in the terminal.


## How to use UI module

Assuing venv is set up, type 

```bash
export PYTHONPATH={PATH TO UI FOLDER}
```
> For example, if the UI directory is in my current directory <br>
> `export PYTHONPATH=./UI`

After this you can use

```bash
python3 -m UI {followed by flags}
```

to run the program

For help, run

```bash
python3 -m UI [-h|--help]

usage: __main__.py [-h] [-t] [-D]

optional arguments:
  -h, --help   show this help message and exit
  -t, --tui    Launch textual user interface
  -D, --debug  Enable debug logging
```

## Dependencies C++ ONLY

- RadioHead Library for RMF95
  - https://github.com/hallard/RadioHead
- easy-install-bcm2835
  - https://github.com/szantaii/easy-install-bcm2835

RadioHead depends on bcm2835 for GPIO control
