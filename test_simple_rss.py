import json
import ssl
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import simple_rss
from simple_rss import (
    FeedResponseError,
    MAX_FEED_BYTES,
    MAX_ITEMS,
    FEED_DELTA_DISPLAY_CHARS,
    RSSParseError,
    RSSViewer,
    SSL_CONTEXT,
    STALE_CRITICAL_COLOR,
    STALE_WARNING_COLOR,
    is_safe_web_url,
    parse_feed,
    parse_feed_document,
    parse_retry_after,
    saved_feed_choices,
    stale_feed_alert,
    validate_feed_response,
)


class FeedParsingTests(unittest.TestCase):
    def test_rss_title_and_newest_items(self):
        items_xml = "".join(
            f"""
            <item>
              <title>Item {index}</title>
              <link>https://example.com/{index}</link>
              <pubDate>Wed, {index + 1:02d} Jan 2025 12:00:00 GMT</pubDate>
            </item>
            """
            for index in range(7)
        )
        title, items = parse_feed_document(
            f"<rss><channel><title>Example News</title>{items_xml}</channel></rss>".encode()
        )

        self.assertEqual(title, "Example News")
        self.assertEqual(len(items), MAX_ITEMS)
        self.assertEqual(items[0]["title"], "Item 6")

    def test_atom_title_and_href_link(self):
        xml = b"""<?xml version="1.0"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <title>Atom Example</title>
          <entry>
            <title>An update</title>
            <link href="https://example.com/update"/>
            <updated>2025-01-02T03:04:05Z</updated>
          </entry>
        </feed>
        """
        title, items = parse_feed_document(xml)

        self.assertEqual(title, "Atom Example")
        self.assertEqual(items[0]["link"], "https://example.com/update")
        self.assertEqual(parse_feed(xml), items)

    def test_invalid_xml_is_reported(self):
        with self.assertRaises(RSSParseError):
            parse_feed(b"<rss>")

    def test_atom_prefers_alternate_link_and_resolves_relative_url(self):
        xml = b"""
        <feed xmlns="http://www.w3.org/2005/Atom" xml:base="https://example.com/news/">
          <title>Example</title>
          <entry>
            <title>Update</title>
            <link rel="self" href="entry.atom" type="application/atom+xml"/>
            <link rel="alternate" href="story/1" type="text/html"/>
          </entry>
        </feed>
        """
        _title, items = parse_feed_document(xml, "https://example.com/feed.atom")
        self.assertEqual(items[0]["link"], "https://example.com/news/story/1")

    def test_rss_permalink_guid_is_used_when_link_is_missing(self):
        xml = b"""
        <rss><channel><title>Example</title><item>
          <title>Update</title><guid>https://example.com/story/1</guid>
        </item></channel></rss>
        """
        self.assertEqual(parse_feed(xml)[0]["link"], "https://example.com/story/1")

    def test_undated_entries_preserve_source_order(self):
        xml = b"""
        <rss><channel><title>Example</title>
          <item><title>First</title></item>
          <item><title>Second</title></item>
        </channel></rss>
        """
        self.assertEqual(
            [item["title"] for item in parse_feed(xml)], ["First", "Second"]
        )


class TextAndLinkTests(unittest.TestCase):
    def test_html_summary_becomes_plain_text(self):
        source = (
            "<p>Hello &amp; welcome.</p><script>bad()</script>"
            "<div>Second&nbsp;line<br>here.</div>"
        )
        self.assertEqual(
            RSSViewer.clean_text(source),
            "Hello & welcome. Second line here.",
        )

    def test_summary_is_truncated(self):
        cleaned = RSSViewer.clean_text("x" * 500)
        self.assertEqual(len(cleaned), 420)
        self.assertTrue(cleaned.endswith("..."))

    def test_only_absolute_http_links_are_safe(self):
        self.assertTrue(is_safe_web_url("https://example.com/story"))
        self.assertTrue(is_safe_web_url("http://example.com"))
        self.assertFalse(is_safe_web_url("file:///etc/passwd"))
        self.assertFalse(is_safe_web_url("javascript:alert(1)"))
        self.assertFalse(is_safe_web_url("/relative/story"))
        self.assertFalse(is_safe_web_url("https:///missing-host"))

    def test_ssl_context_keeps_certificate_and_hostname_checks_enabled(self):
        self.assertEqual(SSL_CONTEXT.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(SSL_CONTEXT.check_hostname)

    def test_feed_delta_strings_fit_the_fixed_display(self):
        samples = [
            None,
            datetime(1, 1, 2, tzinfo=timezone.utc),
        ]
        for timestamp in samples:
            text = RSSViewer.format_feed_delta(timestamp).upper()
            self.assertLessEqual(len(text), FEED_DELTA_DISPLAY_CHARS)


class ResponseValidationTests(unittest.TestCase):
    def test_oversized_feed_is_rejected_explicitly(self):
        with self.assertRaisesRegex(FeedResponseError, "exceeds"):
            validate_feed_response(b"x" * (MAX_FEED_BYTES + 1), "application/xml")

    def test_html_response_gets_a_clear_error(self):
        with self.assertRaisesRegex(FeedResponseError, "HTML page"):
            validate_feed_response(b"<!doctype html><title>Denied</title>", "text/html")

    def test_xml_is_accepted_from_a_misconfigured_server(self):
        validate_feed_response(b"<?xml version='1.0'?><rss/>", "text/plain")

    def test_wrong_non_xml_content_type_is_rejected(self):
        with self.assertRaisesRegex(FeedResponseError, "image/png"):
            validate_feed_response(b"not a feed", "image/png")

    def test_retry_after_supports_seconds_and_http_date(self):
        now = datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(parse_retry_after("120", now), 120)
        self.assertEqual(
            parse_retry_after("Thu, 03 Sep 2026 12:02:00 GMT", now), 120
        )
        self.assertIsNone(parse_retry_after("soon", now))


class FeedMemoryTests(unittest.TestCase):
    def make_viewer(self):
        viewer = object.__new__(RSSViewer)
        viewer.feed_url = ""
        viewer.active_feed_title = ""
        viewer.saved_feeds = []
        viewer.forgotten_feed_urls = set()
        viewer.save_settings = lambda: None
        return viewer

    def test_feed_title_replaces_fallback_label(self):
        viewer = self.make_viewer()
        viewer.remember_feed("https://example.com/rss")
        viewer.remember_feed("https://example.com/rss", "Example News")

        self.assertEqual(viewer.saved_feeds, [{
            "url": "https://example.com/rss",
            "label": "Example News",
            "stale_alert": False,
        }])

    def test_feed_memory_has_no_application_limit(self):
        viewer = self.make_viewer()
        for index in range(250):
            viewer.remember_feed(
                f"https://example.com/feed/{index}", f"Feed {index}"
            )

        self.assertEqual(len(viewer.saved_feeds), 250)

    def test_dropdown_uses_feed_names_without_urls(self):
        choices = saved_feed_choices([
            {"url": "https://one.example/feed", "label": "Daily News"},
            {"url": "https://two.example/feed", "label": "Daily News"},
            {"url": "https://radio.example/rss", "label": "Radio Updates"},
        ])

        self.assertEqual(
            list(choices), ["Daily News", "Daily News (2)", "Radio Updates"]
        )
        self.assertNotIn("https://", " ".join(choices))

    def test_deleted_feed_is_not_automatically_remembered(self):
        viewer = self.make_viewer()
        url = "https://example.com/rss"
        viewer.forgotten_feed_urls.add(url)

        viewer.remember_feed(url, "Example News")

        self.assertEqual(viewer.saved_feeds, [])

    def test_stale_alert_is_configured_per_feed(self):
        viewer = self.make_viewer()
        viewer.remember_feed(
            "https://example.com/rss", "Example News", stale_alert=True
        )

        self.assertTrue(viewer.feed_stale_alert_enabled("https://example.com/rss"))
        self.assertFalse(viewer.feed_stale_alert_enabled("https://other.example/rss"))

    def test_stale_alert_thresholds(self):
        now = datetime.now(timezone.utc)

        self.assertIsNone(stale_feed_alert(now - timedelta(minutes=20), False, now))
        self.assertIsNone(stale_feed_alert(now - timedelta(seconds=299), True, now))
        self.assertEqual(
            stale_feed_alert(now - timedelta(minutes=5), True, now),
            (STALE_WARNING_COLOR, 0.5),
        )
        self.assertEqual(
            stale_feed_alert(now - timedelta(minutes=10), True, now),
            (STALE_CRITICAL_COLOR, 0.5),
        )
        self.assertEqual(
            stale_feed_alert(now - timedelta(minutes=15), True, now),
            (STALE_CRITICAL_COLOR, 0.25),
        )

    def test_status_display_uses_feed_title_instead_of_url(self):
        viewer = self.make_viewer()
        viewer.feed_url = "https://example.com/very/long/feed/address.xml"
        viewer.saved_feeds = [{
            "url": viewer.feed_url,
            "label": "Example News",
            "stale_alert": False,
        }]

        self.assertEqual(viewer.feed_display_name(), "Example News")
        self.assertNotIn("https://", viewer.feed_display_name())


class SettingsRecoveryTests(unittest.TestCase):
    def test_invalid_fields_do_not_discard_valid_saved_feeds(self):
        settings = {
            "feed_url": "https://example.com/rss",
            "contact_email": "not-an-email",
            "refresh_seconds": "invalid",
            "theme": "Missing Theme",
            "geometry": "broken",
            "saved_feeds": [{
                "url": "https://example.com/rss",
                "label": "Keep Me",
                "stale_alert": True,
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps(settings), encoding="utf-8")
            viewer = object.__new__(RSSViewer)
            viewer.feed_url = ""
            viewer.active_feed_title = ""
            viewer.contact_email = ""
            viewer.refresh_seconds = simple_rss.DEFAULT_REFRESH_SECONDS
            viewer.theme_name = simple_rss.DEFAULT_THEME
            viewer.saved_feeds = []
            viewer.forgotten_feed_urls = set()
            viewer.settings_warnings = []
            viewer.geometry = lambda _value: None

            with patch.object(simple_rss, "CONFIG_PATH", str(path)):
                viewer.load_settings()

        self.assertEqual(viewer.feed_url, "https://example.com/rss")
        self.assertEqual(viewer.saved_feeds[0]["label"], "Keep Me")
        self.assertTrue(viewer.saved_feeds[0]["stale_alert"])
        self.assertEqual(viewer.contact_email, "")
        self.assertGreaterEqual(len(viewer.settings_warnings), 4)


if __name__ == "__main__":
    unittest.main()
