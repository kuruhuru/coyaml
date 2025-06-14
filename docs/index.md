# Coyaml

Coyaml is an intuitive Python library designed to simplify YAML configuration management. It lets you split your configurations into smaller files, embed environment variables, and reuse configuration nodes—keeping your settings organized, maintainable, and scalable.

Developed with practical insights from real-world projects, Coyaml is ideal for Python developers who require flexible, powerful, and simple configuration handling.

![Tests](https://github.com/kuruhuru/coyaml/actions/workflows/ci-main.yml/badge.svg)
![Coverage](https://img.shields.io/coveralls/github/kuruhuru/coyaml.svg?branch=main)
![Publish](https://github.com/kuruhuru/coyaml/actions/workflows/publish.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/coyaml.svg)
![PyPI - License](https://img.shields.io/pypi/l/coyaml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/coyaml)
---
## Why Use Coyaml?

Coyaml simplifies common YAML management tasks:

* **Dot Notation Access**: Easily access nested configuration (`config.section.option`).
* **Pydantic Integration**: Automatic validation and type safety for your settings.
* **Environment Variables**: Direct integration of OS or `.env` variables, with defaults.
* **External File & YAML Inclusion**: Embed file contents and additional YAML files seamlessly.
* **Reusable Nodes**: Reference and reuse YAML configuration sections dynamically.

## Quick Links

- [Installation](1_installation.md)
- [Quickstart](2_quickstart.md)
<!-- - [Configuration & Templates](configuration.md) -->
<!-- - [Tutorials](tutorials/first-steps.md) -->
- [API Reference](api/modules.md)
<!-- - [Contributing](contributing.md) -->
- [Changelog](CHANGELOG.md)
