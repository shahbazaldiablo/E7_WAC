# Changelog

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
