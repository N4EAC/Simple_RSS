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

Simple RSS identifies itself honestly as an RSS/Atom reader. It does not automatically send an email address or a fictitious `From` header. A contact address is sent only after the user explicitly enters one in Setup. This may be required by providers such as local government etcetera, keeping it compliant and legal.

Conditional requests reduce unnecessary downloads. When a server returns `304 Not Modified`, the existing feed remains displayed. When a server supplies a numeric `Retry-After` value with HTTP 429 or 503, Simple RSS delays the next request accordingly.


## Feed navigation

The five feed entries remain inside a clipped viewport. Use the mouse wheel, touchpad, Page Up/Page Down, Home, or End to scroll long entries. No scrollbar is displayed (that is intentional).

## RSS Feed Sites for Amateur Radio

Below are 10 of the best RSS feeds for amateur radio news, selected to provide broad coverage of the **United States, United Kingdom, Brazil, France, Japan**, plus important international DX and satellite news. These are all well-established sources with active or regularly maintained feeds. ([RSS Database - FeedSpot][1])

| #  | Country          | Source                              | RSS Feed URL                                                                   |
| -- | ---------------- | ----------------------------------- | ------------------------------------------------------------------------------ |
| 1  | 🇺🇸 USA         | ARRL News                           | [https://www.arrl.org/arrl.rss](https://www.arrl.org/arrl.rss)                 |
| 2  | 🇬🇧 UK          | RSGB News                           | [https://rsgb.org/feed/](https://rsgb.org/feed/)                               |
| 3  | 🇬🇧 UK          | Southgate Amateur Radio News        | [https://www.southgatearc.org/sarc.rss](https://www.southgatearc.org/sarc.rss) |
| 4  | 🇧🇷 Brazil      | LABRE News                          | [https://www.labre.org.br/feed/](https://www.labre.org.br/feed/)               |
| 5  | 🇫🇷 France      | REF (Réseau des Émetteurs Français) | [https://www.r-e-f.org/feed/](https://www.r-e-f.org/feed/)                     |
| 6  | 🇯🇵 Japan       | JARL News                           | [https://www.jarl.org/English/rss.xml](https://www.jarl.org/English/rss.xml)   |
| 7  | 🌍 International | IARU Region 1 News                  | [https://www.iaru-r1.org/feed/](https://www.iaru-r1.org/feed/)                 |
| 8  | 🌍 International | AMSAT News                          | [https://www.amsat.org/feed/](https://www.amsat.org/feed/)                     |
| 9  | 🌍 International | AmateurRadio.com                    | [https://www.amateurradio.com/feed/](https://www.amateurradio.com/feed/)       |
| 10 | 🌍 International | SWLing Post                         | [https://swling.com/blog/feed/](https://swling.com/blog/feed/)                 |

### Best combination for a desktop RSS reader

If you only subscribe to a handful, I'd recommend these:

* ARRL (US)
* RSGB (UK)
* Southgate ARC (international/DX)
* LABRE (Brazil)
* REF (France)
* JARL (Japan)
* AMSAT
* AmateurRadio.com
* IARU Region 1
* SWLing Post

This mix gives excellent coverage of:

* Regulatory news
* HF/VHF/UHF operating
* DXpeditions
* Contesting
* Satellites
* Emergency communications
* Digital modes
* Equipment reviews
* Club news
* International amateur radio developments

These feeds are among the most commonly referenced by amateur-radio RSS aggregators and club news services. ([hampager.de][2])

[1]: https://rss.feedspot.com/ham_radio_rss_feeds/?utm_source=chatgpt.com "Top 60 Ham Radio RSS Feeds"
[2]: https://hampager.de/dokuwiki/doku.php?id=usecaseclubnews&utm_source=chatgpt.com "usecaseclubnews [DAPNET DokuWiki]"

