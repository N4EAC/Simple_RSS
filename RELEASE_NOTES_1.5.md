# Simple RSS 1.5 — Draft release notes

## New

- Added native macOS application and DMG builds alongside Windows releases.
- Added automatic Linux packaging for Ubuntu/Debian `.deb` and Fedora `.rpm` releases.
- Added unlimited Saved Feeds memory with automatically extracted feed names and deletion support.
- Added an optional per-feed stale-update LED: amber after 5 minutes, red after 10 minutes, and faster red blinking after 15 minutes.
- Added theme-aware Unix-inspired custom window chrome for Windows.

## Changed

- The main status bar now shows the feed title instead of the full URL.
- Simplified the reload indicator to an LED and countdown without the `RELOAD` label.
- Stabilized the feed-age display at a fixed width.
- Updated footer text to `Simple RSS version 1.5`.
- Added explicit documentation for unsigned Windows, macOS, and Linux release warnings.

## Fixed

- Enforced the 5 MB response limit by detecting data beyond the limit instead of parsing a silently truncated document.
- Added clear errors for HTML pages and other non-feed responses returned with successful HTTP status codes.
- Preferred Atom article (`rel="alternate"`) links, resolved relative and `xml:base` links, and used RSS permalink GUIDs when an item link is absent.
- Recognized additional common entry date fields while preserving source order for undated entries.
- Supported both numeric and HTTP-date forms of the HTTP `Retry-After` header.
- Recovered settings field by field so one invalid value no longer discards valid feeds and preferences; repaired fields are now reported to the user.
- Bundled a trusted CA certificate store to prevent missing-issuer SSL errors in standalone builds without disabling certificate verification.
- Corrected feed-age handling for historical timestamps on Windows.
- Removed bright native resize-frame seams from the Windows custom title bar.

## Distribution

- Windows, macOS, and Linux release artifacts remain outside Git and will be uploaded only as GitHub Release assets.
- The AMD64 Debian package has been successfully tested on Ubuntu 24.
- Fedora `.rpm` package validation is planned for a later time.
- Release artifacts are not Developer ID, Authenticode, or Linux distribution-key signed and may trigger platform trust warnings.
