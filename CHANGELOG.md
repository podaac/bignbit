# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed
- [issues/71](https://github.com/podaac/bignbit/issues/71): Increased timeout of the handle_gitc_response lambda function from 15 seconds to 45 seconds.
- [issues/68](https://github.com/podaac/bignbit/issues/68): Fixed bug that was causing excessive size of output state object from the TransferImageSet map step.
- [issues/60](https://github.com/podaac/bignbit/issues/60): Fixed bug causing GIBS responses to fail processing in OPS due to a case-sensitive comparison of environment name.
- [issues/65](https://github.com/podaac/bignbit/issues/65): Fixed bug when input CMA message does not contain `cmrConceptId` by parsing the concept ID from the `cmrLink` instead.
### Security

## [0.2.3]
### Added
### Changed
- [issues/55](https://github.com/podaac/bignbit/issues/55): Harmony client changed from per request and instead will be cached as global variable and will not validate auth credentials on initialization.
### Deprecated
### Removed
### Fixed
- [issues/54](https://github.com/podaac/bignbit/issues/54): Fixed bug where status was not being reported to Cumulus Dashboard by adding `cumulus_meta` back into the output CMA.
### Security

## [0.2.2]
### Added
### Changed
- Lowered required version of hashicorp/null to ~> 2.1 to be compatible with the requirements of cumulus core
### Deprecated
### Removed
### Fixed
### Security

## [0.2.1]
### Added
### Changed
### Deprecated
### Removed
### Fixed
- [issues/50](https://github.com/podaac/bignbit/issues/50): Fixed bug where `count` is unsupported for bignbit by inheriting the AWS provider config from the root module
### Security

## [0.2.0]
### Added
- [issues/40](https://github.com/podaac/bignbit/issues/40): New message attribute `response_topic_arn` will be added to every message sent to GIBS
- [issues/9](https://github.com/podaac/bignbit/issues/9): Added some documentation for installing as cumulus module
### Changed
- [issues/15](https://github.com/podaac/bignbit/issues/15): Change 'convertToPNG' choice to a generic send to harmony choice
- [issues/16](https://github.com/podaac/bignbit/issues/16): Change apply opera treatment choice and lambda to be specific to HLS
- [issues/23](https://github.com/podaac/bignbit/issues/23): Harmony requests now include `destinationUrl` parameter to place output 
  directly in s3 bucket instead of requiring data to be copied.
- [issues/41](https://github.com/podaac/bignbit/issues/41): Module no longer depends on deprecated hashicorp/template provider
- [issues/42](https://github.com/podaac/bignbit/issues/42): Terraform version upgraded to v1.5.3
- Default values for `config_dir` and `bignbit_audit_path` have changed to `big-config` and `bignbit-cnm-output` respectively
### Deprecated 
### Removed
- [issues/7](https://github.com/podaac/bignbit/issues/15): Remove the wait for GITC response
- [issues/23](https://github.com/podaac/bignbit/issues/23): Removed `lambda_role` module variable. The lambda role is now created as part of the module, `permissions_boundary_arn` is required instead.
### Fixed
- [issues/36](https://github.com/podaac/bignbit/issues/36): Support datetimes without microseconds
### Security


## [0.1.2]
### Added
### Changed
- BIG terraform failing in SWOT venues due to long function(lambda) names
### Deprecated
### Removed
### Fixed
### Security


## [0.1.1]
### Added 
- [issues/2](https://github.com/podaac/bignbit/issues/2): Create github action pipeline to build artifacts
- [issues/3](https://github.com/podaac/bignbit/issues/3): Update terraform mock deployment of cumulus module to services accounts
- Initial port from JPL GHE to public GitHub.com
### Changed
- [issues/10](https://github.com/podaac/bignbit/issues/10): Move combined big and pobit state machine into terraform module
- [issues/6](https://github.com/podaac/bignbit/issues/6): BIG terraform failing in SWOT venues due to long lambda name
### Deprecated
### Removed
### Fixed
### Security
