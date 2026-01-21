# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Unreleased]
### Added
- [issues/108](https://github.com/podaac/bignbit/issues/108): Handle case when no data is returned from a Harmony job by throwing a warning that can be tracked in CloudWatch logs.
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.6.0]
### Added
- [issues/109](https://github.com/podaac/bignbit/issues/109): Handle new format of EDL token expiration datetime, also backwards compatible with old date format.
### Changed
### Deprecated
### Removed
### Fixed
- [issues/138](https://github.com/podaac/bignbit/issues/138): Fix key error when building image sets from OPERA HLS imagery.
### Security

## [0.5.0]
### Added
### Changed
### Deprecated
### Removed
### Fixed
- [issues/127](https://github.com/podaac/bignbit/issues/127): Additional hotfix to allow for deployment in PODAAC environments with their version of cumulus
- [features/old_null](https://github.com/podaac/bignbit/pull/134) Updated null provider version to > 2.1 for PODAAC cumulus compatibility
### Security

## [0.4.1]
### Added
- [issues/97](https://github.com/podaac/bignbit/issues/97): Added the "bignbit" label to all `harmony-py` requests.
### Changed
### Deprecated
### Removed
### Fixed
- [issues/127](https://github.com/podaac/bignbit/issues/127): Merged 0.4.0 changes into develop, updated harmony-py version, fixed conflict in terraform lock file.
### Security

## [0.4.0]
### Added
- [issues/69](https://github.com/podaac/bignbit/issues/69): Added support for other projections, with the default being EPSG:4326. The projection is read from the `outputCrs` keyword in the dataset config. This likely needs refinement to account for cases when we have multiple projections per dataset.
- [issues/116](https://github.com/podaac/bignbit/issues/116): As part of the new projection support, it was necessary to add in a `scaleExtent` parameter for polar projected browse images. The dataset configuration file now supports a `scaleExtentPolar` keyword which is a list of four numbers specifying geographic bounds on the EPSG:3413 or EPSG:3031 outputs. This keyword only works if one of those projections is listed in the `outputCrs` keyword. If `scaleExtentPolar` is not specified, bounds are set to a default value used by GIBS ([-4194303, -4194303, 4194303, 4194303], technically this is 1m less than the bound, but this was done intentionally to avoid precision errors).
### Changed
- [issues/62](https://github.com/podaac/bignbit/issues/62): The retry policy for querying Harmony job status is now configurable as module parameters. By default, it will query for job status every 20 seconds for a maximum of 15 attempts.
### Deprecated
### Removed
### Fixed
- [issues/91](https://github.com/podaac/bignbit/issues/91): Fixed bug where the CNM collection name sent to GIBS included '/' characters when dealing with certain variables. This caused processing errors in GIBS, all collection names will now replace '/' with '_' before being sent to GIBS.
- [issues/89](https://github.com/podaac/bignbit/issues/89): Fixed bug where querying CMR for a collection could result in multiple results because collection version was not included in the query. Fix is to include the version in the CMR query, which will now return only one result.
- [issues/96](https://github.com/podaac/bignbit/issues/96): Fixed bug causing GIBS responses to fail processing due to provider name containing an underscore `_` which collided with the delimiter used in CNM identifiers. The new delimiter for CNM identifier is now an exclamation mark `!`.
- [issues/113](https://github.com/podaac/bignbit/issues/113): Height and width are now optional in the dataset configuration file. If not provided, the height and width will not be passed to harmony and will be determined automatically.
### Security

## [0.3.0]
### Added
- [issues/59](https://github.com/podaac/bignbit/issues/59): A new pair of keywords (`dataDayStrategy` and `singleDayNumber`) have been added to the DatasetConfiguration for BIG to enable proper image metadata for annual products. These keywords allow a dataset to override the umm-g date info.
- [issues/84](https://github.com/podaac/bignbit/issues/84): New parameter in dataset config `subdaily` that sends DataDateTime to GIBS instead of DataDay.
- Added optional `concept_id` keyword to dataset config to provide an override for finding the proper CMR collection concept ID when testing.
### Changed
### Deprecated
### Removed
### Fixed
- [issues/82](https://github.com/podaac/bignbit/issues/82): Fixed date parsing bug where ISO-8601 format dates, the default for UMM-G, were not handled properly.
- Update gibs_response_queue visibility timeout to match aws_lambda_function handle_gitc_response timeout
### Security

## [0.2.4]
### Added
- [issues/71](https://github.com/podaac/bignbit/issues/71): New module parameter `cmr_environment` is used to determine which environment to use for CMR requests when processing GIBS responses.
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
