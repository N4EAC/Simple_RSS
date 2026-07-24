# Simple RSS 1.4.2
<img width="1004" height="705" alt="image" src="https://github.com/user-attachments/assets/7f5bfc21-9d2e-46ad-89e2-bdbf0be82eb7" />

A compact Windows desktop RSS/Atom reader with selectable visual themes.

## Features

- User-configurable RSS or Atom feed URL through **SETUP**
- Shows only the five newest entries, with the latest item first
- Every feed update is clickable and opens in the Windows default browser
- Displays the feed-age delta beside the live date/time, based on the newest entry timestamp—not the last reload
- User-selectable reload intervals: 10 seconds, 15 seconds, 30 seconds, 60 seconds, 1 minute, 5 minutes, or 10 minutes
- Tiny white LED flashes during the final five seconds before each reload
- Canvas-rendered dot-matrix date, time, and feed-age display; no external digital font is required
- Honest `SimpleRSS` HTTP User-Agent rather than deceptive browser impersonation
- Optional contact email, transmitted only when the user enters one
- Conditional HTTP requests using ETag and Last-Modified when supported
- Respects server Retry-After instructions for HTTP 429 and 503 responses
- Six selectable themes: Neon Dark, Beige Simple, Red Dark, Blue Medic, Orange, and Gray 95
- Setup dropdown controls and their expanded menus match the active theme
- Windows title bar follows the user’s Windows light/dark application theme
- Embedded application icon for the window, taskbar, executable, shortcuts, and installer
- Feed URL, optional contact email, reload interval, selected theme, and window geometry are remembered locally
- No telemetry, analytics, tracking, or runtime Python packages

## Run from source

1. Install Python 3.11 or newer for Windows.
2. Double-click `simple_rss.py`, or run `py simple_rss.py`.

## Build the standalone EXE

Double-click `build_exe.bat`. The finished executable is created as:

`dist\Simple RSS.exe`

## Build the installer

1. Build the EXE first.
2. Install Inno Setup 6.
3. Open `Simple_RSS.iss`.
4. Compile the script.

The installer is created in the `installer` folder and installs under `C:\Program Files\Simple RSS` with administrator privileges.

## Compliance and privacy

Simple RSS identifies itself honestly as an RSS/Atom reader. It does not automatically send an email address or a fictitious `From` header. A contact address is sent only after the user explicitly enters one in Setup. This may be required by providers such as SEC.gov.

Conditional requests reduce unnecessary downloads. When a server returns `304 Not Modified`, the existing feed remains displayed. When a server supplies a numeric `Retry-After` value with HTTP 429 or 503, Simple RSS delays the next request accordingly.

The footer displays `Simple RSS - Legal & Compliant version 1.4.2`.


## Feed navigation

The five feed entries remain inside a clipped viewport. Use the mouse wheel, touchpad, Page Up/Page Down, Home, or End to scroll long entries. No scrollbar is displayed. The footer remains visible at all times.
