"""Records docs/demo.gif from the live examples: open a Wonderous module, click a widget, see its
code and how it looks, follow "Appears in", open a method from an arrow, find a file's classes;
then the same popups on the native iOS (NetNewsWire) and Android (Now in Android) maps.

Usage: python record.py [base url]     (needs `pip install playwright pillow` and Google Chrome)
"""
import io
import os
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'https://yonivav.github.io/app-map/examples/wonderous/').rstrip('/') + '/'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'demo.gif')
WIDTH, HEIGHT, GIF_WIDTH = 1280, 760, 960
CAPTION = """
(text) => {
  let bar = document.getElementById('demo-caption');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'demo-caption';
    bar.style.cssText = 'position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:99999;' +
      'background:#36169d;color:#fff;font:600 20px "IBM Plex Sans",system-ui,sans-serif;' +
      'padding:10px 20px;border-radius:999px;box-shadow:0 10px 30px rgba(0,0,0,.45);white-space:nowrap';
    document.body.appendChild(bar);
  }
  bar.textContent = text;
}
"""

frames = []  # (image, milliseconds)


def shot(page, ms=160):
    image = Image.open(io.BytesIO(page.screenshot())).convert('RGB')
    image = image.resize((GIF_WIDTH, round(image.height * GIF_WIDTH / image.width)), Image.LANCZOS)
    frames.append((image, ms))


def hold(page, ms):
    shot(page, ms)


def caption(page, text):
    page.evaluate(CAPTION, text)


def glide(page, target_y, steps=10):
    """Scrolls smoothly to a page offset, one frame per step."""
    start = page.evaluate('window.scrollY')
    for index in range(1, steps + 1):
        page.evaluate('(y) => window.scrollTo(0, y)', start + (target_y - start) * index / steps)
        page.wait_for_timeout(40)
        shot(page, 70)


def center_of(page, selector_js):
    box = page.evaluate(selector_js)
    return box['x'], box['y']


def element_y(page, text):
    return page.evaluate("""(text) => {
      const el = [...document.querySelectorAll('.code-link')].find((e) => e.textContent.trim() === text);
      const r = el.getBoundingClientRect();
      return window.scrollY + r.top - innerHeight / 2 + r.height / 2;
    }""", text)


def click_link(page, text):
    point = page.evaluate("""(text) => {
      const el = [...document.querySelectorAll('.code-link')].find((e) => e.textContent.trim() === text);
      const r = el.getBoundingClientRect();
      return {x: r.x + r.width / 2, y: r.y + r.height / 2};
    }""", text)
    page.mouse.move(point['x'], point['y'], steps=8)
    shot(page, 300)
    page.mouse.click(point['x'], point['y'])
    # The first popup on a page loads the highlighter first; wait until it's really open.
    page.wait_for_selector('dialog.code-pop[open]', timeout=15000)
    page.wait_for_timeout(500)


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='chrome')
        page = browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT}, color_scheme='dark')

        # 1. The overview: one card per module.
        page.goto(BASE + 'index.html', wait_until='networkidle')
        page.evaluate("document.querySelectorAll('img').forEach((i) => i.loading = 'eager')")
        page.wait_for_timeout(2500)
        caption(page, 'Your agent maps the app: one page per module')
        hold(page, 2200)

        # 2. A module page, down to its widget diagram.
        card = page.locator('a[href="artifacts.html"]')
        card.hover()
        shot(page, 400)
        card.click()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2500)
        caption(page, 'UML drawn from the real code')
        hold(page, 1200)
        glide(page, element_y(page, '_DoubleBorderImage'), steps=14)
        hold(page, 800)

        # 3. A widget: how it looks, and its exact code.
        caption(page, 'Click a widget: how it looks + its exact code')
        click_link(page, '_DoubleBorderImage')
        hold(page, 3200)
        page.keyboard.press('Escape')
        page.wait_for_timeout(400)

        # 4. A class used across modules: "Appears in".
        glide(page, element_y(page, 'SettingsLogic'), steps=10)
        caption(page, 'Code → map: every place a class appears')
        click_link(page, 'SettingsLogic')
        hold(page, 2800)
        link = page.locator('dialog.code-pop .appears a', has_text='Home menu: Logic')
        box = link.bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2, steps=8)
        shot(page, 400)
        link.click()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2500)
        hold(page, 1200)

        # 5. An arrow's label opens the method it names.
        caption(page, 'Click an arrow: the method it calls')
        click_link(page, 'changeLocale()')
        hold(page, 3000)
        page.keyboard.press('Escape')

        # 6. Find any class or file.
        page.goto(BASE + 'index.html', wait_until='networkidle')
        page.wait_for_timeout(1500)
        search = page.locator('section.find input')
        search.scroll_into_view_if_needed()
        page.evaluate('window.scrollBy(0, -60)')
        caption(page, 'Find any class or file in the map')
        search.click()
        for char in 'timeline_logic.dart':
            search.type(char)
            shot(page, 70)
        hold(page, 2600)

        # 7. Native apps too: the same popups on an iOS and an Android map.
        root = BASE.split('examples/')[0]
        for url, name, text in [
            ('examples/netnewswire/main-timeline.html', 'MainTimelineCell', 'Native iOS too: Swift and Objective-C'),
            ('examples/now-in-android/topic.html', 'TopicHeader', 'And Android: Kotlin and Jetpack Compose'),
        ]:
            page.goto(root + url, wait_until='networkidle')
            page.wait_for_timeout(2000)
            page.evaluate('(y) => window.scrollTo(0, y)', element_y(page, name))
            page.wait_for_timeout(300)
            caption(page, text)
            hold(page, 900)
            click_link(page, name)
            hold(page, 2800)
            page.keyboard.press('Escape')
        browser.close()

    first, *rest = [image for image, _ in frames]
    palette = first.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    images = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image, _ in frames]
    images[0].save(OUT, save_all=True, append_images=images[1:], duration=[ms for _, ms in frames],
                   loop=0, optimize=True, disposal=1)
    print(f'{OUT}: {len(frames)} frames, {os.path.getsize(OUT) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
