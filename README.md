## Installation

Requires python 3.9.1
```bash
# Install package requirements
pip install -e .
```

### Scrape NGO
```bash
# Crawl NGOs data from GuideStar
# NOTE: We only scrape last reported year data at the moment
scrapy crawl guidestar -a ngo_ids="<ngo_id_1>,<ngo_id_2>" -O <output_file> 

```