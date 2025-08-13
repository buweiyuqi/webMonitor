# Hermès Product Scraping Guide

## Overview
This package provides multiple approaches to scrape product information from the Hermès website and save it to Excel format.

## Files Included

1. **hermes_simple_scraper.py** - Basic scraper using urllib and regex
2. **hermes_selenium_scraper.py** - Advanced scraper using Selenium for JavaScript-heavy sites
3. **hermes_scraper.py** - Comprehensive scraper with multiple strategies
4. **requirements.txt** - Required Python packages

## Installation

### Option 1: Basic Setup (No Browser Required)
```bash
# Install basic packages
pip3 install requests beautifulsoup4 pandas openpyxl lxml

# Run simple scraper
python3 hermes_simple_scraper.py
```

### Option 2: Advanced Setup (Recommended for Hermès)
```bash
# Install Selenium and ChromeDriver
pip3 install selenium webdriver-manager

# On macOS:
brew install chromedriver

# Run advanced scraper
python3 hermes_selenium_scraper.py
```

## Usage

### Method 1: Basic Scraping
```bash
python3 hermes_simple_scraper.py
```

### Method 2: Selenium Scraping (Recommended)
```bash
python3 hermes_selenium_scraper.py
```

### Method 3: Manual Browser + Scraping
1. Open the Hermès website in your browser
2. Save the page as HTML
3. Run the scraper on the saved HTML

## Output Files

The scrapers will create:
- `hermes_products_[timestamp].csv` - Excel-compatible CSV file
- `hermes_products_[timestamp].json` - Raw JSON backup

## Data Extracted

Each product will include:
- **Product Name** - Full product name
- **Price** - Product price
- **Currency** - Currency (HKD, USD, etc.)
- **Image URL** - Product image link
- **Product URL** - Direct link to product page
- **Description** - Product description
- **Availability** - In stock/out of stock
- **Colors** - Available colors
- **Sizes** - Available sizes
- **Category** - Product category

## Troubleshooting

### Common Issues

1. **Access Denied / 403 Error**
   - Use Selenium scraper instead of basic scraper
   - Add delays between requests
   - Use different user-agent strings

2. **No Products Found**
   - Check if the website structure has changed
   - Try different selectors in the code
   - Ensure JavaScript content is loaded

3. **ChromeDriver Issues**
   - Ensure ChromeDriver version matches your Chrome browser
   - Add ChromeDriver to system PATH
   - Use webdriver-manager for automatic updates

### Manual Alternative

If automated scraping fails:

1. **Manual Data Collection**
   - Browse the website manually
   - Copy product information
   - Use browser dev tools to inspect elements

2. **Browser Extension Method**
   - Use "Web Scraper" Chrome extension
   - Install "DataMiner" or similar extensions
   - Export data directly from browser

## Hermès Website Structure

The Hermès website typically uses:
- Product containers: `<article>` tags
- Product names: `<h3>` or `<h2>` tags
- Prices: `<span class="price">` or similar
- Images: `<img>` tags within product containers
- Links: `<a>` tags linking to product detail pages

## Legal Considerations

- **Respect robots.txt** - Check site policies
- **Rate limiting** - Don't overwhelm the server
- **Terms of Service** - Ensure compliance with website TOS
- **Personal use only** - Don't use for commercial redistribution

## Example Output

```csv
name,price,currency,availability,category,description,colors,sizes,image_url,product_url
"Hermès Birkin 30","85000","HKD","In Stock","Bags","Classic leather handbag","Gold, Black, Etoupe","30cm","https://...","https://..."
"Hermès Kelly 28","78000","HKD","In Stock","Bags","Iconic Kelly bag","Rouge, Noir, Etoupe","28cm","https://...","https://..."
```

## Support

If you encounter issues:
1. Check the error messages
2. Try different scraping methods
3. Update selectors based on current website structure
4. Use browser dev tools to inspect current page structure