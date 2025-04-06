# Changelog

All notable changes to the Secure Eraser project will be documented in this file.

## [v1.0.0] - 2025-04-06

### Added
- Flask web interface for demonstrating secure erasure functionality
- Bootstrap dark theme styling for better visual experience
- Interactive demo page for secure file erasure testing
- Command help page displaying all available CLI options
- Unique report file names generated using UUIDs
- Automatic cleanup for temporary files after use
- Proper error handling for visualization dependencies

### Fixed
- HTML report generation with proper Jinja2 template handling
- Template rendering issue with dict.items() conflict
- Serialization of datetime objects in JSON reports
- Chart generation with correct BytesIO handling
- Dependency issue with matplotlib visualization components

### Improved
- Enhanced error handling throughout the application
- More secure temp file naming conventions
- Better fallback templates when visualization fails
- Improved type hints with Union types for better type checking
- Cleaner project structure with test file removal

### Security
- More secure handling of temp files during operations
- Better cleanup of sensitive data after operations
- Improved verification report signing mechanism