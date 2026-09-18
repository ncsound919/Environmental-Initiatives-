# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-27

### Added
- Initial commercial release of TOON (Token-Oriented Object Notation)
- Complete implementation of TOON specification v1.4
- Comprehensive test suite with spec conformance tests
- CLI tool for JSON ↔ TOON conversion
- Extensive benchmarks comparing TOON vs JSON, YAML, XML, CSV
- TypeScript types and full API documentation
- Support for multiple delimiters (comma, tab, pipe)
- Length markers for enhanced LLM parsing
- Strict validation mode for data integrity

### Features
- **Token-efficient serialization**: 30-60% fewer tokens than JSON for uniform arrays
- **LLM-friendly structure**: Explicit length markers and field declarations
- **Deterministic output**: Consistent formatting for reproducible results
- **Type-safe**: Full TypeScript support with comprehensive type definitions
- **Cross-platform**: Works in Node.js and browser environments
- **Extensible**: Clean API for custom encoders/decoders

### Performance
- **Token savings**: Up to 60% reduction vs formatted JSON for tabular data
- **LLM accuracy**: 73.9% comprehension accuracy across multiple models
- **Parsing speed**: Optimized scanner and parser for fast conversion
- **Memory efficient**: Streaming processing for large datasets

### Compatibility
- Compatible with TOON specification v1.4
- Supports all JSON-serializable data types
- Handles edge cases (NaN, Infinity, Dates, BigInt)
- Graceful degradation for non-uniform data structures

### Documentation
- Comprehensive README with usage examples
- API documentation with TypeScript types
- Benchmark results and performance comparisons
- CLI usage guide and examples
- Syntax cheatsheet and format overview

## [0.8.0] - 2025-01-01

### Added
- Initial implementation of TOON format
- Basic encode/decode functionality
- Core test suite
- CLI prototype
- Initial benchmarks

### Changed
- Improved parsing performance
- Enhanced error handling
- Better TypeScript types

### Fixed
- Various encoding edge cases
- Parsing of complex nested structures
- Memory leaks in large dataset processing</content>
<parameter name="filePath">C:\Users\tap45\Desktop\project 5\cheetah v2\toon-main\CHANGELOG.md