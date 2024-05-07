# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.3.0]

### Added
* Compilation of the `back-processing` code to the Dockerfile.
* CPU-based workflow for back-projecting level-0 Sentinel-1 data

### Changed
* Compilation script now uses libfftw3f library installed using `apt` instead of locally compiled version.

## [0.2.0]

### Added
* Created a fresh version of the repository using hyp3-cookiecutter.

### Removed
* All the files associated with the pre-2021 work, except the .git folder.

## [0.1.0]

### Added
* All pre-2021 work on the repository.

## [0.0.0]

### Added
* Initial version of repository.

