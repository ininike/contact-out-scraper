# ContactOutScraper

A Python tool for automated scraping of public profile data from [ContactOut](https://contactout.com) using Selenium and BeautifulSoup.

## Features

- Automates login and session management with cookies
- Searches for people by name and scrapes multiple pages of results
- Extracts profile details: name, profile picture, LinkedIn, GitHub, Twitter, Facebook URLs, and location
- Headless Chrome browser for efficient, invisible scraping

## Requirements

- Python 3.7+
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)
- [Selenium](https://pypi.org/project/selenium/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)

## Installation

1. **Clone this repository** or copy the script to your project folder.

2. **Install dependencies:**
   ```sh
   pip install selenium beautifulsoup4
   ```

3. **Download ChromeDriver:**
   - [Get ChromeDriver here](https://sites.google.com/a/chromium.org/chromedriver/downloads)
   - Place the `chromedriver.exe` in your PATH or the same directory as the script.

## Usage

1. **Edit your credentials:**

   In `contactout_scraper.py`, replace:
   ```python
   email = "YOUR WORK EMAIL"
   password = "PASSWORD"
   ```

2. **Run the script:**
   ```sh
   python contactout_scraper.py
   ```

3. **Example output:**
   ```
   {'profile_pic': 'https://...', 'name': 'John Doe', 'linkedin_profile_url': 'https://linkedin.com/in/...', ...}
   ```

## How it Works

- The script logs into ContactOut using your credentials.
- It performs a search for the specified name.
- It scrapes the specified number of result pages, clicking "Next" and "Load More" as needed.
- Extracted data includes profile picture, name, social links, and location.

## Notes

- **This tool is for educational and research purposes only.** Scraping websites may violate their terms of service. Use responsibly.
- Your credentials are stored only in your script and cookies are saved locally for session reuse.
- For best results, ensure your ChromeDriver and Chrome browser versions match.

## File Structure

```
contactout_scraper.py
README.md
```

## License

MIT License

---

**Disclaimer:** This project is not affiliated with or endorsed by ContactOut.
