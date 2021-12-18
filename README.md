## Installation

Requires python 3.9.1
```bash
# Install package requirements
pip install -e .
```

### Scrape NGO
```bash
# Crawl NGO data from GuideStar
# NOTE: We only scrape last reported year data at the moment
scrapy crawl guidestar -a ngo_id=<ngo_id> -O <output_file> 

```