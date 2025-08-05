# 🎯 Essential CRM Scripts

**Clean, working CRM tools for CLANNAI sports analytics**

## 📋 The 3 Core Scripts

### **1. `club_scraper.py`** - VEO Club Scraper
```bash
python src/club_scraper.py
```
- **Purpose:** Scrapes ALL clubs from VEO directory
- **Output:** `data/veo_clubs.csv` 
- **Gets:** Club name, recordings count, teams count
- **Features:** Progress tracking, headless browser, error handling

### **2. `location_sorter.py`** - Geographic Sorter  
```bash
python src/location_sorter.py
```
- **Purpose:** Sorts clubs by country/region
- **Input:** `data/veo_clubs.csv`
- **Output:** `data/clubs_by_location.csv` + country-specific files
- **Features:** Activity scoring, smart location detection

### **3. `contact_finder.py`** - Contact Scraper
```bash
python src/contact_finder.py
```
- **Purpose:** Finds phone numbers & emails for clubs
- **Input:** `data/clubs_by_location.csv`
- **Output:** `data/club_contacts.csv`
- **Features:** Google search + web scraping, progress tracking

---

## 🚀 Quick Start

### **Option 1: Run Full Pipeline**
```bash
# Install dependencies
pip install -r essential_requirements.txt

# Run everything at once
python src/run_crm.py --full
```

### **Option 2: Run Step by Step**
```bash
# Interactive mode - choose what to run
python src/run_crm.py
```

### **Option 3: Manual Steps**
```bash
# Step 1: Get all clubs
python src/club_scraper.py

# Step 2: Sort by location  
python src/location_sorter.py

# Step 3: Find contacts
python src/contact_finder.py
```

---

## 📊 Data Flow

```
VEO Directory
     ↓
club_scraper.py → veo_clubs.csv (raw club data)
     ↓
location_sorter.py → clubs_by_location.csv (sorted + scored)
     ↓
contact_finder.py → club_contacts.csv (with phone/email)
```

---

## 📁 Output Files

### **Core Data Files:**
- `data/veo_clubs.csv` - Raw scraped clubs
- `data/clubs_by_location.csv` - Sorted with activity scores
- `data/club_contacts.csv` - Clubs with contact details

### **Country-Specific Files:**
- `data/clubs_england.csv`
- `data/clubs_northern_ireland.csv` 
- `data/clubs_ireland.csv`
- `data/clubs_scotland.csv`
- `data/clubs_wales.csv`
- `data/clubs_united_states.csv`

### **Progress Files:**
- `data/scraper_progress.json` - Scraping progress
- `data/contact_progress.json` - Contact finding progress

---

## ⚙️ Configuration

### **Contact Finder Settings:**
```python
# In contact_finder.py, adjust these:
max_clubs = 50          # How many clubs to process
activity_threshold = 10  # Minimum activity score
rate_limit = 2          # Seconds between requests
```

### **Location Sorting:**
```python
# In location_sorter.py, customize location patterns:
location_patterns = {
    'Northern Ireland': ['belfast', 'derry', ...],
    'Ireland': ['dublin', 'cork', ...],
    # Add your own patterns
}
```

---

## 🛠️ Dependencies

**Essential only:**
- `selenium` - Web scraping
- `pandas` - Data processing  
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `googlesearch-python` - Google search

**Install:**
```bash
pip install -r essential_requirements.txt
```

---

## 📈 Expected Results

### **Club Scraper:**
- **Target:** 5,000+ clubs from VEO
- **Time:** ~30-60 minutes
- **Success rate:** 95%+

### **Location Sorter:**  
- **Processing:** All scraped clubs
- **Time:** <5 minutes
- **Accuracy:** ~90% for UK/Ireland clubs

### **Contact Finder:**
- **Success rate:** ~15-25% (industry standard)
- **Time:** ~2-3 minutes per club
- **Contacts per hour:** ~20-30 clubs

---

## 🎯 Pro Tips

1. **Start small:** Run contact finder on 10-20 clubs first
2. **Focus targets:** Use activity score to prioritize high-value clubs
3. **Geographic focus:** Process one country at a time
4. **Rate limiting:** Don't go too fast - you'll get blocked
5. **Progress tracking:** All scripts resume where they left off

---

## 🚨 Troubleshooting

### **Chrome Driver Issues:**
```bash
# Install webdriver-manager for automatic setup
pip install webdriver-manager
```

### **Google Search Blocked:**
- Reduce search frequency
- Use VPN if needed
- Try different search terms

### **Contact Success Rate Low:**
- Check club names are correct
- Verify activity scores are realistic
- Try smaller batches

---

**Ready to build your sports analytics empire!** 🚀

*These 3 scripts replace 63 files with clean, working essentials.*