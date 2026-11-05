\# PyProjs



A collection of Python projects and experiments, mainly around visualization, along with some utilities, GUI work and ML/AI explorations.



\## Repository Structure



```

PyProjs/

├── BMTCTRACK/                    # Bus tracking project

├── EPT-NDI-Producer-Consumer/    # NDI producer/consumer demo

├── MKBCompression/               # Compression experiments

├── ModularViz/                   # Modular visualization framework

├── QtAthon2025/                  # Qt hackathon project (2025)

├── hugging-face/                 # Hugging Face model experiments

├── tic-tac-toe/                  # Tic-tac-toe game

├── TextJustification.py          # Word-wrapping utility

└── tryviz.py                     # Matplotlib plotting demo

```



\## Projects



> Descriptions marked \*\*TODO\*\* are inferred from folder names. Please replace them with what each project actually does.



\### \[BMTCTRACK](BMTCTRACK/)

TODO: One or two lines on what this tracks (e.g. BMTC bus tracking and visualization), the data source, and the output.



\### \[EPT-NDI-Producer-Consumer](EPT-NDI-Producer-Consumer/)

TODO: A producer/consumer pipeline for NDI (Network Device Interface) video streams. Say what the producer sends, what the consumer does with it, and any NDI runtime/SDK requirements.



\### \[MKBCompression](MKBCompression/)

TODO: Describe the compression approach (algorithm, data type, e.g. text, images or point clouds) and how results are measured.



\### \[ModularViz](ModularViz/)

TODO: Describe the modular visualization design: what the modules are, how they plug together, and which plotting/rendering libraries it uses.



\### \[QtAthon2025](QtAthon2025/)

TODO: Describe the Qt hackathon entry: the problem statement, the GUI toolkit (PyQt / PySide), and how to launch it.



\### \[hugging-face](hugging-face/)

TODO: List the Hugging Face models or pipelines explored (e.g. text, vision, audio) and the tasks they are applied to.



\### \[tic-tac-toe](tic-tac-toe/)

TODO: Describe the game (console or GUI, human vs. human or vs. computer) and how to play.



\## Standalone Scripts



\### `TextJustification.py`

Splits a list of words into lines that fit within a maximum width, using a greedy line-breaking approach. Words are joined with single spaces (no extra padding is added to reach exact width).



```bash

python TextJustification.py <maxWidth> <word1> <word2> ...

```



Example:



```bash

python TextJustification.py 16 This is an example of text justification

```



Each resulting line is printed in quotes.



\### `tryviz.py`

A small Matplotlib/NumPy demo that draws two plots: a sine-based line plot over a small set of x-values, and a line plot with circular markers for a short list of points.



```bash

python tryviz.py

```



\## Getting Started



\*\*Prerequisites:\*\* Python 3.9 or newer (the scripts use built-in generic type hints such as `list\[str]`).



```bash

git clone https://github.com/bmkamath2000/PyProjs.git

cd PyProjs



\# optional: isolated environment

python -m venv .venv

\# Windows: .venv\\Scripts\\activate

\# macOS/Linux: source .venv/bin/activate



pip install numpy matplotlib

```



Individual projects may need additional packages (e.g. Qt bindings, `transformers`, an NDI binding). Check each project folder for its own dependencies, or add a `requirements.txt` per project.



\## Author



Mukesh (GitHub: \[@bmkamath2000](https://github.com/bmkamath2000))



\## License



TODO: Add a license (e.g. MIT) if you want others to reuse this code.

