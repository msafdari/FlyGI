"""Render the authored social cards. Requires Python Playwright and Chromium."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT / 'exports'

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={'width': 1200, 'height': 1500}, device_scale_factor=1)
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('file:') else route.abort())
    page.goto((ROOT / 'carousel.html').as_uri())
    page.evaluate('document.fonts.ready')
    page.wait_for_function('Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)')
    EXPORTS.mkdir(exist_ok=True)
    for index in range(1, 8):
        identifier = f'slide-{index}' if index < 7 else 'story'
        element = page.locator('#' + identifier)
        issues = element.evaluate('''element => {
            const edge = element.getBoundingClientRect();
            const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
            const issues = [];
            let node;
            while (node = walker.nextNode()) {
                if (!node.textContent.trim()) continue;
                const range = document.createRange(); range.selectNodeContents(node);
                for (const rect of range.getClientRects()) {
                    if (rect.left < edge.left || rect.right > edge.right || rect.top < edge.top || rect.bottom > edge.bottom)
                        issues.push(node.textContent.trim());
                }
            }
            return issues;
        }''')
        if issues:
            raise ValueError(f'{identifier} has clipped text: {issues}')
        filename = f'{index:02d}-flygi.jpg' if index < 7 else 'story-teaser.jpg'
        element.screenshot(path=EXPORTS / filename, type='jpeg', quality=96, animations='disabled')
        print(filename, flush=True)
    # The preview uses the finished cards at phone scale. It does not alter the source artwork.
    tiles = ''.join(f'<img src="{(EXPORTS / f"{index:02d}-flygi.jpg").as_uri()}">' for index in range(1, 7))
    page.set_content('<style>body{margin:0;padding:12px;background:#172323;display:grid;grid-template-columns:repeat(3,360px);gap:12px}img{width:360px;height:450px}</style>' + tiles)
    page.wait_for_function('Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)')
    page.set_viewport_size({'width': 1128, 'height': 936})
    page.screenshot(path=EXPORTS / 'preview.jpg', type='jpeg', quality=95, full_page=True)
    browser.close()
