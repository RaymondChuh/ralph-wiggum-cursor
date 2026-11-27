# Notebooks

Hands-on Jupyter notebooks that run on **public datasets or our de-identified samples**. No
hardware needed. Each one runs top to bottom in under two minutes.

Running locally:

```bash
cd smart-insoles
python3 -m venv .venv && source .venv/bin/activate
pip install -e software/gaitlab jupyterlab   # once gaitlab exists (phase P5)
jupyter lab docs/notebooks/
```

Notebooks appear here as the project reaches them (see the [curriculum](../chapters/index.md)).
