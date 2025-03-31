# User Inerface in Python

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

## Dependencies C++ ONLY

- RadioHead Library for RMF95
  - https://github.com/hallard/RadioHead
- easy-install-bcm2835
  - https://github.com/szantaii/easy-install-bcm2835

RadioHead depends on bcm2835 for GPIO control
