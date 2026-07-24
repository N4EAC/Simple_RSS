import json
import os
import sys
import threading
import time
import tkinter as tk
import ctypes
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from tkinter import messagebox, ttk
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET
import webbrowser

APP_NAME = "Simple RSS"
APP_VERSION = "1.4.2"
DEFAULT_REFRESH_SECONDS = 15
REFRESH_OPTIONS = [
    ("10 seconds", 10),
    ("15 seconds", 15),
    ("30 seconds", 30),
    ("60 seconds", 60),
    ("1 minute", 60),
    ("5 minutes", 300),
    ("10 minutes", 600),
]
MAX_ITEMS = 5
APP_USER_AGENT = f"SimpleRSS/{APP_VERSION} (Windows; RSS/Atom reader)"

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
    def __init__(self, parent, text="", dot=3, gap=1, char_gap=4, color="#79f9ff", **kwargs):
        self.dot = dot
        self.gap = gap
        self.char_gap = char_gap
        self.dot_color = color
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
        width = max(1, x + 2)
        height = 7 * step + 4
        self.configure(width=width, height=height, scrollregion=(0,0,width,height))


def resource_path(filename: str) -> str:
    """Return a bundled resource path for source and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def windows_uses_dark_apps() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return int(value) == 0
    except Exception:
        return False


def apply_windows_titlebar_theme(window: tk.Tk) -> None:
    """Ask Windows DWM to match the user's light/dark app theme."""
    if sys.platform != "win32":
        return
    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        enabled = ctypes.c_int(1 if windows_uses_dark_apps() else 0)
        # Attribute 20 is current; 19 supports older Windows 10 builds.
        for attribute in (20, 19):
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attribute, ctypes.byref(enabled), ctypes.sizeof(enabled)
            )
            if result == 0:
                break
    except Exception:
        pass


def configure_windows_identity(window: tk.Tk) -> None:
    """Set the app identity and window/taskbar icon on Windows."""
    try:
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "Eduardo.SimpleRSS.1.4.2"
            )
        ico_path = resource_path("simple_rss.ico")
        png_path = resource_path("simple_rss.png")
        if os.path.exists(ico_path):
            window.iconbitmap(default=ico_path)
        if os.path.exists(png_path):
            icon_image = tk.PhotoImage(file=png_path)
            window.iconphoto(True, icon_image)
            window._icon_image = icon_image
    except Exception:
        pass


def app_data_dir() -> str:
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "SimpleRSS")
    os.makedirs(path, exist_ok=True)
    return path


CONFIG_PATH = os.path.join(app_data_dir(), "settings.json")


class RSSParseError(Exception):
    pass


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


def parse_feed(xml_bytes: bytes):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise RSSParseError(f"Invalid XML: {exc}") from exc

    entries = []
    for node in root.iter():
        if local_name(node.tag) not in {"item", "entry"}:
            continue

        title = child_text(node, ["title"]) or "Untitled update"
        summary = child_text(node, ["description", "summary", "content"])
        date_text = child_text(node, ["pubDate", "published", "updated", "date"])
        dt = parse_date(date_text)

        link = ""
        for child in list(node):
            if local_name(child.tag) == "link":
                link = (child.attrib.get("href") or (child.text or "")).strip()
                if link:
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
    return entries[:MAX_ITEMS]


class SetupDialog(tk.Toplevel):
    def __init__(self, parent, current_url: str, current_contact: str, current_refresh_seconds: int, current_theme: str):
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
        self.transient(parent)
        self.grab_set()

        frame = tk.Frame(self, bg=c["window"], padx=22, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="RSS FEED SETUP", bg=c["window"], fg=c["accent"],
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 14))

        tk.Label(
            frame, text="Feed URL", bg=c["window"], fg=c["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        self.url_var = tk.StringVar(value=current_url)
        self.entry = tk.Entry(
            frame, textvariable=self.url_var, width=58,
            bg=c["entry"], fg=c["text"], insertbackground=c["text"],
            relief="flat", highlightthickness=1,
            highlightbackground=c["entry_border"], highlightcolor=c["accent"],
            font=("Segoe UI", 10)
        )
        self.entry.pack(fill="x", ipady=8, pady=(6, 12))
        self.entry.focus_set()
        self.entry.selection_range(0, tk.END)

        tk.Label(
            frame, text="Optional contact email (used only when a provider requires identification)",
            bg=c["window"], fg=c["muted"], font=("Segoe UI", 10)
        ).pack(anchor="w")
        self.contact_var = tk.StringVar(value=current_contact)
        self.contact_entry = tk.Entry(
            frame, textvariable=self.contact_var, width=58,
            bg=c["entry"], fg=c["text"], insertbackground=c["text"],
            relief="flat", highlightthickness=1,
            highlightbackground=c["entry_border"], highlightcolor=c["accent"],
            font=("Segoe UI", 10)
        )
        self.contact_entry.pack(fill="x", ipady=8, pady=(6, 14))

        tk.Label(
            frame, text="Automatic reload interval", bg=c["window"], fg=c["muted"],
            font=("Segoe UI", 10)
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
            font=("Segoe UI", 10),
        )
        self.refresh_combo.pack(fill="x", ipady=4, pady=(6, 12))

        tk.Label(
            frame, text="Theme", bg=c["window"], fg=c["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.theme_name)
        self.theme_combo = ttk.Combobox(
            frame, textvariable=self.theme_var, state="readonly",
            values=list(THEMES.keys()), width=55, font=("Segoe UI", 10),
        )
        self.theme_combo.pack(fill="x", ipady=4, pady=(6, 16))
        self.configure_combobox_style()

        buttons = tk.Frame(frame, bg=c["window"])
        buttons.pack(fill="x")
        tk.Button(
            buttons, text="CANCEL", command=self.destroy,
            bg=c["button"], fg=c["muted"], activebackground=c["button_active"],
            activeforeground=c["button_text"], relief="flat", padx=18, pady=7,
            font=("Segoe UI", 9, "bold")
        ).pack(side="right")
        tk.Button(
            buttons, text="SAVE", command=self.save,
            bg=c["accent"], fg=c["window"], activebackground=c["accent3"],
            activeforeground=c["window"], relief="flat", padx=20, pady=7,
            font=("Segoe UI", 9, "bold")
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
        self.option_add("*TCombobox*Listbox.background", c["entry"])
        self.option_add("*TCombobox*Listbox.foreground", c["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", c["button"])
        self.option_add("*TCombobox*Listbox.selectForeground", c["button_text"])

    def save(self):
        value = self.url_var.get().strip()
        if not value.lower().startswith(("http://", "https://")):
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
        self.destroy()


class RSSViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1000x690")
        self.minsize(820, 560)
        self.theme_name = DEFAULT_THEME
        self.theme = THEMES[self.theme_name]
        self.configure(bg=self.theme["window"])
        configure_windows_identity(self)
        self.after(0, lambda: apply_windows_titlebar_theme(self))

        self.feed_url = ""
        self.contact_email = ""
        self.refresh_seconds = DEFAULT_REFRESH_SECONDS
        self.latest_feed_timestamp = None
        self.next_refresh = time.monotonic()
        self.fetching = False
        self.led_state = False
        self.item_frames = []
        self.etag = ""
        self.last_modified = ""
        self.cached_items = []
        self.backoff_until = 0.0

        self.load_settings()
        self.theme = THEMES.get(self.theme_name, THEMES[DEFAULT_THEME])
        self.configure(bg=self.theme["window"])
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.after(150, self.startup)
        self.after(200, self.tick)

    def build_ui(self):
        c = self.theme
        header = tk.Frame(self, bg=c["header"], height=122)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_wrap = tk.Frame(header, bg=c["header"])
        title_wrap.pack(side="left", fill="y", padx=(22, 14))
        tk.Label(
            title_wrap, text="SIMPLE RSS", bg=c["header"], fg=c["accent"],
            font=("Segoe UI", 23, "bold")
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
            font=("Consolas", 8, "bold")
        ).pack(anchor="w", pady=(8, 3))
        self.feed_delta_display = DotMatrixDisplay(
            delta_wrap, "UNKNOWN", dot=2, gap=1, char_gap=3,
            color=c["delta"], bg=c["panel"]
        )
        self.feed_delta_display.pack(anchor="w", pady=(3, 0))

        controls = tk.Frame(header, bg=c["header"])
        controls.pack(side="right", fill="y", padx=20)

        self.led = tk.Canvas(controls, width=10, height=10, bg=c["header"], highlightthickness=0)
        self.led.pack(side="left", padx=(0, 7))
        self.led_dot = self.led.create_oval(3, 3, 7, 7, fill=c["led_off"], outline="", width=0)

        self.countdown_var = tk.StringVar(value="RELOAD --")
        tk.Label(
            controls, textvariable=self.countdown_var, bg=c["header"], fg=c["muted"],
            font=("Consolas", 10, "bold")
        ).pack(side="left", padx=(0, 14))

        tk.Button(
            controls, text="SETUP", command=self.open_setup,
            bg=c["button"], fg=c["text"], activebackground=c["button_active"],
            activeforeground=c["button_text"], relief="flat", padx=16, pady=8,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        status_bar = tk.Frame(self, bg=c["status"], height=38)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)

        self.feed_label = tk.Label(
            status_bar, text="NO FEED CONFIGURED", bg=c["status"], fg=c["muted"],
            font=("Segoe UI", 9), anchor="w"
        )
        self.feed_label.pack(side="left", fill="x", expand=True, padx=20)

        self.status_var = tk.StringVar(value="IDLE")
        tk.Label(
            status_bar, textvariable=self.status_var, bg=c["status"], fg=c["accent"],
            font=("Consolas", 9, "bold")
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
            bg=c["footer"], fg=c["footer_text"], font=("Segoe UI", 8)
        ).pack(side="left", padx=18)


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
        self.feed_label.configure(text=self.feed_url or "NO FEED CONFIGURED")
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
            font=("Segoe UI", 13), wraplength=720, justify="center"
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
            self.feed_label.configure(text=self.feed_url)
            self.refresh_feed()

    def open_setup(self):
        dialog = SetupDialog(
            self, self.feed_url, self.contact_email, self.refresh_seconds, self.theme_name
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
            if theme_changed:
                self.rebuild_ui()
            self.update_footer_text()
            self.feed_label.configure(text=self.feed_url)
            self.save_settings()
            self.refresh_feed()

    def load_settings(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.feed_url = str(data.get("feed_url", "")).strip()
            self.contact_email = str(data.get("contact_email", "")).strip()
            self.theme_name = str(data.get("theme", DEFAULT_THEME))
            if self.theme_name not in THEMES:
                self.theme_name = DEFAULT_THEME
            try:
                self.refresh_seconds = int(data.get("refresh_seconds", DEFAULT_REFRESH_SECONDS))
            except (TypeError, ValueError):
                self.refresh_seconds = DEFAULT_REFRESH_SECONDS
            allowed_seconds = {seconds for _label, seconds in REFRESH_OPTIONS}
            if self.refresh_seconds not in allowed_seconds:
                self.refresh_seconds = DEFAULT_REFRESH_SECONDS
            geometry = data.get("geometry")
            if geometry:
                self.geometry(geometry)
        except Exception:
            self.feed_url = ""
            self.contact_email = ""
            self.refresh_seconds = DEFAULT_REFRESH_SECONDS
            self.theme_name = DEFAULT_THEME

    def save_settings(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "feed_url": self.feed_url,
                    "contact_email": self.contact_email,
                    "refresh_seconds": self.refresh_seconds,
                    "theme": self.theme_name,
                    "geometry": self.geometry(),
                }, f, indent=2)
        except Exception:
            pass

    def on_close(self):
        self.save_settings()
        self.destroy()

    def tick(self):
        c = self.theme
        now = datetime.now()
        self.clock_date_display.set(now.strftime("%Y-%m-%d"))
        self.clock_time_display.set(now.strftime("%H:%M:%S"))

        remaining = max(0, int(round(self.next_refresh - time.monotonic())))
        self.countdown_var.set(f"RELOAD {self.format_countdown(remaining)}")
        self.feed_delta_display.set(
            self.format_feed_delta(self.latest_feed_timestamp).upper()
        )

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
        thread = threading.Thread(target=self.fetch_worker, daemon=True)
        thread.start()

    def fetch_worker(self):
        try:
            headers = {
                "User-Agent": APP_USER_AGENT,
                "Accept": "application/atom+xml,application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.5",
                "Accept-Language": "en-US,en;q=0.9",
            }
            # Contact identity is sent only when the user supplied a real address.
            if self.contact_email:
                headers["From"] = self.contact_email
                headers["User-Agent"] += f" (contact: {self.contact_email})"
            # Conditional requests avoid redownloading unchanged feeds.
            if self.etag:
                headers["If-None-Match"] = self.etag
            if self.last_modified:
                headers["If-Modified-Since"] = self.last_modified

            request = Request(self.feed_url, headers=headers)
            with urlopen(request, timeout=12) as response:
                self.etag = response.headers.get("ETag", self.etag)
                self.last_modified = response.headers.get("Last-Modified", self.last_modified)
                data = response.read(5_000_000)
            items = parse_feed(data)
            self.cached_items = items
            self.after(0, lambda: self.display_items(items))
        except HTTPError as exc:
            if exc.code == 304:
                self.after(0, self.show_not_modified)
                return
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if exc.code in (429, 503) and retry_after:
                try:
                    delay = max(self.refresh_seconds, int(retry_after))
                    self.backoff_until = time.monotonic() + delay
                    detail = f"Server requested a {delay}-second retry delay (HTTP {exc.code})."
                except ValueError:
                    detail = f"HTTP error {exc.code}: {exc.reason}"
            elif exc.code == 403 and "sec.gov" in self.feed_url.lower() and not self.contact_email:
                detail = (
                    "HTTP error 403: SEC.gov may require an identified automated client. "
                    "Open SETUP and enter a genuine contact email, then save the feed again."
                )
            else:
                detail = f"HTTP error {exc.code}: {exc.reason}"
            self.after(0, lambda message=detail: self.show_error(message))
        except URLError as exc:
            self.after(0, lambda: self.show_error(f"Network error: {exc.reason}"))
        except Exception as exc:
            self.after(0, lambda: self.show_error(str(exc)))
        finally:
            self.after(0, self.fetch_complete)

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
                font=("Digital-7", 12, "bold")
            ).pack(side="left")

            if is_latest:
                tk.Label(
                    top, text="LATEST UPDATE", bg=c["accent"], fg=c["window"],
                    font=("Segoe UI", 8, "bold"), padx=8, pady=3
                ).pack(side="right")

            title_label = tk.Label(
                card, text=item["title"], bg=bg, fg=c["text"],
                font=("Segoe UI", 12, "bold"), anchor="w",
                justify="left", wraplength=850
            )
            title_label.pack(fill="x", pady=(5, 3))

            summary = self.clean_text(item["summary"])
            if summary:
                summary_label = tk.Label(
                    card, text=summary, bg=bg, fg=c["muted"],
                    font=("Segoe UI", 9), anchor="w", justify="left",
                    wraplength=850
                )
                summary_label.pack(fill="x")

            # Make the complete feed card behave as a link. Opening is delegated
            # to Windows, which uses the user's configured default browser.
            link = str(item.get("link") or "").strip()
            if link:
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
            node.configure(cursor="hand2")
            node.bind("<Button-1>", open_link, add="+")
            for child in node.winfo_children():
                bind_tree(child)

        bind_tree(widget)


    def update_footer_text(self):
        if hasattr(self, "footer_var"):
            self.footer_var.set(f"Simple RSS - Legal & Compliant version {APP_VERSION}")

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
        delta_seconds = int((now - feed_timestamp.astimezone()).total_seconds())
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
        out = []
        in_tag = False
        for ch in text:
            if ch == "<":
                in_tag = True
            elif ch == ">":
                in_tag = False
            elif not in_tag:
                out.append(ch)
        cleaned = " ".join("".join(out).split())
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
