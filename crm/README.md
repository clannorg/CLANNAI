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

## 🚀 AWS VM Deployment (Current Priority)

**Goal**: Get complete Veo dataset (100k+ clubs) faster than local machine

**Setup**:
1. Launch AWS EC2 (t3.large, Ubuntu 22.04)
2. `git clone` this repo 
3. Install Chrome + Python deps
4. Run: `python3 scripts/enhanced_scraper.py`

**Expected**: 3-5 hours for complete dataset vs 15+ hours locally

**Output**: `data/raw/all_veo_clubs.csv` (complete global dataset)

## 🔄 Next Steps After VM
1. Re-run categorization on complete dataset
2. Expand filtering to all UK/Ireland regions  
3. Scale contact scraping to larger target lists

## 🛠 Dependencies
See `requirements.txt` for Python packages including:
- requests, beautifulsoup4 (web scraping)
- google-generativeai (Gemini API)
- pandas, csv (data processing)