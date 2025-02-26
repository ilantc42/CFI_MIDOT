# CFI_MIDOT NGO Data Processing Tool

A Python-based toolkit for scraping, processing, and analyzing NGO (Non-Governmental Organization) data with integration to Google Sheets.

## Features

- Web scraping of NGO data using Scrapy
- Data processing and standardization
- Google Sheets integration for data export

## Installation

```bash
make setup
```

## Project Structure

```
CFI_MIDOT/
├── src/
│   └── ngo_toolkit/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py          # Configuration settings
│       │   └── constants.py         # Project constants
│       ├── scrapers/
│       │   ├── __init__.py
│       │   └── cfi_midot_scrapy/
│       │       ├── __init__.py
│       │       ├── spiders/         # Scrapy spiders
│       │       ├── items.py         # Data models
│       │       ├── middlewares.py   # Custom middlewares
│       │       ├── pipelines.py     # Data processing pipelines
│       │       └── items_loaders.py # Item loaders and processors
│       ├── uploaders/
│       │   ├── __init__.py
│       │   └── google_sheet.py      # Google Sheets integration
│       └── utils/
│           ├── __init__.py
│           ├── logger.py            # Logging configuration
│           └── helpers.py           # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_scrapers/
│   └── test_uploaders/
├── docs/
│   ├── api/
│   └── user_guide/
├── scripts/
│   └── setup_credentials.py
├── .gitignore
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE
```

This structure provides several benefits:

1. Clear Module Organization:

- `config/` - Centralized configuration management
- `scrapers/` - All scraping-related code
- `uploaders/` - Data export functionality
- `utils/` - Shared utilities and helpers

2. Testing Framework:

- Dedicated `tests/` directory matching the src structure
- Easy to run with standard test runners

3. Documentation:

- `docs/` directory for both API and user documentation
- Clear separation between technical and user guides

4. Development Tools:

- `scripts/` for utility scripts and tools
- Standard Python project files (setup.py, requirements.txt)

5. Best Practices:

- Proper Python packaging structure
- Clear import paths
- Easy to maintain and scale

This structure makes the project more maintainable, testable, and easier to contribute to.

## Usage

### 1. Data Scraping

The scraper collects NGO information including:

- Organization name
- Goals
- Year founded
- Number of volunteers
- Number of employees
- Member count
- Main activity fields
- Target audience
- Financial information

### 2. Google Sheets Integration

The toolkit provides an automatic uploader that exports the scraped data for each year to a Google Sheet.

## Configuration

1. Set up Google Sheets API credentials
2. Configure scraping parameters
3. Adjust batch processing settings as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License

Copyright (c) [year] [copyright holders]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contact

[Add Contact Information]
