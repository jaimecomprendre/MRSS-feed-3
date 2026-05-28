 
import os
import mimetypes
import xml.etree.ElementTree as ET
from xml.dom import minidom
 
# --- Configuration ---
MEDIA_DIR = "media"                          # Path to your media folder (relative to this script)
OUTPUT_FILE = "feed.xml"                     # Output path for the generated feed
BASE_URL = "https://jaimecomprendre.github.io/MRSS-feed-3"  # Base URL of your GitHub Pages site
FEED_TITLE = "Auto Signage Feed"
 
SUPPORTED_EXTENSIONS = {
    ".jpg":  ("image/jpeg", "image"),
    ".jpeg": ("image/jpeg", "image"),
    ".png":  ("image/png",  "image"),
    ".mp4":  ("video/mp4",  "video"),
}
# ---------------------
 
 
def get_file_size(filepath: str) -> int:
    """Return file size in bytes, or 0 if the file doesn't exist."""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0
 
 
def slugify_guid(filename: str, index: int) -> str:
    """Generate a stable GUID from the filename stem + index."""
    stem = os.path.splitext(filename)[0].lower().replace(" ", "_")
    return f"{stem}_{index:04d}"
 
 
def build_feed(media_dir: str, base_url: str, feed_title: str) -> str:
    """Scan media_dir and return the feed.xml content as a string."""
 
    # Register the media RSS namespace
    ET.register_namespace("media", "http://search.yahoo.com/mrss/")
 
    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:media": "http://search.yahoo.com/mrss/",
    })
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = feed_title
 
    # Collect and sort files for a stable, predictable order
    try:
        filenames = sorted(os.listdir(media_dir))
    except FileNotFoundError:
        raise SystemExit(f"[ERROR] Media directory not found: '{media_dir}'")
 
    item_count = 0
    for filename in filenames:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue  # Skip unsupported files
 
        mime_type, medium = SUPPORTED_EXTENSIONS[ext]
        file_url = f"{base_url}/media/{filename}"
        filepath = os.path.join(media_dir, filename)
        file_size = get_file_size(filepath)
        item_count += 1
        guid = slugify_guid(filename, item_count)
 
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = filename
        ET.SubElement(item, "link").text = file_url
        ET.SubElement(item, "description").text = file_url
        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = guid
        ET.SubElement(item, "medium").text = medium
 
        ET.SubElement(item, "media:content", {
            "url":      file_url,
            "fileSize": str(file_size),
            "type":     mime_type,
            "medium":   medium,
        })
 
    if item_count == 0:
        print("[WARNING] No supported media files found in the media folder.")
 
    # Pretty-print
    raw_xml = ET.tostring(rss, encoding="unicode", xml_declaration=False)
    dom = minidom.parseString(raw_xml)
    pretty = dom.toprettyxml(indent="  ", encoding=None)
    # minidom adds its own XML declaration; replace it with the standard one
    lines = pretty.split("\n")
    lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
    return "\n".join(lines)
 
 
def main():
    print(f"[INFO] Scanning '{MEDIA_DIR}' ...")
    feed_content = build_feed(MEDIA_DIR, BASE_URL, FEED_TITLE)
 
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(feed_content)
 
    print(f"[OK]   '{OUTPUT_FILE}' written successfully.")
 
 
if __name__ == "__main__":
    main()