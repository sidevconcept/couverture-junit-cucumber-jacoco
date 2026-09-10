from playwright.sync_api import sync_playwright

SHOTS = "/private/tmp/claude-501/-Users-sidneycohen-dev-projects-couverture-code/89c0d7fe-4ceb-4392-ac42-22a8c714d66f/scratchpad/screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 1000})

    page.goto("http://localhost:9000/sessions/new")
    page.fill('input[name="login"]', "admin")
    page.fill('input[name="password"]', "DemoConf2026!")
    page.click('button[type="submit"]')
    page.wait_for_timeout(1500)
    if page.locator('input[name="password"]').count() > 0:
        # le mot de passe n'a pas encore ete change sur cette instance
        page.fill('input[name="login"]', "admin")
        page.fill('input[name="password"]', "admin")
        page.click('button[type="submit"]')
        page.wait_for_timeout(2500)

    if page.get_by_text("Update your password").count() > 0:
        pwd_inputs = page.locator('input[type="password"]')
        pwd_inputs.nth(0).fill("admin")
        pwd_inputs.nth(1).fill("DemoConf2026!")
        pwd_inputs.nth(2).fill("DemoConf2026!")
        page.get_by_role("button", name="Update").click()
        page.wait_for_timeout(2500)

    def dismiss_clutter():
        for sel in [
            'button:has-text("Dismiss")',
            'button[aria-label="Dismiss"]',
            '.alert .icon-close',
            'button:has-text("close")',
        ]:
            loc = page.locator(sel)
            if loc.count() > 0:
                try:
                    loc.first.click(timeout=1000)
                    page.wait_for_timeout(300)
                except Exception:
                    pass
        # ferme le bandeau jaune "embedded database" (bouton X generique dans l'alert)
        alert_close = page.locator('.js-dismiss-message, [data-testid="dismiss-message"]')
        if alert_close.count() > 0:
            try:
                alert_close.first.click(timeout=1000)
            except Exception:
                pass

    page.goto("http://localhost:9000/dashboard?id=couverture-code")
    page.wait_for_timeout(2500)
    dismiss_clutter()
    page.wait_for_timeout(500)
    page.screenshot(path=f"{SHOTS}/sonar-overview.png")
    print("saved overview")

    page.goto("http://localhost:9000/component_measures?id=couverture-code&metric=coverage&view=list")
    page.wait_for_timeout(2500)
    dismiss_clutter()
    page.wait_for_timeout(500)
    page.screenshot(path=f"{SHOTS}/sonar-coverage-list.png")
    print("saved coverage list")

    page.goto("http://localhost:9000/code?id=couverture-code&selected=couverture-code%3Asrc%2Fmain%2Fjava%2Fcom%2Fsidev%2Fagenda%2Fservice%2FRecurrenceService.java")
    page.wait_for_timeout(2500)
    dismiss_clutter()
    page.get_by_text("MENSUELLE ->").first.scroll_into_view_if_needed()
    page.wait_for_timeout(600)
    page.mouse.wheel(0, -150)
    page.wait_for_timeout(400)
    page.screenshot(path=f"{SHOTS}/sonar-code-drilldown.png")
    print("saved code drilldown")

    browser.close()
