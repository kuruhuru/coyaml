# Changelog

## [v0.10.2] - 2025-01-27

### Fixed
- Fixed source distribution packaging: added missing Python files to tar.gz archive
- Added `packages = ["src/coyaml"]` and `"src/coyaml/**/*.py"` to sdist configuration

## [v0.10.1] - 2025-08-25

### Fixed
- Added PEP 561 typing package support: included `py.typed` and package-level stubs `coyaml/__init__.pyi` with decorator overloads.
- Fixed Pyright false positive: `Argument missing for parameter "func"` for `@coyaml(...)` usage via proper overloads and moving stubs to package root.
- Packaging config updated to include `.pyi` and `py.typed` into wheel and sdist.

## [v0.10.0] - 2025-08-23

### Added
- Injection by parameter name with optional `mask` (glob over dotted paths: `*`, `**`) and deterministic behavior
- Improved error diagnostics for injection (lists candidates, shows masks) and templates
- New search utilities for dotted trees and masks
- Tutorials (Basic, Templates, Injection, Merging, Registry), Concepts, Scenarios, Cookbook

### Changed
- `YResource.path` is now optional for by-name injection scenarios
- Documentation restructured and expanded; README updated with DI examples

### Fixed
- Robust globstar handling in mask compilation
- Numerous test improvements; coverage threshold enforced at 80% (current ~96%)

## [v0.9.4] - 2025-07-21

### Added to __init__.py
- New `YSettings` class as the primary configuration API
- `YRegistry` for thread-safe configuration management with URI-based factory helpers
- `YNode` class with extended API: `items()`, `values()`, rich equality and iterator support
- `YSource` abstract base class and concrete implementations: `YamlFileSource`, `EnvFileSource`
- `@coyaml` decorator and `YResource` metadata for zero-boilerplate dependency injection
- `deep_merge` utility function for configuration merging
- Legacy imports maintained for backward compatibility (`YConfig`, `YConfigFactory`)

### Changed
- Updated package exports to include new API classes while maintaining legacy support
- Improved module structure with better separation of concerns

## [v0.9.3] - 2025-06-22

### Added
- Powerful template engine with `${{ action:param }}` syntax supporting `env`, `file`, `config` and `yaml` actions
- `YSettings.resolve_templates()` for recursive template evaluation
- Thread-safe `YRegistry` with URI-based factory helpers (`create_from_uri`, `create_from_uri_list`)
- Decorator `@coyaml` and metadata `YResource` for zero-boilerplate dependency injection with `typing.Annotated` support and automatic conversion to Pydantic models
- New sources: `YamlFileSource`, `EnvFileSource` (binary-safe I/O)
- Extended `YNode` API: `items()`, `values()`, rich equality and iterator support
- Almost 100 % test coverage, over 70 new tests covering edge cases and error paths

### Changed
- All file operations switched to binary mode with explicit UTF-8 decoding for robust Unicode handling
- Deep-merge logic extracted to `coyaml.utils.merge.deep_merge`
- Documentation polished and translated, quick-start rewritten
- `pyproject.toml` updated: project version, dependency bumps, stricter type-checking and lint rules

### Removed
- Legacy `_internal.deps` module (functionality superseded by `@coyaml` injection utilities)

### Fixed
- Nested and recursive template resolution edge cases
- Graceful errors for missing environment variables, files and YAML decoding problems
- Numerous minor bug fixes discovered via exhaustive test suite

## [v0.9.2] - 2025-06-14

### Added
- Added CI/CD and code coverage badges
- Added Coveralls integration

### Changed
- Improved test coverage to 100%
- Improved documentation

## [v0.9.1] - 2025-06-12

### Added
- Added documentation using MkDocs Material
- Added pymdown-extensions
- Added ReadTheDocs configuration

### Changed
- Changed documentation theme to Material
- Code refactoring
- Translated documentation to English

### Fixed
- Fixed test issues
- Fixed documentation

## [v0.1.0] - 2025-06-07

### Added
- Initial project version
- Basic project structure
- Initial documentation 