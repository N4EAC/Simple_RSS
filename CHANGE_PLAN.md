# Simple RSS change plan

This checklist tracks the version 1.5 reliability, compatibility, interface, packaging, and maintenance work.

## Completed — highest-priority upgrades

- [x] Add native macOS application and DMG packaging alongside the Windows build and installer.
- [x] Add unlimited Saved Feeds memory with automatic feed-name labels and feed deletion.
- [x] Add an optional per-feed stale-update alert with escalating visual thresholds.
- [x] Add theme-aware Unix-inspired window chrome and resizing behavior to Windows.
- [x] Improve RSS and Atom compatibility for alternate links, relative URLs, timestamps, and missing item links.
- [x] Strengthen network handling with response validation, a hard download-size limit, conditional requests, and complete `Retry-After` support.

## Completed — reliability and corrections

- [x] Deliver background network results through a thread-safe UI queue.
- [x] Restrict opened entry links to safe absolute HTTP(S) addresses.
- [x] Use structured HTML parsing when cleaning feed summaries.
- [x] Bundle a trusted CA store while keeping HTTPS verification enabled.
- [x] Recover settings independently and report repaired preferences without losing valid saved data.
- [x] Correct historical feed timestamp handling on Windows.
- [x] Correct visual seams and resizing glitches around the Windows custom frame.
- [x] Show extracted feed names instead of long URLs in saved-feed and status displays.
- [x] Stabilize the feed-age field width and provide a compact reload countdown.
- [x] Clean up reload interval choices.

## Completed — testing, builds, and distribution

- [x] Add focused automated coverage for networking, parsing, settings, and compatibility behavior.
- [x] Pin the tested PyInstaller version for repeatable builds.
- [x] Update the Windows build script to install dependencies, run tests, build, and launch the application.
- [x] Add a distribution-aware Linux builder for native Ubuntu/Debian `.deb` and Fedora `.rpm` packages.
- [x] Build and validate the version 1.5 AMD64 `.deb` package on Ubuntu 24.
- [x] Build and validate the version 1.5 macOS release artifact.
- [x] Build the version 1.5 Windows installer for platform testing.
- [x] Document unsigned installer warnings for Windows, macOS, and Linux.
- [x] Keep release binaries outside Git for upload as GitHub Release assets.
- [x] Track user testing across Windows, macOS, and Ubuntu; all reported tests currently pass.

## Remaining candidates

- [ ] Fix the missing Ubuntu taskbar/dock icon in a future update by assigning a unique application window class and matching `StartupWMClass` in the Linux desktop launcher. Apply the fix to both `.deb` and `.rpm` packaging; Fedora may share the issue because it uses the same launcher configuration. Verify on Ubuntu and Fedora when available.
- [ ] Split the UI, feed parsing, networking, settings, and themes into separate modules.
- [ ] Evaluate a non-administrator, per-user Windows installer mode.
- [ ] Build and validate the version 1.5 `.rpm` package on Fedora at a later time; this is deferred and is not an immediate release blocker.
- [ ] Complete final Windows installation and launch validation for the version 1.5 installer.
- [ ] Prepare the final version 1.5 Git commit, tag, checksums, release notes, and GitHub Release assets.
