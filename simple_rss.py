import json
import math
import os
import queue
import re
import ssl
import sys
import threading
import time
import tkinter as tk
import ctypes
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from tkinter import messagebox, ttk
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET
import webbrowser

import certifi

APP_NAME = "Simple RSS"
APP_VERSION = "1.5"
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
PLATFORM_NAME = "macOS" if IS_MACOS else ("Windows" if IS_WINDOWS else "Desktop")
UI_FONT = "Segoe UI" if IS_WINDOWS else ("Helvetica Neue" if IS_MACOS else "TkDefaultFont")
MONO_FONT = "Consolas" if IS_WINDOWS else ("Menlo" if IS_MACOS else "TkFixedFont")
LINK_CURSOR = "pointinghand" if IS_MACOS else "hand2"
DEFAULT_REFRESH_SECONDS = 15
REFRESH_OPTIONS = [
    ("10 seconds", 10),
    ("15 seconds", 15),
    ("30 seconds", 30),
    ("1 minute", 60),
    ("5 minutes", 300),
    ("10 minutes", 600),
]
MAX_ITEMS = 5
MAX_FEED_BYTES = 5_000_000
FEED_DELTA_DISPLAY_CHARS = 15
STALE_WARNING_COLOR = "#ffb000"
STALE_CRITICAL_COLOR = "#ff3b30"
APP_USER_AGENT = f"SimpleRSS/{APP_VERSION} ({PLATFORM_NAME}; RSS/Atom reader)"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

THEMES = {
    "Neon Dark": {
        "window": "#06020d", "header": "#0b0315", "status": "#120721",
        "panel": "#030407", "panel_border": "#33414d", "feed_bg": "#06020d",
        "card": "#0d0618", "card_latest": "#120822", "card_border": "#43206d",
        "accent": "#00f7ff", "accent2": "#ff4de1", "accent3": "#b887ff",
        "button": "#5b18a8", "button_active": "#7c2de0", "button_text": "#ffffff",
        "text": "#ffffff", "muted": "#bdaed3", "subtle": "#7d8790",
        "entry": "#130923", "entry_border": "#6f2cff", "footer": "#0b0315",
        "footer_text": "#6f5a8e", "clock_date": "#79f9ff", "clock_time": "#ff4de1",
        "delta": "#b887ff", "led_off": "#35303d",
    },
    "Beige Simple": {
        "window": "#e8dcc8", "header": "#f4ead9", "status": "#ded0b8",
        "panel": "#fffaf0", "panel_border": "#9b8a6e", "feed_bg": "#e8dcc8",
        "card": "#f6ecd9", "card_latest": "#fff8e8", "card_border": "#b9a17d",
        "accent": "#6d4c2f", "accent2": "#8a3f2a", "accent3": "#70543c",
        "button": "#8c6746", "button_active": "#a57c57", "button_text": "#ffffff",
        "text": "#2b2118", "muted": "#5f5144", "subtle": "#7c6c5b",
        "entry": "#fffdf7", "entry_border": "#9b8a6e", "footer": "#ded0b8",
        "footer_text": "#6f604f", "clock_date": "#5b4634", "clock_time": "#7e3f2a",
        "delta": "#6d4c2f", "led_off": "#a69a89",
    },
    "Red Dark": {
        "window": "#100000", "header": "#1a0000", "status": "#290000",
        "panel": "#080000", "panel_border": "#5e1a1a", "feed_bg": "#100000",
        "card": "#180303", "card_latest": "#220404", "card_border": "#681f1f",
        "accent": "#ff3b30", "accent2": "#ff7b72", "accent3": "#ff9b94",
        "button": "#9e1010", "button_active": "#d32121", "button_text": "#ffffff",
        "text": "#fff5f5", "muted": "#d8a6a6", "subtle": "#a66f6f",
        "entry": "#210606", "entry_border": "#7a2222", "footer": "#1a0000",
        "footer_text": "#9b5a5a", "clock_date": "#ff6b61", "clock_time": "#ff3b30",
        "delta": "#ff8f86", "led_off": "#4b2424",
    },
    "Blue Medic": {
        "window": "#03111b", "header": "#062032", "status": "#0a2b42",
        "panel": "#020b11", "panel_border": "#2a5d78", "feed_bg": "#03111b",
        "card": "#071b29", "card_latest": "#0b2638", "card_border": "#1c5877",
        "accent": "#39c6ff", "accent2": "#75e5ff", "accent3": "#76b7dc",
        "button": "#0c6fa3", "button_active": "#1295d4", "button_text": "#ffffff",
        "text": "#f2fbff", "muted": "#a8c9db", "subtle": "#7395a8",
        "entry": "#0b2638", "entry_border": "#1f7fae", "footer": "#062032",
        "footer_text": "#5f91aa", "clock_date": "#4bd4ff", "clock_time": "#8de9ff",
        "delta": "#64c7ef", "led_off": "#284956",
    },
    "Orange": {
        "window": "#130900", "header": "#211000", "status": "#321700",
        "panel": "#090400", "panel_border": "#6f3a0a", "feed_bg": "#130900",
        "card": "#1d0e02", "card_latest": "#281303", "card_border": "#75410f",
        "accent": "#ff9500", "accent2": "#ffb347", "accent3": "#ffc36b",
        "button": "#b85f00", "button_active": "#e77d00", "button_text": "#ffffff",
        "text": "#fff8ef", "muted": "#d7b48e", "subtle": "#a67d54",
        "entry": "#281303", "entry_border": "#8e4b0a", "footer": "#211000",
        "footer_text": "#a76b2d", "clock_date": "#ffad33", "clock_time": "#ff9500",
        "delta": "#ffbd66", "led_off": "#4d3520",
    },
    "Gray 95": {
        "window": "#2c2c2c", "header": "#383838", "status": "#444444",
        "panel": "#1f1f1f", "panel_border": "#707070", "feed_bg": "#2c2c2c",
        "card": "#363636", "card_latest": "#404040", "card_border": "#696969",
        "accent": "#f0f0f0", "accent2": "#d0d0d0", "accent3": "#b8b8b8",
        "button": "#606060", "button_active": "#777777", "button_text": "#ffffff",
        "text": "#f5f5f5", "muted": "#c8c8c8", "subtle": "#a0a0a0",
        "entry": "#3a3a3a", "entry_border": "#777777", "footer": "#383838",
        "footer_text": "#b0b0b0", "clock_date": "#f2f2f2", "clock_time": "#d7d7d7",
        "delta": "#c7c7c7", "led_off": "#666666",
    },
}
DEFAULT_THEME = "Neon Dark"


DOT_MATRIX = {
    "0": ("01110","10001","10011","10101","11001","10001","01110"),
    "1": ("00100","01100","00100","00100","00100","00100","01110"),
    "2": ("01110","10001","00001","00010","00100","01000","11111"),
    "3": ("11110","00001","00001","01110","00001","00001","11110"),
    "4": ("00010","00110","01010","10010","11111","00010","00010"),
    "5": ("11111","10000","10000","11110","00001","00001","11110"),
    "6": ("01110","10000","10000","11110","10001","10001","01110"),
    "7": ("11111","00001","00010","00100","01000","01000","01000"),
    "8": ("01110","10001","10001","01110","10001","10001","01110"),
    "9": ("01110","10001","10001","01111","00001","00001","01110"),
    ":": ("00000","00100","00100","00000","00100","00100","00000"),
    "-": ("00000","00000","00000","11111","00000","00000","00000"),
    " ": ("00000",)*7,
    "A": ("01110","10001","10001","11111","10001","10001","10001"),
    "B": ("11110","10001","10001","11110","10001","10001","11110"),
    "C": ("01111","10000","10000","10000","10000","10000","01111"),
    "D": ("11110","10001","10001","10001","10001","10001","11110"),
    "E": ("11111","10000","10000","11110","10000","10000","11111"),
    "F": ("11111","10000","10000","11110","10000","10000","10000"),
    "G": ("01111","10000","10000","10111","10001","10001","01111"),
    "H": ("10001","10001","10001","11111","10001","10001","10001"),
    "I": ("01110","00100","00100","00100","00100","00100","01110"),
    "J": ("00001","00001","00001","00001","10001","10001","01110"),
    "K": ("10001","10010","10100","11000","10100","10010","10001"),
    "L": ("10000","10000","10000","10000","10000","10000","11111"),
    "M": ("10001","11011","10101","10101","10001","10001","10001"),
    "N": ("10001","11001","10101","10011","10001","10001","10001"),
    "O": ("01110","10001","10001","10001","10001","10001","01110"),
    "P": ("11110","10001","10001","11110","10000","10000","10000"),
    "Q": ("01110","10001","10001","10001","10101","10010","01101"),
    "R": ("11110","10001","10001","11110","10100","10010","10001"),
    "S": ("01111","10000","10000","01110","00001","00001","11110"),
    "T": ("11111","00100","00100","00100","00100","00100","00100"),
    "U": ("10001","10001","10001","10001","10001","10001","01110"),
    "V": ("10001","10001","10001","10001","10001","01010","00100"),
    "W": ("10001","10001","10001","10101","10101","11011","10001"),
    "X": ("10001","10001","01010","00100","01010","10001","10001"),
    "Y": ("10001","10001","01010","00100","00100","00100","00100"),
    "Z": ("11111","00001","00010","00100","01000","10000","11111"),
    ".": ("00000","00000","00000","00000","00000","00100","00100"),
}


class DotMatrixDisplay(tk.Canvas):
    """Canvas-rendered dot-matrix display with no external font dependency."""
    def __init__(self, parent, text="", dot=3, gap=1, char_gap=4,
                 color="#79f9ff", fixed_chars=None, **kwargs):
        self.dot = dot
        self.gap = gap
        self.char_gap = char_gap
        self.dot_color = color
        self.fixed_chars = fixed_chars
        self.value = text
        super().__init__(parent, bg=kwargs.pop("bg", "#030407"), highlightthickness=0, **kwargs)
        self.bind("<Configure>", lambda _e: self.redraw())
        self.redraw()

    def set(self, text):
        if text != self.value:
            self.value = text
            self.redraw()

    def redraw(self):
        self.delete("all")
        x = 2
        y = 2
        step = self.dot + self.gap
        for ch in self.value:
            pattern = DOT_MATRIX.get(ch, DOT_MATRIX[" "])
            for row, bits in enumerate(pattern):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        x0 = x + col * step
                        y0 = y + row * step
                        self.create_oval(x0, y0, x0+self.dot, y0+self.dot, fill=self.dot_color, outline="")
            x += 5 * step + self.char_gap
        rendered_width = x + 2
        if self.fixed_chars is not None:
            rendered_width = 4 + self.fixed_chars * (5 * step + self.char_gap)
        width = max(1, rendered_width)
        height = 7 * step + 4
        self.configure(width=width, height=height, scrollregion=(0,0,width,height))


class ThemedButton(tk.Label):
    """Flat button whose colors remain controllable on macOS Aqua Tk."""

    def __init__(self, parent, command, activebackground, activeforeground, **kwargs):
        self.command = command
        self.normal_background = kwargs.get("bg")
        self.normal_foreground = kwargs.get("fg")
        self.active_background = activebackground
        self.active_foreground = activeforeground
        kwargs.setdefault("cursor", LINK_CURSOR)
        kwargs.setdefault("takefocus", True)
        kwargs.setdefault("bd", 0)
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", self._activate)
        self.bind("<Leave>", self._deactivate)
        self.bind("<ButtonRelease-1>", self._invoke)
        self.bind("<Return>", self._invoke)
        self.bind("<space>", self._invoke)

    def _activate(self, _event=None):
        self.configure(bg=self.active_background, fg=self.active_foreground)

    def _deactivate(self, _event=None):
        self.configure(bg=self.normal_background, fg=self.normal_foreground)

    def _invoke(self, _event=None):
        self.command()
        return "break"


def resource_path(filename: str) -> str:
    """Return a bundled resource path for source and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def windows_hwnd(window):
    """Return the native top-level HWND without truncating it on 64-bit Windows."""
    user32 = ctypes.windll.user32
    user32.GetParent.argtypes = [ctypes.c_void_p]
    user32.GetParent.restype = ctypes.c_void_p
    return user32.GetParent(ctypes.c_void_p(window.winfo_id()))


def configure_windows_identity(window: tk.Tk) -> None:
    """Set the app identity and window/taskbar icon on Windows."""
    try:
        if IS_WINDOWS:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "Eduardo.SimpleRSS.1.5"
            )
        ico_path = resource_path("simple_rss.ico")
        png_path = resource_path("simple_rss.png")
        if IS_WINDOWS and os.path.exists(ico_path):
            window.iconbitmap(default=ico_path)
        if os.path.exists(png_path):
            icon_image = tk.PhotoImage(file=png_path)
            window.iconphoto(True, icon_image)
            window._icon_image = icon_image
    except Exception:
        pass


def app_data_dir() -> str:
    if IS_MACOS:
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        base = os.getenv("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "SimpleRSS")


CONFIG_PATH = os.path.join(app_data_dir(), "settings.json")


class RSSParseError(Exception):
    pass


class FeedResponseError(Exception):
    pass


class TextExtractor(HTMLParser):
    """Turn an HTML fragment into readable plain text."""

    BLOCK_TAGS = {
        "address", "article", "aside", "blockquote", "br", "div", "footer",
        "h1", "h2", "h3", "h4", "h5", "h6", "header", "li", "main", "p",
        "pre", "section", "table", "tr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.suppressed_depth = 0

    def handle_starttag(self, tag, _attrs):
        if tag.lower() in {"script", "style"}:
            self.suppressed_depth += 1
            return
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style"}:
            self.suppressed_depth = max(0, self.suppressed_depth - 1)
            return
        if tag.lower() in self.BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.suppressed_depth:
            self.parts.append(data)

    def text(self):
        return " ".join("".join(self.parts).split())


def local_name(tag: str) -> str:
    return tag.split("}")[-1].lower()


def child_text(node, names):
    wanted = {n.lower() for n in names}
    for child in list(node):
        if local_name(child.tag) in wanted:
            text = "".join(child.itertext()).strip()
            if text:
                return text
    return ""


def parse_date(value: str):
    if not value:
        return None
    value = value.strip()
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone()
    except Exception:
        pass
    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone()
    except Exception:
        return None


def parse_feed_document(xml_bytes: bytes, base_url: str = ""):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise RSSParseError(f"Invalid XML: {exc}") from exc

    feed_title = ""
    if local_name(root.tag) == "feed":
        feed_title = child_text(root, ["title"])
    else:
        channel = next(
            (child for child in list(root) if local_name(child.tag) == "channel"),
            None,
        )
        if channel is not None:
            feed_title = child_text(channel, ["title"])

    document_base = urljoin(base_url, root.attrib.get(
        "{http://www.w3.org/XML/1998/namespace}base", ""
    ))
    entries = []
    for node in root.iter():
        if local_name(node.tag) not in {"item", "entry"}:
            continue

        title = child_text(node, ["title"]) or "Untitled update"
        summary = child_text(node, ["description", "summary", "content"])
        date_text = child_text(
            node, ["pubDate", "published", "updated", "date", "created", "issued"]
        )
        dt = parse_date(date_text)

        link = ""
        link_nodes = [
            child for child in list(node) if local_name(child.tag) == "link"
        ]
        preferred_links = sorted(
            link_nodes,
            key=lambda child: (
                (child.attrib.get("rel") or "alternate").lower() != "alternate",
                (child.attrib.get("type") or "text/html").lower() not in {
                    "text/html", "application/xhtml+xml",
                },
            ),
        )
        for child in preferred_links:
            candidate = (child.attrib.get("href") or (child.text or "")).strip()
            if candidate:
                node_base = urljoin(document_base, node.attrib.get(
                    "{http://www.w3.org/XML/1998/namespace}base", ""
                ))
                link = urljoin(node_base or base_url, candidate)
                break
        if not link:
            for child in list(node):
                if local_name(child.tag) != "guid":
                    continue
                candidate = (child.text or "").strip()
                is_permalink = child.attrib.get("isPermaLink", "true").lower()
                if candidate and is_permalink != "false":
                    link = urljoin(document_base or base_url, candidate)
                    break

        entries.append({
            "title": title,
            "summary": summary,
            "link": link,
            "published": dt,
            "raw_date": date_text,
        })

    if not entries:
        raise RSSParseError("No RSS or Atom entries were found.")

    entries.sort(
        key=lambda item: item["published"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return feed_title, entries[:MAX_ITEMS]


def parse_feed(xml_bytes: bytes, base_url: str = ""):
    """Parse a feed while preserving the original public list-only API."""
    _feed_title, entries = parse_feed_document(xml_bytes, base_url)
    return entries


def validate_feed_response(data: bytes, content_type: str = ""):
    """Reject oversized or clearly non-feed responses with useful errors."""
    if len(data) > MAX_FEED_BYTES:
        raise FeedResponseError(
            f"Feed response exceeds the {MAX_FEED_BYTES // 1_000_000} MB limit."
        )
    normalized_type = (content_type or "").split(";", 1)[0].strip().lower()
    prefix = data.lstrip()[:512].lower()
    looks_html = (
        normalized_type in {"text/html", "application/xhtml+xml"}
        or prefix.startswith(b"<!doctype html")
        or prefix.startswith(b"<html")
    )
    if looks_html:
        raise FeedResponseError(
            "Server returned an HTML page instead of an RSS or Atom feed."
        )
    xml_type = (
        normalized_type in {
            "application/atom+xml", "application/rss+xml", "application/xml",
            "text/xml", "application/rdf+xml",
        }
        or normalized_type.endswith("+xml")
    )
    looks_xml = prefix.startswith(b"<?xml") or prefix.startswith(
        (b"<rss", b"<feed", b"<rdf:rdf")
    )
    if normalized_type and not xml_type and not looks_xml:
        raise FeedResponseError(
            f"Server returned {normalized_type}, not an RSS or Atom feed."
        )


def parse_retry_after(value: str, now=None):
    """Convert Retry-After seconds or an HTTP date to a nonnegative delay."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return int(value)
    try:
        retry_at = parsedate_to_datetime(value)
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        now = now or datetime.now(timezone.utc)
        return max(0, math.ceil((retry_at - now).total_seconds()))
    except (TypeError, ValueError, OverflowError):
        return None


def is_safe_web_url(value: str) -> bool:
    """Return True only for absolute HTTP(S) links."""
    try:
        parsed = urlsplit(value.strip())
        return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)
    except (AttributeError, TypeError, ValueError):
        return False


def fallback_feed_label(url: str) -> str:
    try:
        return urlsplit(url).hostname or url
    except ValueError:
        return url


def saved_feed_choices(saved_feeds):
    """Map short, unique display names to remembered feed URLs."""
    choices = {}
    label_counts = {}
    for saved_feed in saved_feeds:
        url = saved_feed["url"]
        label = str(saved_feed.get("label") or fallback_feed_label(url)).strip()
        label = label or fallback_feed_label(url)
        label_counts[label] = label_counts.get(label, 0) + 1
        display = label
        if label_counts[label] > 1:
            display = f"{label} ({label_counts[label]})"
        choices[display] = url
    return choices


def stale_feed_alert(feed_timestamp, enabled: bool, now=None):
    """Return the stale LED color and toggle interval, or None when inactive."""
    if not enabled or feed_timestamp is None:
        return None
    now = now or datetime.now().astimezone()
    if feed_timestamp.tzinfo is None:
        feed_timestamp = feed_timestamp.replace(tzinfo=timezone.utc)
    age_seconds = (now - feed_timestamp).total_seconds()
    if age_seconds < 300:
        return None
    color = STALE_CRITICAL_COLOR if age_seconds >= 600 else STALE_WARNING_COLOR
    toggle_interval = 0.25 if age_seconds >= 900 else 0.5
    return color, toggle_interval


class SetupDialog(tk.Toplevel):
    def __init__(self, parent, current_url: str, current_contact: str,
                 current_refresh_seconds: int, current_theme: str, saved_feeds):
        super().__init__(parent)
        self.title("RSS Setup")
        self.theme_name = current_theme if current_theme in THEMES else DEFAULT_THEME
        self.theme = THEMES[self.theme_name]
        c = self.theme
        self.configure(bg=c["window"])
        self.resizable(False, False)
        self.result = None
        self.contact_result = current_contact
        self.refresh_result = current_refresh_seconds
        self.theme_result = self.theme_name
        self.stale_alert_result = next(
            (
                bool(saved_feed.get("stale_alert", False))
                for saved_feed in saved_feeds
                if saved_feed.get("url") == current_url
            ),
            False,
        )
        self.saved_feeds = [dict(saved_feed) for saved_feed in saved_feeds]
        self.saved_feeds_result = self.saved_feeds
        self.deleted_feed_urls = set()
        self.transient(parent)
        self.grab_set()

        frame = tk.Frame(self, bg=c["window"], padx=22, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="RSS FEED SETUP", bg=c["window"], fg=c["accent"],
            font=(UI_FONT, 15, "bold")
        ).pack(anchor="w", pady=(0, 14))

        self.saved_feed_values = saved_feed_choices(self.saved_feeds)
        if self.saved_feed_values:
            tk.Label(
                frame, text="Saved Feeds", bg=c["window"], fg=c["muted"],
                font=(UI_FONT, 10)
            ).pack(anchor="w")
            saved_feed_row = tk.Frame(frame, bg=c["window"])
            saved_feed_row.pack(fill="x", pady=(6, 8))
            self.saved_feed_var = tk.StringVar()
            self.saved_feed_combo = ttk.Combobox(
                saved_feed_row, textvariable=self.saved_feed_var, state="readonly",
                values=list(self.saved_feed_values), width=43, font=(UI_FONT, 10),
            )
            self.saved_feed_combo.pack(side="left", fill="x", expand=True, ipady=4)
            self.saved_feed_combo.bind("<<ComboboxSelected>>", self.select_saved_feed)
            ThemedButton(
                saved_feed_row, text="DELETE", command=self.delete_saved_feed,
                bg=c["button"], fg=c["text"], activebackground=c["button_active"],
                activeforeground=c["button_text"], relief="flat", padx=12, pady=7,
                font=(UI_FONT, 8, "bold"),
            ).pack(side="left", padx=(8, 0))

        tk.Label(
            frame, text="Feed URL", bg=c["window"], fg=c["muted"],
            font=(UI_FONT, 10)
        ).pack(anchor="w")

        self.url_var = tk.StringVar(value=current_url)
        self.entry = tk.Entry(
            frame, textvariable=self.url_var, width=58,
            bg=c["entry"], fg=c["text"], insertbackground=c["text"],
            relief="flat", highlightthickness=1,
            highlightbackground=c["entry_border"], highlightcolor=c["accent"],
            font=(UI_FONT, 10)
        )
        self.entry.pack(fill="x", ipady=8, pady=(6, 12))
        self.entry.focus_set()
        self.entry.selection_range(0, tk.END)

        self.stale_alert_var = tk.BooleanVar(value=self.stale_alert_result)
        self.stale_alert_by_url = {
            saved_feed["url"]: bool(saved_feed.get("stale_alert", False))
            for saved_feed in self.saved_feeds
        }
        self.url_var.trace_add("write", self.sync_stale_alert_setting)
        tk.Checkbutton(
            frame, text="Enable stale-feed LED (5 / 10 / 15 min)",
            variable=self.stale_alert_var, bg=c["window"], fg=c["muted"],
            activebackground=c["window"], activeforeground=c["text"],
            selectcolor=c["entry"], highlightthickness=0,
            font=(UI_FONT, 9),
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            frame, text="Optional contact email (used only when a provider requires identification)",
            bg=c["window"], fg=c["muted"], font=(UI_FONT, 10)
        ).pack(anchor="w")
        self.contact_var = tk.StringVar(value=current_contact)
        self.contact_entry = tk.Entry(
            frame, textvariable=self.contact_var, width=58,
            bg=c["entry"], fg=c["text"], insertbackground=c["text"],
            relief="flat", highlightthickness=1,
            highlightbackground=c["entry_border"], highlightcolor=c["accent"],
            font=(UI_FONT, 10)
        )
        self.contact_entry.pack(fill="x", ipady=8, pady=(6, 14))

        tk.Label(
            frame, text="Automatic reload interval", bg=c["window"], fg=c["muted"],
            font=(UI_FONT, 10)
        ).pack(anchor="w")
        self.refresh_label_to_seconds = dict(REFRESH_OPTIONS)
        selected_label = next(
            (label for label, seconds in REFRESH_OPTIONS if seconds == current_refresh_seconds),
            "15 seconds",
        )
        self.refresh_var = tk.StringVar(value=selected_label)
        self.refresh_combo = ttk.Combobox(
            frame, textvariable=self.refresh_var, state="readonly",
            values=[label for label, _seconds in REFRESH_OPTIONS], width=55,
            font=(UI_FONT, 10),
        )
        self.refresh_combo.pack(fill="x", ipady=4, pady=(6, 12))

        tk.Label(
            frame, text="Theme", bg=c["window"], fg=c["muted"],
            font=(UI_FONT, 10)
        ).pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.theme_name)
        self.theme_combo = ttk.Combobox(
            frame, textvariable=self.theme_var, state="readonly",
            values=list(THEMES.keys()), width=55, font=(UI_FONT, 10),
        )
        self.theme_combo.pack(fill="x", ipady=4, pady=(6, 16))
        self.configure_combobox_style()

        buttons = tk.Frame(frame, bg=c["window"])
        buttons.pack(fill="x")
        ThemedButton(
            buttons, text="CANCEL", command=self.destroy,
            bg=c["button"], fg=c["muted"], activebackground=c["button_active"],
            activeforeground=c["button_text"], relief="flat", padx=18, pady=7,
            font=(UI_FONT, 9, "bold")
        ).pack(side="right")
        ThemedButton(
            buttons, text="SAVE", command=self.save,
            bg=c["accent"], fg=c["window"], activebackground=c["accent3"],
            activeforeground=c["window"], relief="flat", padx=20, pady=7,
            font=(UI_FONT, 9, "bold")
        ).pack(side="right", padx=(0, 8))

        self.bind("<Return>", lambda _e: self.save())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def configure_combobox_style(self):
        c = self.theme
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "SimpleRSS.TCombobox",
            fieldbackground=c["entry"], background=c["button"],
            foreground=c["text"], arrowcolor=c["text"],
            bordercolor=c["entry_border"], lightcolor=c["entry_border"],
            darkcolor=c["entry_border"], padding=6,
        )
        style.map(
            "SimpleRSS.TCombobox",
            fieldbackground=[("readonly", c["entry"])],
            foreground=[("readonly", c["text"])],
            selectbackground=[("readonly", c["button"])],
            selectforeground=[("readonly", c["button_text"])],
        )
        self.refresh_combo.configure(style="SimpleRSS.TCombobox")
        self.theme_combo.configure(style="SimpleRSS.TCombobox")
        if hasattr(self, "saved_feed_combo"):
            self.saved_feed_combo.configure(style="SimpleRSS.TCombobox")
        self.option_add("*TCombobox*Listbox.background", c["entry"])
        self.option_add("*TCombobox*Listbox.foreground", c["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", c["button"])
        self.option_add("*TCombobox*Listbox.selectForeground", c["button_text"])

    def select_saved_feed(self, _event=None):
        url = self.saved_feed_values.get(self.saved_feed_var.get())
        if url:
            self.url_var.set(url)

    def sync_stale_alert_setting(self, *_args):
        url = self.url_var.get().strip()
        self.stale_alert_var.set(self.stale_alert_by_url.get(url, False))

    def delete_saved_feed(self):
        display = self.saved_feed_var.get()
        url = self.saved_feed_values.get(display)
        if not url:
            messagebox.showinfo(
                "Delete Saved Feed", "Select a saved feed to delete.", parent=self
            )
            return
        if not messagebox.askyesno(
            "Delete Saved Feed",
            f'Remove "{display}" from Saved Feeds?',
            parent=self,
        ):
            return
        self.saved_feeds = [
            saved_feed for saved_feed in self.saved_feeds
            if saved_feed["url"] != url
        ]
        self.deleted_feed_urls.add(url)
        self.saved_feed_values = saved_feed_choices(self.saved_feeds)
        self.saved_feed_combo.configure(values=list(self.saved_feed_values))
        self.saved_feed_var.set("")

    def save(self):
        value = self.url_var.get().strip()
        if not is_safe_web_url(value):
            messagebox.showerror("Invalid URL", "Enter a valid http:// or https:// RSS feed URL.", parent=self)
            return
        contact = self.contact_var.get().strip()
        if contact and ("@" not in contact or "." not in contact.rsplit("@", 1)[-1]):
            messagebox.showerror("Invalid email", "Enter a valid contact email or leave it blank.", parent=self)
            return
        self.result = value
        self.contact_result = contact
        self.refresh_result = self.refresh_label_to_seconds.get(
            self.refresh_var.get(), DEFAULT_REFRESH_SECONDS
        )
        self.theme_result = self.theme_var.get() if self.theme_var.get() in THEMES else DEFAULT_THEME
        self.stale_alert_result = bool(self.stale_alert_var.get())
        self.saved_feeds_result = self.saved_feeds
        self.destroy()


class RSSViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        if IS_WINDOWS:
            self.overrideredirect(True)
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1000x690")
        self.minsize(820, 560)
        self.theme_name = DEFAULT_THEME
        self.theme = THEMES[self.theme_name]
        self.configure(bg=self.theme["window"])
        configure_windows_identity(self)

        self.feed_url = ""
        self.active_feed_title = ""
        self.contact_email = ""
        self.refresh_seconds = DEFAULT_REFRESH_SECONDS
        self.latest_feed_timestamp = None
        self.next_refresh = time.monotonic()
        self.fetching = False
        self.led_state = False
        self.stale_led_state = False
        self.stale_led_last_toggle = 0.0
        self.item_frames = []
        self.etag = ""
        self.last_modified = ""
        self.cached_items = []
        self.backoff_until = 0.0
        self.saved_feeds = []
        self.forgotten_feed_urls = set()
        self.fetch_results = queue.Queue()
        self.settings_warnings = []
        self._is_maximized = False
        self._restore_geometry = ""
        self._drag_offset = (0, 0)
        self._resize_start = None

        self.load_settings()
        self.theme = THEMES.get(self.theme_name, THEMES[DEFAULT_THEME])
        self.configure(bg=self.theme["window"])
        self.build_ui()
        if IS_WINDOWS:
            self.after(0, self.configure_windows_custom_chrome)
        if self.settings_warnings:
            self.after(50, self.show_settings_warnings)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.after(150, self.startup)
        self.after(200, self.tick)

    def build_ui(self):
        c = self.theme
        if IS_WINDOWS:
            self.build_custom_titlebar()
        header = tk.Frame(self, bg=c["header"], height=122)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_wrap = tk.Frame(header, bg=c["header"])
        title_wrap.pack(side="left", fill="y", padx=(22, 14))
        tk.Label(
            title_wrap, text="SIMPLE RSS", bg=c["header"], fg=c["accent"],
            font=(UI_FONT, 23, "bold")
        ).pack(anchor="w", pady=(42, 0))

        # Clock and feed age share one dedicated digital display panel.
        digital_panel = tk.Frame(
            header, bg=c["panel"], highlightthickness=1,
            highlightbackground=c["panel_border"], padx=16, pady=10
        )
        digital_panel.pack(side="left", fill="y", pady=13, padx=(8, 12))

        clock_wrap = tk.Frame(digital_panel, bg=c["panel"])
        clock_wrap.pack(side="left", fill="y")
        self.clock_date_display = DotMatrixDisplay(
            clock_wrap, "0000-00-00", dot=2, gap=1, char_gap=3, color=c["clock_date"], bg=c["panel"]
        )
        self.clock_date_display.pack(anchor="w")
        self.clock_time_display = DotMatrixDisplay(
            clock_wrap, "00:00:00", dot=3, gap=1, char_gap=4, color=c["clock_time"], bg=c["panel"]
        )
        self.clock_time_display.pack(anchor="w", pady=(6, 0))

        divider = tk.Frame(digital_panel, bg=c["panel_border"], width=1)
        divider.pack(side="left", fill="y", padx=18)

        delta_wrap = tk.Frame(digital_panel, bg=c["panel"])
        delta_wrap.pack(side="left", fill="both", expand=True)
        tk.Label(
            delta_wrap, text="FEED LAST UPDATED", bg=c["panel"], fg=c["subtle"],
            font=(MONO_FONT, 8, "bold")
        ).pack(anchor="w", pady=(8, 3))
        self.feed_delta_display = DotMatrixDisplay(
            delta_wrap, "UNKNOWN", dot=2, gap=1, char_gap=3,
            color=c["delta"], fixed_chars=FEED_DELTA_DISPLAY_CHARS, bg=c["panel"]
        )
        self.feed_delta_display.pack(anchor="w", pady=(3, 0))

        controls = tk.Frame(header, bg=c["header"])
        controls.pack(side="right", fill="y", padx=20)

        self.stale_led = tk.Canvas(
            controls, width=10, height=10, bg=c["header"], highlightthickness=0
        )
        self.stale_led.pack(side="left", padx=(0, 4))
        self.stale_led_dot = self.stale_led.create_oval(
            3, 3, 7, 7, fill=c["led_off"], outline="", width=0
        )

        self.led = tk.Canvas(controls, width=10, height=10, bg=c["header"], highlightthickness=0)
        self.led.pack(side="left", padx=(0, 7))
        self.led_dot = self.led.create_oval(3, 3, 7, 7, fill=c["led_off"], outline="", width=0)

        self.countdown_var = tk.StringVar(value="--")
        tk.Label(
            controls, textvariable=self.countdown_var, bg=c["header"], fg=c["muted"],
            font=(MONO_FONT, 10, "bold")
        ).pack(side="left", padx=(0, 14))

        ThemedButton(
            controls, text="SETUP", command=self.open_setup,
            bg=c["button"], fg=c["text"], activebackground=c["button_active"],
            activeforeground=c["button_text"], relief="flat", padx=16, pady=8,
            font=(UI_FONT, 9, "bold")
        ).pack(side="left")

        status_bar = tk.Frame(self, bg=c["status"], height=38)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)

        self.feed_label = tk.Label(
            status_bar, text="NO FEED CONFIGURED", bg=c["status"], fg=c["muted"],
            font=(UI_FONT, 9), anchor="w"
        )
        self.feed_label.pack(side="left", fill="x", expand=True, padx=20)

        self.status_var = tk.StringVar(value="IDLE")
        tk.Label(
            status_bar, textvariable=self.status_var, bg=c["status"], fg=c["accent"],
            font=(MONO_FONT, 9, "bold")
        ).pack(side="right", padx=20)

        body = tk.Frame(self, bg=c["feed_bg"])
        body.pack(fill="both", expand=True, padx=18, pady=12)

        # Scrollable feed viewport without a visible scrollbar. This keeps the
        # footer visible even when five entries contain long summaries.
        self.feed_canvas = tk.Canvas(
            body, bg=c["feed_bg"], highlightthickness=0, bd=0
        )
        self.feed_canvas.pack(fill="both", expand=True)
        self.feed_container = tk.Frame(self.feed_canvas, bg=c["feed_bg"])
        self.feed_window = self.feed_canvas.create_window(
            (0, 0), window=self.feed_container, anchor="nw"
        )
        self.feed_container.bind("<Configure>", self._update_feed_scrollregion)
        self.feed_canvas.bind("<Configure>", self._resize_feed_window)
        self._bind_feed_scrolling(self.feed_canvas)

        self.show_placeholder("Use SETUP to enter an RSS or Atom feed URL.")

        footer = tk.Frame(self, bg=c["footer"], height=30)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        self.footer_var = tk.StringVar()
        self.update_footer_text()
        tk.Label(
            footer, textvariable=self.footer_var,
            bg=c["footer"], fg=c["footer_text"], font=(UI_FONT, 8)
        ).pack(side="left", padx=18)
        if IS_WINDOWS:
            self.build_resize_handles()

    def build_custom_titlebar(self):
        """Draw a compact Unix-inspired title bar for the Windows build."""
        c = self.theme
        bar = tk.Frame(self, bg=c["panel"], height=30)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        motif = tk.Label(
            bar, text="●  ●  ●", bg=c["panel"], fg=c["accent3"],
            font=(UI_FONT, 8), padx=10,
        )
        motif.pack(side="left", fill="y")
        title = tk.Label(
            bar, text=f"{APP_NAME.upper()} {APP_VERSION}",
            bg=c["panel"], fg=c["muted"], font=(MONO_FONT, 9, "bold"),
        )
        title.pack(side="left", fill="y")

        for widget in (bar, motif, title):
            widget.bind("<ButtonPress-1>", self.start_window_drag)
            widget.bind("<B1-Motion>", self.drag_window)
            widget.bind("<Double-Button-1>", self.toggle_maximize)

        ThemedButton(
            bar, text="×", command=self.on_close,
            bg=c["panel"], fg=c["muted"], activebackground="#b3261e",
            activeforeground="#ffffff", padx=12, font=(UI_FONT, 12, "bold"),
        ).pack(side="right", fill="y")
        ThemedButton(
            bar, text="□", command=self.toggle_maximize,
            bg=c["panel"], fg=c["muted"], activebackground=c["button_active"],
            activeforeground=c["button_text"], padx=12, font=(UI_FONT, 10),
        ).pack(side="right", fill="y")
        ThemedButton(
            bar, text="—", command=self.minimize_window,
            bg=c["panel"], fg=c["muted"], activebackground=c["button_active"],
            activeforeground=c["button_text"], padx=12, font=(UI_FONT, 9, "bold"),
        ).pack(side="right", fill="y")

    def configure_windows_custom_chrome(self):
        """Restore taskbar behavior while keeping the native frame hidden."""
        if not IS_WINDOWS:
            return
        try:
            self.update_idletasks()
            user32 = ctypes.windll.user32
            hwnd = windows_hwnd(self)
            get_long = user32.GetWindowLongW
            get_long.argtypes = [ctypes.c_void_p, ctypes.c_int]
            get_long.restype = ctypes.c_long
            set_long = user32.SetWindowLongW
            set_long.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long]
            set_long.restype = ctypes.c_long
            user32.SetWindowPos.argtypes = [
                ctypes.c_void_p, ctypes.c_void_p,
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                ctypes.c_uint,
            ]
            user32.SetWindowPos.restype = ctypes.c_int

            style = get_long(hwnd, -16)
            style |= 0x00020000 | 0x00010000 | 0x00080000
            style &= ~(0x00C00000 | 0x00040000)
            set_long(hwnd, -16, style)

            ex_style = get_long(hwnd, -20)
            ex_style = (ex_style | 0x00040000) & ~0x00000080
            set_long(hwnd, -20, ex_style)
            user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                0x0001 | 0x0002 | 0x0004 | 0x0010 | 0x0020,
            )
        except Exception:
            pass

    def build_resize_handles(self):
        """Provide subtle themed resize targets without a bright Win32 frame."""
        color = self.theme["panel_border"]
        specifications = (
            ("n", {"x": 7, "y": 0, "relwidth": 1.0, "width": -14, "height": 5}, "size_ns"),
            ("s", {"x": 7, "rely": 1.0, "y": -5, "relwidth": 1.0, "width": -14, "height": 5}, "size_ns"),
            ("w", {"x": 0, "y": 7, "width": 5, "relheight": 1.0, "height": -14}, "size_we"),
            ("e", {"relx": 1.0, "x": -5, "y": 7, "width": 5, "relheight": 1.0, "height": -14}, "size_we"),
            ("nw", {"x": 0, "y": 0, "width": 7, "height": 7}, "size_nw_se"),
            ("ne", {"relx": 1.0, "x": -7, "y": 0, "width": 7, "height": 7}, "size_ne_sw"),
            ("sw", {"x": 0, "rely": 1.0, "y": -7, "width": 7, "height": 7}, "size_ne_sw"),
            ("se", {"relx": 1.0, "x": -7, "rely": 1.0, "y": -7, "width": 7, "height": 7}, "size_nw_se"),
        )
        self._resize_handles = []
        for mode, placement, cursor in specifications:
            handle = tk.Frame(self, bg=color, cursor=cursor)
            handle.place(**placement)
            handle.bind(
                "<ButtonPress-1>",
                lambda event, resize_mode=mode: self.start_window_resize(
                    resize_mode, event
                ),
            )
            handle.bind("<B1-Motion>", self.resize_window)
            handle.lift()
            self._resize_handles.append(handle)

    def start_window_resize(self, mode, event):
        if self._is_maximized:
            return "break"
        self._resize_start = (
            mode, event.x_root, event.y_root,
            self.winfo_x(), self.winfo_y(),
            self.winfo_width(), self.winfo_height(),
        )
        return "break"

    def resize_window(self, event):
        if self._is_maximized or not self._resize_start:
            return "break"
        mode, pointer_x, pointer_y, x, y, width, height = self._resize_start
        delta_x = event.x_root - pointer_x
        delta_y = event.y_root - pointer_y
        minimum_width, minimum_height = 820, 560

        if "e" in mode:
            width = max(minimum_width, width + delta_x)
        if "s" in mode:
            height = max(minimum_height, height + delta_y)
        if "w" in mode:
            new_width = max(minimum_width, width - delta_x)
            x += width - new_width
            width = new_width
        if "n" in mode:
            new_height = max(minimum_height, height - delta_y)
            y += height - new_height
            height = new_height

        self.geometry(f"{width}x{height}{x:+d}{y:+d}")
        return "break"

    def start_window_drag(self, event):
        if self._is_maximized:
            return
        self._drag_offset = (
            event.x_root - self.winfo_x(),
            event.y_root - self.winfo_y(),
        )

    def drag_window(self, event):
        if self._is_maximized:
            return
        x = event.x_root - self._drag_offset[0]
        y = event.y_root - self._drag_offset[1]
        self.geometry(f"{x:+d}{y:+d}")

    def minimize_window(self):
        if not IS_WINDOWS:
            self.iconify()
            return
        try:
            user32 = ctypes.windll.user32
            user32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
            user32.ShowWindow.restype = ctypes.c_int
            user32.ShowWindow(windows_hwnd(self), 6)
        except Exception:
            self.iconify()

    def toggle_maximize(self, _event=None):
        if self._is_maximized:
            if self._restore_geometry:
                self.geometry(self._restore_geometry)
            self._is_maximized = False
            return "break"

        self._restore_geometry = self.geometry()
        if IS_WINDOWS:
            class Rect(ctypes.Structure):
                _fields_ = [
                    ("left", ctypes.c_long), ("top", ctypes.c_long),
                    ("right", ctypes.c_long), ("bottom", ctypes.c_long),
                ]

            rect = Rect()
            try:
                user32 = ctypes.windll.user32
                user32.SystemParametersInfoW.argtypes = [
                    ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint
                ]
                user32.SystemParametersInfoW.restype = ctypes.c_int
                user32.SystemParametersInfoW(
                    0x0030, 0, ctypes.byref(rect), 0
                )
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                self.geometry(
                    f"{width}x{height}{rect.left:+d}{rect.top:+d}"
                )
            except Exception:
                self.geometry(
                    f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0"
                )
        else:
            self.state("zoomed")
        self._is_maximized = True
        return "break"


    def _update_feed_scrollregion(self, _event=None):
        if hasattr(self, "feed_canvas"):
            self.feed_canvas.configure(scrollregion=self.feed_canvas.bbox("all"))

    def _resize_feed_window(self, event):
        if hasattr(self, "feed_canvas") and hasattr(self, "feed_window"):
            self.feed_canvas.itemconfigure(self.feed_window, width=event.width)

    def _bind_feed_scrolling(self, widget):
        """Enable wheel, touchpad, and keyboard scrolling with no scrollbar."""
        def on_mousewheel(event):
            delta = getattr(event, "delta", 0)
            if delta:
                steps = -1 * int(delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
                self.feed_canvas.yview_scroll(steps, "units")
            return "break"

        def on_linux_up(_event):
            self.feed_canvas.yview_scroll(-1, "units")
            return "break"

        def on_linux_down(_event):
            self.feed_canvas.yview_scroll(1, "units")
            return "break"

        def bind_tree(node):
            node.bind("<MouseWheel>", on_mousewheel, add="+")
            node.bind("<Button-4>", on_linux_up, add="+")
            node.bind("<Button-5>", on_linux_down, add="+")
            for child in node.winfo_children():
                bind_tree(child)

        bind_tree(widget)
        if not getattr(self, "_feed_keyboard_bound", False):
            self.bind("<Prior>", lambda _e: self.feed_canvas.yview_scroll(-1, "pages"), add="+")
            self.bind("<Next>", lambda _e: self.feed_canvas.yview_scroll(1, "pages"), add="+")
            self.bind("<Home>", lambda _e: self.feed_canvas.yview_moveto(0), add="+")
            self.bind("<End>", lambda _e: self.feed_canvas.yview_moveto(1), add="+")
            self._feed_keyboard_bound = True

    def rebuild_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(bg=self.theme["window"])
        self.build_ui()
        self.update_feed_label()
        if self.cached_items:
            self.display_items(self.cached_items)
        else:
            self.show_placeholder("Use SETUP to enter an RSS or Atom feed URL.")

    def show_placeholder(self, text: str):
        c = self.theme
        for widget in self.feed_container.winfo_children():
            widget.destroy()
        box = tk.Frame(self.feed_container, bg=c["card"], highlightthickness=1, highlightbackground=c["card_border"])
        box.pack(fill="x", padx=4, pady=4, ipady=40)
        label = tk.Label(
            box, text=text, bg=c["card"], fg=c["subtle"],
            font=(UI_FONT, 13), wraplength=720, justify="center"
        )
        label.pack(fill="x", padx=20)
        self._bind_feed_scrolling(box)
        if hasattr(self, "feed_canvas"):
            self.feed_canvas.yview_moveto(0)
            self.after_idle(self._update_feed_scrollregion)

    def startup(self):
        if not self.feed_url:
            self.open_setup()
        else:
            self.update_feed_label()
            self.refresh_feed()

    def open_setup(self):
        previous_url = self.feed_url
        dialog = SetupDialog(
            self, self.feed_url, self.contact_email, self.refresh_seconds,
            self.theme_name, self.saved_feeds,
        )
        self.wait_window(dialog)
        if dialog.result:
            self.feed_url = dialog.result
            self.contact_email = dialog.contact_result
            self.refresh_seconds = dialog.refresh_result
            new_theme = getattr(dialog, "theme_result", self.theme_name)
            theme_changed = new_theme != self.theme_name
            self.theme_name = new_theme
            self.theme = THEMES[self.theme_name]
            self.saved_feeds = dialog.saved_feeds_result
            self.forgotten_feed_urls.update(dialog.deleted_feed_urls)
            if self.feed_url not in dialog.deleted_feed_urls:
                self.forgotten_feed_urls.discard(self.feed_url)
                self.remember_feed(
                    self.feed_url, stale_alert=dialog.stale_alert_result
                )
            if self.feed_url != previous_url:
                self.etag = ""
                self.last_modified = ""
                self.cached_items = []
                self.latest_feed_timestamp = None
                self.active_feed_title = self.saved_feed_label(self.feed_url)
            if theme_changed:
                self.rebuild_ui()
            self.update_footer_text()
            self.update_feed_label()
            self.save_settings()
            self.refresh_feed()

    def load_settings(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        except (OSError, json.JSONDecodeError) as exc:
            self.settings_warnings.append(f"Settings file could not be read: {exc}")
            return

        if not isinstance(data, dict):
            self.settings_warnings.append("Settings root was not an object; defaults were used.")
            return

        feed_url = data.get("feed_url", "")
        if isinstance(feed_url, str) and (not feed_url.strip() or is_safe_web_url(feed_url)):
            self.feed_url = feed_url.strip()
        elif "feed_url" in data:
            self.settings_warnings.append("Invalid feed URL was ignored.")

        contact = data.get("contact_email", "")
        if isinstance(contact, str):
            contact = contact.strip()
            if not contact or ("@" in contact and "." in contact.rsplit("@", 1)[-1]):
                self.contact_email = contact
            else:
                self.settings_warnings.append("Invalid contact email was ignored.")
        elif "contact_email" in data:
            self.settings_warnings.append("Invalid contact email was ignored.")

        theme = data.get("theme", DEFAULT_THEME)
        if theme in THEMES:
            self.theme_name = theme
        elif "theme" in data:
            self.settings_warnings.append("Unknown theme was replaced with the default.")

        allowed_seconds = {seconds for _label, seconds in REFRESH_OPTIONS}
        refresh_invalid = False
        try:
            refresh_seconds = int(data.get("refresh_seconds", DEFAULT_REFRESH_SECONDS))
        except (TypeError, ValueError):
            refresh_seconds = DEFAULT_REFRESH_SECONDS
            refresh_invalid = True
        if refresh_seconds in allowed_seconds and not refresh_invalid:
            self.refresh_seconds = refresh_seconds
        elif "refresh_seconds" in data:
            self.settings_warnings.append("Invalid reload interval was replaced with 15 seconds.")

        forgotten = data.get("forgotten_feed_urls", [])
        if not isinstance(forgotten, list):
            forgotten = []
            self.settings_warnings.append("Invalid forgotten-feed list was ignored.")
        self.forgotten_feed_urls = {
            url.strip() for url in forgotten
            if isinstance(url, str) and is_safe_web_url(url.strip())
        }

        saved_feeds = data.get("saved_feeds", [])
        if not isinstance(saved_feeds, list):
            saved_feeds = []
            self.settings_warnings.append("Invalid saved-feed list was ignored.")
        seen_urls = set()
        invalid_feed_records = 0
        for saved_feed in saved_feeds:
            if not isinstance(saved_feed, dict):
                invalid_feed_records += 1
                continue
            url = saved_feed.get("url", "")
            url = url.strip() if isinstance(url, str) else ""
            if (not is_safe_web_url(url) or url in seen_urls
                    or url in self.forgotten_feed_urls):
                invalid_feed_records += 1
                continue
            label_value = saved_feed.get("label", "")
            label = label_value.strip() if isinstance(label_value, str) else ""
            self.saved_feeds.append({
                "url": url,
                "label": label or fallback_feed_label(url),
                "stale_alert": saved_feed.get("stale_alert") is True,
            })
            seen_urls.add(url)
        if invalid_feed_records:
            self.settings_warnings.append(
                f"Ignored {invalid_feed_records} invalid saved-feed record(s)."
            )

        if (self.feed_url and self.feed_url not in seen_urls
                and self.feed_url not in self.forgotten_feed_urls):
            self.saved_feeds.append({
                "url": self.feed_url,
                "label": fallback_feed_label(self.feed_url),
                "stale_alert": False,
            })
        self.active_feed_title = self.saved_feed_label(self.feed_url)

        geometry = data.get("geometry")
        if geometry:
            if isinstance(geometry, str) and re.fullmatch(
                r"\d+x\d+[+-]\d+[+-]\d+", geometry
            ):
                try:
                    self.geometry(geometry)
                except tk.TclError:
                    self.settings_warnings.append("Invalid window geometry was ignored.")
            else:
                self.settings_warnings.append("Invalid window geometry was ignored.")

    def show_settings_warnings(self):
        if self.settings_warnings:
            messagebox.showwarning(
                "Settings Repaired",
                "Some saved settings were invalid and were repaired:\n\n"
                + "\n".join(f"• {warning}" for warning in self.settings_warnings),
                parent=self,
            )

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "feed_url": self.feed_url,
                    "contact_email": self.contact_email,
                    "refresh_seconds": self.refresh_seconds,
                    "theme": self.theme_name,
                    "geometry": self.geometry(),
                    "saved_feeds": self.saved_feeds,
                    "forgotten_feed_urls": sorted(self.forgotten_feed_urls),
                }, f, indent=2)
        except Exception:
            pass

    def on_close(self):
        self.save_settings()
        self.destroy()

    def tick(self):
        self.process_fetch_results()
        c = self.theme
        now = datetime.now()
        self.clock_date_display.set(now.strftime("%Y-%m-%d"))
        self.clock_time_display.set(now.strftime("%H:%M:%S"))

        remaining = max(0, int(round(self.next_refresh - time.monotonic())))
        self.countdown_var.set(self.format_countdown(remaining))
        self.feed_delta_display.set(
            self.format_feed_delta(self.latest_feed_timestamp).upper()
        )

        monotonic_now = time.monotonic()
        stale_alert = stale_feed_alert(
            self.latest_feed_timestamp,
            self.feed_stale_alert_enabled(self.feed_url),
        )
        if stale_alert:
            color, toggle_interval = stale_alert
            if monotonic_now - self.stale_led_last_toggle >= toggle_interval:
                self.stale_led_state = not self.stale_led_state
                self.stale_led_last_toggle = monotonic_now
            self.stale_led.itemconfigure(
                self.stale_led_dot,
                fill=color if self.stale_led_state else c["led_off"],
            )
        else:
            self.stale_led_state = False
            self.stale_led_last_toggle = monotonic_now
            self.stale_led.itemconfigure(self.stale_led_dot, fill=c["led_off"])

        if 0 < remaining <= 5 and not self.fetching:
            self.led_state = not self.led_state
            color = c["text"] if self.led_state else c["led_off"]
            self.led.itemconfigure(self.led_dot, fill=color)
        else:
            self.led_state = False
            self.led.itemconfigure(self.led_dot, fill=c["led_off"])

        if remaining <= 0 and self.feed_url and not self.fetching:
            self.refresh_feed()

        self.after(250, self.tick)

    def refresh_feed(self):
        if not self.feed_url or self.fetching:
            return
        self.fetching = True
        self.next_refresh = time.monotonic() + self.refresh_seconds
        self.status_var.set("RELOADING")
        request_state = {
            "url": self.feed_url,
            "contact_email": self.contact_email,
            "refresh_seconds": self.refresh_seconds,
            "etag": self.etag,
            "last_modified": self.last_modified,
        }
        thread = threading.Thread(
            target=self.fetch_worker, args=(request_state,), daemon=True
        )
        thread.start()

    def fetch_worker(self, request_state):
        """Fetch and parse without calling Tk; results cross a thread-safe queue."""
        try:
            headers = {
                "User-Agent": APP_USER_AGENT,
                "Accept": "application/atom+xml,application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.5",
                "Accept-Language": "en-US,en;q=0.9",
            }
            # Contact identity is sent only when the user supplied a real address.
            if request_state["contact_email"]:
                headers["From"] = request_state["contact_email"]
                headers["User-Agent"] += f" (contact: {request_state['contact_email']})"
            # Conditional requests avoid redownloading unchanged feeds.
            if request_state["etag"]:
                headers["If-None-Match"] = request_state["etag"]
            if request_state["last_modified"]:
                headers["If-Modified-Since"] = request_state["last_modified"]

            request = Request(request_state["url"], headers=headers)
            with urlopen(request, timeout=12, context=SSL_CONTEXT) as response:
                etag = response.headers.get("ETag", request_state["etag"])
                last_modified = response.headers.get(
                    "Last-Modified", request_state["last_modified"]
                )
                content_type = response.headers.get("Content-Type", "")
                data = response.read(MAX_FEED_BYTES + 1)
            validate_feed_response(data, content_type)
            feed_title, items = parse_feed_document(data, request_state["url"])
            self.fetch_results.put((
                "success", request_state["url"], feed_title, items, etag, last_modified
            ))
        except HTTPError as exc:
            if exc.code == 304:
                self.fetch_results.put(("not_modified", request_state["url"]))
                return
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            backoff_delay = 0
            if exc.code in (429, 503) and retry_after:
                parsed_delay = parse_retry_after(retry_after)
                if parsed_delay is not None:
                    delay = max(request_state["refresh_seconds"], parsed_delay)
                    backoff_delay = delay
                    detail = f"Server requested a {delay}-second retry delay (HTTP {exc.code})."
                else:
                    detail = f"HTTP error {exc.code}: {exc.reason}"
            elif (exc.code == 403 and "sec.gov" in request_state["url"].lower()
                  and not request_state["contact_email"]):
                detail = (
                    "HTTP error 403: SEC.gov may require an identified automated client. "
                    "Open SETUP and enter a genuine contact email, then save the feed again."
                )
            else:
                detail = f"HTTP error {exc.code}: {exc.reason}"
            self.fetch_results.put(("error", request_state["url"], detail, backoff_delay))
        except URLError as exc:
            self.fetch_results.put((
                "error", request_state["url"], f"Network error: {exc.reason}", 0
            ))
        except Exception as exc:
            self.fetch_results.put(("error", request_state["url"], str(exc), 0))

    def process_fetch_results(self):
        """Apply completed network work exclusively on Tk's main thread."""
        while True:
            try:
                result = self.fetch_results.get_nowait()
            except queue.Empty:
                break

            kind, request_url, *payload = result
            if request_url != self.feed_url:
                self.fetch_complete()
                self.next_refresh = time.monotonic()
                continue
            if kind == "success":
                feed_title, items, self.etag, self.last_modified = payload
                self.cached_items = items
                if feed_title:
                    self.active_feed_title = feed_title
                self.remember_feed(request_url, feed_title)
                self.update_feed_label()
                self.display_items(items)
            elif kind == "not_modified":
                self.show_not_modified()
            else:
                message, backoff_delay = payload
                if backoff_delay:
                    self.backoff_until = time.monotonic() + backoff_delay
                self.show_error(message)
            self.fetch_complete()

    def remember_feed(self, url: str, feed_title: str = "", stale_alert=None):
        """Add or update a feed memory; the list intentionally has no limit."""
        if url in self.forgotten_feed_urls:
            return
        label = feed_title.strip() if feed_title else ""
        for saved_feed in self.saved_feeds:
            if saved_feed["url"] == url:
                if label:
                    saved_feed["label"] = label
                if stale_alert is not None:
                    saved_feed["stale_alert"] = bool(stale_alert)
                self.save_settings()
                return
        self.saved_feeds.append({
            "url": url,
            "label": label or fallback_feed_label(url),
            "stale_alert": bool(stale_alert) if stale_alert is not None else False,
        })
        self.save_settings()

    def feed_stale_alert_enabled(self, url: str) -> bool:
        return next(
            (
                bool(saved_feed.get("stale_alert", False))
                for saved_feed in self.saved_feeds
                if saved_feed["url"] == url
            ),
            False,
        )

    def saved_feed_label(self, url: str) -> str:
        if not url:
            return ""
        return next(
            (
                str(saved_feed.get("label", "")).strip()
                for saved_feed in self.saved_feeds
                if saved_feed["url"] == url and saved_feed.get("label")
            ),
            "",
        )

    def feed_display_name(self) -> str:
        if not self.feed_url:
            return "NO FEED CONFIGURED"
        return (
            self.active_feed_title
            or self.saved_feed_label(self.feed_url)
            or fallback_feed_label(self.feed_url)
        )

    def update_feed_label(self):
        if hasattr(self, "feed_label"):
            self.feed_label.configure(text=self.feed_display_name())

    def show_not_modified(self):
        self.status_var.set("LIVE • NO CHANGE")
        if self.cached_items and not self.feed_container.winfo_children():
            self.display_items(self.cached_items)

    def fetch_complete(self):
        self.fetching = False
        self.next_refresh = max(time.monotonic() + self.refresh_seconds, self.backoff_until)

    def show_error(self, message: str):
        self.status_var.set("FEED ERROR")
        self.show_placeholder(f"Unable to load the feed.\n\n{message}")

    def display_items(self, items):
        self.status_var.set(f"LIVE • {len(items)} ITEMS")
        self.latest_feed_timestamp = next(
            (item["published"] for item in items if item.get("published")), None
        )
        self.feed_delta_display.set(
            self.format_feed_delta(self.latest_feed_timestamp).upper()
        )
        for widget in self.feed_container.winfo_children():
            widget.destroy()

        for index, item in enumerate(items):
            is_latest = index == 0
            c = self.theme
            border = c["accent"] if is_latest else c["card_border"]
            bg = c["card_latest"] if is_latest else c["card"]

            card = tk.Frame(
                self.feed_container, bg=bg,
                highlightthickness=1, highlightbackground=border,
                padx=14, pady=9
            )
            card.pack(fill="x", padx=4, pady=(0, 7))

            top = tk.Frame(card, bg=bg)
            top.pack(fill="x")

            if item["published"]:
                stamp = item["published"].strftime("%Y-%m-%d  %H:%M:%S")
            else:
                stamp = item["raw_date"] or "TIMESTAMP UNAVAILABLE"

            tk.Label(
                top, text=stamp, bg=bg,
                fg=c["accent2"] if is_latest else c["accent3"],
                font=(MONO_FONT, 12, "bold")
            ).pack(side="left")

            if is_latest:
                tk.Label(
                    top, text="LATEST UPDATE", bg=c["accent"], fg=c["window"],
                    font=(UI_FONT, 8, "bold"), padx=8, pady=3
                ).pack(side="right")

            title_label = tk.Label(
                card, text=item["title"], bg=bg, fg=c["text"],
                font=(UI_FONT, 12, "bold"), anchor="w",
                justify="left", wraplength=850
            )
            title_label.pack(fill="x", pady=(5, 3))

            summary = self.clean_text(item["summary"])
            if summary:
                summary_label = tk.Label(
                    card, text=summary, bg=bg, fg=c["muted"],
                    font=(UI_FONT, 9), anchor="w", justify="left",
                    wraplength=850
                )
                summary_label.pack(fill="x")

            # Make the complete feed card behave as a link. Opening is delegated
            # to the OS, which uses the user's configured default browser.
            link = str(item.get("link") or "").strip()
            if is_safe_web_url(link):
                self.make_card_clickable(card, link)
            self._bind_feed_scrolling(card)

        self.feed_canvas.yview_moveto(0)
        self.after_idle(self._update_feed_scrollregion)


    def make_card_clickable(self, widget, link: str):
        """Bind a card and all of its child widgets to the feed entry URL."""
        def open_link(_event=None):
            try:
                webbrowser.open(link, new=2)
            except Exception as exc:
                messagebox.showerror(
                    "Unable to open link",
                    f"The feed entry could not be opened in the default browser.\n\n{exc}",
                    parent=self,
                )

        def bind_tree(node):
            node.configure(cursor=LINK_CURSOR)
            node.bind("<Button-1>", open_link, add="+")
            for child in node.winfo_children():
                bind_tree(child)

        bind_tree(widget)


    def update_footer_text(self):
        if hasattr(self, "footer_var"):
            self.footer_var.set(f"Simple RSS version {APP_VERSION}")

    @staticmethod
    def format_interval(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds} seconds"
        minutes = seconds // 60
        return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"

    @staticmethod
    def format_countdown(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds:02d}s"
        minutes, secs = divmod(seconds, 60)
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_feed_delta(feed_timestamp) -> str:
        if feed_timestamp is None:
            return "unknown"
        now = datetime.now().astimezone()
        if feed_timestamp.tzinfo is None:
            feed_timestamp = feed_timestamp.replace(tzinfo=timezone.utc)
        # Subtract aware datetimes directly. Calling astimezone() on very old
        # dates delegates to Windows' local-time API, which rejects year 1.
        delta_seconds = int((now - feed_timestamp).total_seconds())
        if delta_seconds < 0:
            return "just now"
        if delta_seconds < 10:
            return "just now"
        if delta_seconds < 60:
            return f"{delta_seconds} seconds ago"
        minutes = delta_seconds // 60
        if minutes < 60:
            return f"{minutes} minute ago" if minutes == 1 else f"{minutes} minutes ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
        days = hours // 24
        return f"{days} day ago" if days == 1 else f"{days} days ago"

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        parser = TextExtractor()
        try:
            parser.feed(text)
            parser.close()
            cleaned = parser.text()
        except Exception:
            cleaned = " ".join(text.split())
        if len(cleaned) > 420:
            cleaned = cleaned[:417].rstrip() + "..."
        return cleaned


if __name__ == "__main__":
    try:
        app = RSSViewer()
        app.mainloop()
    except Exception as exc:
        try:
            messagebox.showerror(APP_NAME, f"The application could not start:\n\n{exc}")
        except Exception:
            print(exc, file=sys.stderr)
