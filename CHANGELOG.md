# Changelog

## [Unreleased]

## [0.2.0] - 2026-09-10

### Added

- Added `install_r_packages()` for explicitly installing missing R dependencies.
- Added regression coverage for side-effect-free package imports and the
  `Itemsets.items()` accessor.
- Added Python-style snake-case aliases for public APIs inherited from R while
  retaining the existing names for compatibility.
- Added `html_widget()` for saving and embedding self-contained arulesViz HTML
  widgets without relying on notebook-server file routing.

### Changed

- Importing `arulespy` no longer initializes R, creates an R library directory,
  or changes global R options. Missing R packages are installed only when the
  corresponding `arulespy.arules` or `arulespy.arulesViz` module is imported.
- Indexing now supports open-ended and stepped slices, negative indices,
  integer sequences, and validated boolean masks with Python-style errors.
- Consolidated package metadata and dependencies in `pyproject.toml`, switched
  the build backend to Hatchling, and replaced deprecated direct `setup.py`
  usage.
- Releases now build validated source and wheel distributions separately from
  publishing and authenticate to PyPI with Trusted Publishing.
- Supported Python versions are now 3.11 through 3.14. CI tests each supported
  version against the current R release and validates distribution builds.
- Corrected the README's public API names and example output, clarified setup
  and low-level usage, and expanded the Python API docstrings.
- Core and visualization APIs are now loaded lazily while retaining their
  top-level exports.
- `arulesViz` is now optional unless visualization functionality is requested.
- Updated the installation documentation to describe explicit R package setup.
- Improved the example notebooks and generated HTML examples.

### Fixed

- Fixed `Itemsets.items()` calling R's unsupported `lhs()` method instead of
  `items()`.
- Fixed `Itemsets.new()` and `Rules.new()` passing S4 slots positionally.
- Fixed `addQuality()` aligning new columns against incompatible pandas/R row
  indexes instead of row position.
- Failed automatic R package installations now produce actionable import
  errors.

## [0.1.4] - 2023-09-12

### Added

- Added package version reporting.
- Added citation information.

### Changed

- Improved installation guidance, including instructions for Windows.
- Changed first-import handling of missing R packages and R warnings.

## [0.1.3] - 2023-06-23

### Changed

- Exposed the underlying R packages through `R_arules` and `R_arulesViz`.
- Improved docstrings and low-level interface naming.

## [0.1.2] - 2023-05-31

### Added

- Added conversion to SciPy sparse matrix representations.
- Added the project paper and reference material.

### Changed

- Set the minimum supported Python version to 3.8.
- Updated the test environment and CI configuration for SciPy.

## [0.1.1] - 2023-05-22

### Changed

- Updated the usage examples.

## [0.1.0] - 2023-05-20

### Added

- Published the initial 0.1 release series.
- Added examples for manually creating association rules.

[Unreleased]: https://github.com/mhahsler/arulespy/compare/arulespy_0.2.0...HEAD
[0.2.0]: https://github.com/mhahsler/arulespy/compare/arulespy_0.1.4...arulespy_0.2.0
[0.1.4]: https://github.com/mhahsler/arulespy/compare/arulespy_0.1.3...arulespy_0.1.4
[0.1.3]: https://github.com/mhahsler/arulespy/compare/arulespy_0.1.2...arulespy_0.1.3
[0.1.2]: https://github.com/mhahsler/arulespy/compare/arulespy_0.1.1...arulespy_0.1.2
[0.1.1]: https://github.com/mhahsler/arulespy/compare/arulespy_0.1.0...arulespy_0.1.1
[0.1.0]: https://github.com/mhahsler/arulespy/releases/tag/arulespy_0.1.0
