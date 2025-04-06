# Changelog

All notable changes to the SecureEraser project will be documented in this file.

## [1.2.0] - 2025-04-06

### Added
- Complete metadata wiping functionality
  - Filename sanitization with random name iterations
  - Timestamp and permission attribute wiping
  - Directory entry cleaning
  - Complete file shredding with `--shred` option
- Enhanced GPU acceleration
  - Improved CUDA kernel for faster wiping
  - Better memory management for large files
  - Automatic fallback to CPU when GPU is unavailable
- Dynamic resource optimization
  - Automatic thread count adjustment based on system load
  - Memory usage optimization with smart buffer management
  - I/O priority handling for background operations
- Advanced job management system
  - Pause/resume for long-running operations
  - Job queue with persistent storage
  - Auto-recovery from interruptions
- Enhanced security features
  - Secure memory handling with memory locking
  - Protection against memory inspection
  - Advanced sanitization of freed memory
- Comprehensive documentation
  - Added 11 detailed markdown files in docs/ directory
  - Complete guide for all features and options
  - Security best practices guide with recommendations

### Changed
- Updated web interface with metadata wiping options
- Extended verification system to cover metadata wiping
- Improved HTML reports with new visualizations for metadata operations
- Enhanced command-line help with examples of metadata wiping
- Refactored core code for better modularity and extensibility
- Updated default security recommendations in documentation

### Fixed
- Fixed memory leak in large file processing
- Improved error handling for permission-related errors
- Enhanced batch processing stability
- Fixed performance issues on limited-resource systems
- Corrected verification hash computation for special files

## [1.1.0] - 2023-04-06

### Added
- Military-grade wiping standards implementation (MilitaryWipingStandards class)
  - NIST SP 800-88 Clear and Purge methods
  - DoD 5220.22-M 3-pass and 7-pass methods
  - HMG IS5 Baseline and Enhanced (UK Government)
  - NAVSO P-5239-26 (US Navy)
  - AFSSI-5020 (Air Force)
  - AR 380-19 (Army)
  - CSC-STD-005-85 (NSA)
- Custom wiping patterns functionality
  - Create, use, delete and list custom patterns
  - Support for hex patterns, multi-pass patterns, and pattern generators
  - Pattern generators: random, zeros, ones, alternating, random_complement,
    ascii_noise, fibonacci, counter, random_blocks
  - Save and load custom patterns from config file
- Command-line options for new wiping methods
  - `--method` argument extended with military standards
  - Added `--custom-pattern`, `--create-pattern`, `--pattern-hex`,
    `--delete-pattern`, and `--list-patterns` options
- Better security measures and documentation
  - Updated SECURITY.md with comprehensive security features documentation
  - Better secure memory handling

### Changed
- Enhanced CLI help documentation
- Improved error handling and logging for custom patterns
- Extended verification for all wiping methods
- Updated main web interface demo

### Fixed
- Fixed several bugs in the verification module
- Fixed race condition in parallel directory processing
- Improved cleanup of temporary files

## [1.0.0] - 2023-01-15

### Added
- Initial release with core secure deletion functionality
- Multiple wiping methods: standard, DoD, Gutmann, and paranoid
- File, directory, and free space wiping capabilities
- Cryptographic verification with multiple hash algorithms
- HTML, PDF, and JSON report generation
- Visualization of wiping operations in HTML reports
- Command-line interface with comprehensive options
- Basic web interface demo
- Performance optimizations