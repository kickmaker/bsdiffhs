# Change Log
All notable changes to this project will be documented in this file.
Release available on [PyPI](https://pypi.org/project/bsdiffhs/)
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [0.3.0] - 2023-10-13

### Added

### Changed

 - change write_patch and read_patch in format.py to fit our implementation of bsdiff algo :
    - header :
        - 8 bytes for magic "BSDIFFHS"
        - 8 bytes for the length of the target firmware
    - content :
        - 24 bytes to decompress for control data (ctrl[0] = diff, ctrl[1] = extra, ctrl[2] = offset)
        - ctrl[0] bytes to decompress
        - ctrl[1] bytes to decompress
        - do the 3 previous steps until all the patch is read
 
### Fixed

## [0.2.0] - 2023-09-30

### Added

- add window_sz2 and lookahead_sz2 heatshrink parameters for compression/decompression
- add test for supported range parameters

### Changed
 
### Fixed
 
## [0.1.0] - 2022-08-23
 
### Added

- Initial commit
   
### Changed
 
### Fixed