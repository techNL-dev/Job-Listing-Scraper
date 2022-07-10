from http.server import BaseHTTPRequestHandler
from scrape import scrape_listings


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        listing_count = scrape_listings()
        self.wfile.write(f"Scraped {listing_count} job listings")
        return
