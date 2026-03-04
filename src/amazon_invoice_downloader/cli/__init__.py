# SPDX-FileCopyrightText: 2023-present David C Wang <dcwangmit01@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Amazon Invoice Downloader

Usage:
  amazon-invoice-downloader.py \
    [--email=<email> --password=<password>] \
    [--year=<YYYY> | --date-range=<YYYYMMDD-YYYYMMDD>]
  amazon-invoice-downloader.py (-h | --help)
  amazon-invoice-downloader.py (-v | --version)

Login Options:
  --email=<email>          Amazon login email  [default: $AMAZON_EMAIL].
  --password=<password>    Amazon login password  [default: $AMAZON_PASSWORD].

Date Range Options:
  --date-range=<YYYYMMDD-YYYYMMDD>  Start and end date range
  --year=<YYYY>                     Year, formatted as YYYY  [default: <CUR_YEAR>].

Options:
  -h --help                Show this screen.
  -v --version             Show version.

Examples:
  amazon-invoice-downloader.py --year=2022  # Uses .env file or env vars $AMAZON_EMAIL and $AMAZON_PASSWORD
  amazon-invoice-downloader.py --date-range=20220101-20221231
  amazon-invoice-downloader.py --email=user@example.com --password=secret  # Defaults to current year
  amazon-invoice-downloader.py --email=user@example.com --password=secret --year=2022
  amazon-invoice-downloader.py --email=user@example.com --password=secret --date-range=20220101-20221231

Features:
  - Remote debugging enabled on port 9222 for AI MCP Servers
  - Virtual authenticator configured to prevent passkey dialogs
  - Stealth mode enabled to avoid detection

Credential Precedence:
  1. Command line arguments (--email, --password)
  2. Environment variables ($AMAZON_EMAIL, $AMAZON_PASSWORD)
  3. .env file (automatically loaded if env vars not set)
"""

import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from docopt import docopt
from dotenv import load_dotenv
from playwright.sync_api import TimeoutError, sync_playwright
from playwright_stealth import Stealth

from ..__about__ import __version__


def load_env_if_needed():
    """Load environment variables from .env file if it exists and variables aren't set."""
    # Check if Amazon credentials are already set in environment
    amazon_email = os.environ.get('AMAZON_EMAIL')
    amazon_password = os.environ.get('AMAZON_PASSWORD')

    # If both are already set, no need to load .env
    if amazon_email and amazon_password:
        return

    # Look for .env file in current directory and parent directories
    current_dir = Path.cwd()
    env_file = None

    # Check current directory and up to 3 parent directories
    for i in range(4):
        check_path = current_dir / '.env'
        if check_path.exists():
            env_file = check_path
            break
        current_dir = current_dir.parent

    if env_file:
        print(f"Loading environment variables from {env_file}")
        load_dotenv(env_file)
    else:
        print("No .env file found in current directory or parent directories")


def sleep():
    # Add human latency
    # Generate a random sleep time between 3 and 5 seconds
    sleep_time = random.uniform(2, 5)
    # Sleep for the generated time
    time.sleep(sleep_time)


def run(playwright, args):
    email = args.get("--email")
    if email == "$AMAZON_EMAIL":
        email = os.environ.get("AMAZON_EMAIL")

    password = args.get("--password")
    if password == "$AMAZON_PASSWORD":
        password = os.environ.get("AMAZON_PASSWORD")

    # Parse date ranges int start_date and end_date
    if args["--date-range"]:
        start_date, end_date = args["--date-range"].split("-")
    elif args["--year"] != "<CUR_YEAR>":
        start_date, end_date = args["--year"] + "0101", args["--year"] + "1231"
    else:
        year = str(datetime.now().year)
        start_date, end_date = year + "0101", year + "1231"
    start_date = datetime.strptime(start_date, "%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y%m%d")

    # Ensure the location exists for where we will save our downloads
    target_dir = os.getcwd() + "/" + "downloads"
    os.makedirs(target_dir, exist_ok=True)

    # Create Playwright context with Chromium
    # Always use CDP for virtual authenticator and remote debugging
    print("🚀 Launching Chromium with CDP debugging on port 9222")
    print("📱 You can connect to this browser at: http://localhost:9222")
    print("🔗 AI assistant can control this browser instance via CDP")

    # Launch browser with CDP endpoint
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            '--remote-debugging-port=9222',
            '--remote-debugging-address=0.0.0.0',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
        ],
    )

    # Connect to the browser using CDP
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")

    # Create context and page
    context = browser.new_context()
    page = context.new_page()

    # Set up virtual authenticator to prevent passkey dialogs
    print("🔐 Setting up virtual authenticator to disable passkeys")
    try:
        client = page.context.new_cdp_session(page)
        client.send("WebAuthn.enable")
        client.send(
            "WebAuthn.addVirtualAuthenticator",
            {
                "options": {
                    "protocol": "ctap2",
                    "transport": "internal",
                    "hasResidentKey": True,
                    "hasUserVerification": True,
                    "isUserVerified": True,
                    "automaticPresenceSimulation": True,
                }
            },
        )
        print("✅ Virtual authenticator configured successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not configure virtual authenticator: {e}")

    Stealth().apply_stealth_sync(page)

    # Navigate directly to order history - Amazon redirects to login if needed
    page.goto("https://www.amazon.de/gp/css/order-history")
    page.wait_for_load_state("domcontentloaded")
    sleep()

    # Try to login if redirected to sign-in page
    email_field = page.query_selector('#ap_email')
    if email_field and email:
        email_field.fill(email)
        continue_btn = page.query_selector('#continue')
    # Handle login - credentials from .env or manual entry
    # If on signin page, try auto-fill; otherwise user logs in manually
    try:
        email_field = page.query_selector('#ap_email')
        if email_field and email:
            email_field.fill(email)
            cont = page.query_selector('#continue')
            if cont:
                cont.click()
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)
    except Exception:
        pass

    try:
        pw_field = page.query_selector('#ap_password')
        if pw_field and password:
            pw_field.fill(password)
            signin = page.query_selector('#signInSubmit')
            if signin:
                signin.click()
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)
    except Exception:
        pass

    # Wait until we leave any auth/login page (2FA, CAPTCHA, signin)
    print(f"📍 URL after login attempt: {page.url}")
    auth_pages = ['ap/mfa', 'ap/cvf', 'ap/challenge', 'ap/signin', 'ap/forgotpassword', 'ax/claim']
    printed_msg = False
    waited = 0
    while waited < 300:
        try:
            current_url = page.evaluate("window.location.href")
        except Exception:
            try:
                current_url = page.url
            except Exception:
                current_url = ""
        if not any(x in current_url for x in auth_pages):
            break
        if not printed_msg:
            print("🔐 Auth/Login page detected - please complete in browser...")
            printed_msg = True
        time.sleep(3)
        waited += 3
    print(f"✅ Auth complete (URL: {page.url})")

    # Navigate to order history
    page.goto("https://www.amazon.de/your-orders/orders")
    page.wait_for_load_state("domcontentloaded")
    time.sleep(5)
    print(f"📍 Orders page: {page.url}")

    # Get a list of years from the select options - try multiple selectors
    select = (
        page.query_selector("select#time-filter")
        or page.query_selector("select#orderFilter")
        or page.query_selector("select[name='timeFilter']")
        or page.query_selector("select[name='orderFilter']")
    )
    if not select:
        print("⚠️ Time filter not found. Debugging page...")
        print(f"  Page title: {page.title()}")
        print(f"  URL: {page.url}")
        all_selects = page.query_selector_all("select")
        print(f"  Found {len(all_selects)} select elements:")
        for i, s in enumerate(all_selects):
            try:
                sid = s.get_attribute('id') or 'no-id'
                sname = s.get_attribute('name') or 'no-name'
                stext = s.inner_text()[:200].replace('\n', ' | ')
                print(f"    [{i}] id={sid}, name={sname}, options={stext}")
            except Exception as e:
                print(f"    [{i}] error reading: {e}")
        raise Exception("Could not find time filter - see debug output above")
    years = select.inner_text().split("\n")  # skip the first two text options

    # Filter years to include only numerical years (YYYY)
    years = [year for year in years if year.isnumeric()]

    # Filter years to the include only the years between start_date and end_date inclusively
    years = [year for year in years if start_date.year <= int(year) <= end_date.year]
    years.sort(reverse=True)

    # Year Loop (Run backwards through the time range from years to pages to orders)
    for year in years:
        # Select the year in the order filter
        print(f"🔍 Selecting year: year-{year}")
        try:
            select.select_option(value=f"year-{year}")
            time.sleep(3)
            print(f"📍 After filter: {page.evaluate('window.location.href')}")
        except Exception as e:
            print(f"❌ Select failed: {e}")
            # Fallback: navigate directly
            page.goto(f"https://www.amazon.de/your-orders/orders?timeFilter=year-{year}")
            time.sleep(5)
            print(f"📍 After direct nav: {page.evaluate('window.location.href')}")
        sleep()

        # Page Loop - URL-based pagination (Weiter-Button unreliable on amazon.de)
        page_index = 0
        while True:
            if page_index > 0:
                page_url = f"https://www.amazon.de/your-orders/orders?timeFilter=year-{year}&startIndex={page_index}"
                print(f"  📄 Loading page: startIndex={page_index}")
                page.goto(page_url)
                sleep()

            # Check if we have order cards on this page
            order_cards_check = page.query_selector_all(".order-card.js-order-card")
            if not order_cards_check:
                print(f"  ✅ No more orders found at startIndex={page_index}")
                break
            print(f"  📦 Found {len(order_cards_check)} orders on page (startIndex={page_index})")

            # Order Loop
            order_cards = page.query_selector_all(".order-card.js-order-card")
            for order_card in order_cards:
                # Parse the order card to create the date and file_name
                spans = order_card.query_selector_all("span")
                # Debug:
                # for i,s in enumerate(spans): print(f"  span[{i}]: {s.inner_text()[:80]}")

                # Skip cancelled orders
                if spans[4].inner_text().strip().lower() in ["cancelled", "storniert"]:
                    continue

                # Parse German date format (e.g. "1. Januar 2025")
                date_text = spans[1].inner_text().strip()
                try:
                    date = datetime.strptime(date_text, "%B %d, %Y")
                except ValueError:
                    try:
                        # German: "1. Januar 2025" or "01. Januar 2025"
                        months_de = {
                            "Januar": 1,
                            "Februar": 2,
                            "März": 3,
                            "April": 4,
                            "Mai": 5,
                            "Juni": 6,
                            "Juli": 7,
                            "August": 8,
                            "September": 9,
                            "Oktober": 10,
                            "November": 11,
                            "Dezember": 12,
                        }
                        parts = date_text.replace(".", "").split()
                        day = int(parts[0])
                        month = months_de.get(parts[1], 1)
                        year_val = int(parts[2])
                        date = datetime(year_val, month, day)
                    except Exception:
                        print(f"⚠️ Could not parse date: {date_text}, skipping")
                        continue
                total = (
                    spans[3].inner_text().replace("EUR", "").replace("€", "").replace(".", "").replace(",", ".").strip()
                )  # handle EUR format
                orderid = spans[8].inner_text()
                date_str = date.strftime("%Y%m%d")
                # Sanitize orderid: remove newlines, limit length
                orderid = orderid.replace("\n", " ").strip()[:60]
                orderid = "".join(c for c in orderid if c.isalnum() or c in " -_").strip()
                file_name = f"{target_dir}/{date_str}_{total}_amazon_{orderid}.pdf"

                if date > end_date:
                    continue
                elif date < start_date:
                    done = True
                    break

                if os.path.isfile(file_name):
                    print(f"File [{file_name}] already exists")
                else:
                    print(f"Saving file [{file_name}]")
                    # Save - find invoice link (German: "Rechnung", English: "View invoice")
                    invoice_link = (
                        order_card.query_selector('xpath=//a[contains(text(), "Rechnung")]')
                        or order_card.query_selector('xpath=//a[contains(text(), "View invoice")]')
                        or order_card.query_selector('xpath=//a[contains(text(), "Invoice")]')
                    )
                    if not invoice_link:
                        print(f"  ⚠️ No invoice link found for order {file_name}, skipping")
                        continue
                    href = invoice_link.get_attribute("href")
                    if href.startswith("http"):
                        link = href
                    else:
                        link = "https://www.amazon.de/" + href
                    invoice_page = context.new_page()
                    invoice_page.goto(link)
                    time.sleep(3)
                    # Amazon shows intermediate dialog with "Rechnung" / "Bestellübersicht"
                    # We need to click the actual "Rechnung" link on that page
                    try:
                        invoice_btn = (
                            invoice_page.query_selector('a:has-text("Rechnung")')
                            or invoice_page.query_selector('a[href*="invoice"]')
                        )
                        if invoice_btn:
                            invoice_btn.click()
                            time.sleep(3)
                    except Exception as e:
                        print(f"  ⚠️ Could not click invoice link on intermediate page: {e}")
                    invoice_page.pdf(
                        path=file_name,
                        format="A4",
                        margin={"top": ".5in", "right": ".5in", "bottom": ".5in", "left": ".5in"},
                    )
                    invoice_page.close()
                    print(f"  ✅ Saved!")

            # Next page
            page_index += 10

    # Close the browser
    context.close()
    browser.close()


def amazon_invoice_downloader():
    # Load environment variables from .env file if needed
    load_env_if_needed()

    args = docopt(__doc__)
    # print(args)
    if args['--version']:
        print(__version__)
        sys.exit(0)

    with sync_playwright() as playwright:
        run(playwright, args)
