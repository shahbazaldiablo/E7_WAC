# Changelog

## [0.9.1] - 2026-09-25

### Fixed
- Fixed a classification bug where `www.` prefix caused internal links to be incorrectly filed into the `External Links` Excel tab.
- Excel reports now dynamically use the correct crawler version in their filename.

## [0.9.0] - 2026-09-25

### Added
- CMS-Agnostic architecture: Gracefully audits TYPO3, Shopify, Next.js, and standard HTML sites without relying on WordPress assumptions.
- Hreflang extraction: Natively parses `<link rel="alternate" hreflang="...">` for multilingual site validation.
- Intelligent CMS Fingerprinting: Detects and logs the underlying generator/CMS into the scan metadata.
- Support for `<base href="...">` and `<area href="...">` URL resolutions.

### Fixed
- Relative URLs are now safely resolved against the document's `<base>` tag rather than the current URL path.
- Import error for `is_same_domain` in `crawler.py` causing NameErrors in Phase 2.

## [0.8.0] - 2026-08-18

### Added
- Modular project architecture (`e7wac/` package)
- CLI audit modes (`--mode [full|images|links|seo|technical|content]`)
- Targeted Image URL Audit mode for CSS background parsing and staging detection
- Configurable crawler settings (`--workers`, `--timeout`, etc.)
- Scan metadata in SQLite
- Severity classification dynamically assigned to issues

### Improved
- ETA calculation now avoids huge initial spikes and uses mode-specific progress
- Sitemap classification
- Safe pause/resume logic

### Changed
- Stable crawler filename (`website_audit_crawler.py` without version suffix)
- Project repository restructured to `E7_WAC`
