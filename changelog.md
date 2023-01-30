# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- add `type` parameter into `md.persistence.LoadInterface` methods
- add recursion protection implementation in `md.persistence.DefaultImport`
- add unit tests

## [0.2.0] - 2023-01-30
### Added

- Added for `md.persistence.LoadException` few reason codes (and related constructors):  
  - `PARSE_ERROR`
  - `NOT_SUPPORTED`
  - `REQUIREMENT_MISSED`

## [0.1.1] - 2023-01-30
### Fix

- Dependency `md.python.dict` requirement switched from `0.*` to `1.*` version.

## [0.1.0] - 2023-01-29

- Initial implementation

[0.2.0]: https://github.com/md-py/md.persistence/releases/tag/0.2.0
[0.1.1]: https://github.com/md-py/md.persistence/releases/tag/0.1.1
[0.1.0]: https://github.com/md-py/md.persistence/releases/tag/0.1.0
