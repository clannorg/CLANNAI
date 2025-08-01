# CRM Lead Generation Pipeline

Clean, organized CRM workflow for identifying and contacting Veo club prospects.

## 🎯 Objective
Find and contact Northern Ireland football clubs using Veo cameras for potential sales opportunities.

## 📁 Project Structure
```
crm/
├── scripts/           # Core processing scripts
├── data/
│   ├── raw/          # Original datasets
│   ├── processed/    # Categorized/filtered data  
│   └── contacts/     # Contact information
└── logs/             # Process logs and progress files
```

## 🔄 Workflow

### 0. Original Data Collection (FOUNDATION)
**Scripts:** `scripts/veo_clubs_scraper.py`, `scripts/enhanced_scraper.py`, `scripts/infinite_scroll_scraper.py`
- ✅ **COMPLETED**: Scraped 27,676 clubs from Veo platform
- Input: Veo website club directory
- Output: `data/raw/veo_clubs_2.csv`
- Result: Complete dataset of all Veo clubs with recording counts

### 1. Club Categorization
**Script:** `scripts/categorize_clubs_by_country.py`
- ✅ **COMPLETED**: Processed 27,676 clubs using Gemini 1.5 Flash API
- Input: `data/raw/veo_clubs_2.csv` 
- Output: `data/processed/all_clubs_by_country.csv`
- Result: Successfully categorized all clubs by country

### 2. Regional Filtering  
**Script:** `scripts/filter_football_clubs.py`
- ✅ **COMPLETED**: Filtered to 65 Northern Ireland football clubs
- Input: Extracted NI clubs from categorized data
- Output: `data/contacts/ni_clubs/ni_football_clubs_only.csv`
- Excluded: Rugby, GAA, hockey, schools

### 3. Contact Scraping
**Script:** `scripts/duckduckgo_ni_scraper.py` 
- 🔄 **IN PROGRESS**: Scraping contact information
- Input: 65 NI football clubs
- Output: `data/contacts/ni_clubs/ni_clubs_with_contacts.csv`
- Status: Successfully found contacts for first few clubs, encountering timeouts

## 📊 Current Data
- **Total Veo Clubs**: 27,676 (categorized by country)
- **UK/Ireland Clubs**: ~1,000+ identified  
- **Northern Ireland**: 162 clubs with cameras
- **NI Football Only**: 65 clubs (target list)
- **Contacts Found**: ~5-10 clubs (partial due to scraping issues)

## 🚀 Next Steps
1. Resolve DuckDuckGo timeout issues in contact scraper
2. Complete contact collection for all 65 NI football clubs  
3. Expand to other UK regions (Scotland, England, Wales)
4. Build outreach campaign templates

## 🛠 Dependencies
See `requirements.txt` for Python packages including:
- requests, beautifulsoup4 (web scraping)
- google-generativeai (Gemini API)
- pandas, csv (data processing)