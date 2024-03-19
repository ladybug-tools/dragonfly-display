[![Build Status](https://github.com/ladybug-tools/dragonfly-display/workflows/CI/badge.svg)](https://github.com/ladybug-tools/dragonfly-display/actions)

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/) [![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# dragonfly-display

Adds methods and a CLI to translate dragonfly objects to VisualizationSets.

## Installation

```console
pip install -U dragonfly-display
```

If you want to also include all dependencies needed to produce VTK visualizations
from dragonfly Models use.

```console
pip install -U dragonfly-display[full]
```

To check if the command line interface is installed correctly use `dragonfly-display --help`

## QuickStart

```python
import dragonfly_display

```

## [API Documentation](http://ladybug-tools.github.io/dragonfly-display/docs)

## Local Development

1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/dragonfly-display

# or

git clone https://github.com/ladybug-tools/dragonfly-display
```
2. Install dependencies:
```console
cd dragonfly-display
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./dragonfly_display
sphinx-build -b html ./docs ./docs/_build/docs
```
