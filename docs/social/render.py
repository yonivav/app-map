"""Renders docs/social.png (the repo's link preview) and docs/linkedin.png from the HTML here.

Usage: python render.py     (needs `pip install playwright` and Google Chrome)
"""
import os

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = [('social.html', 1280, 640, 'social.png'), ('linkedin.html', 1200, 627, 'linkedin.png')]

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel='chrome')
    for page_name, width, height, out in PAGES:
        page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=2)
        page.goto('file://' + os.path.join(HERE, page_name), wait_until='networkidle')
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(HERE, '..', out))
        print(out)
    browser.close()
