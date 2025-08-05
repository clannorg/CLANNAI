# 🎯 ClannAI CRM - Organized Pipeline

**Clean, numbered workflow for sports analytics outreach**

## 🗂️ **Organized Structure**

```
crm-clean/
├── src/                              # 📝 NUMBERED SCRIPTS
│   ├── 1-veo-scraper.py             # Stage 1: Get ALL clubs
│   ├── 2-location-sorter.py         # Stage 2: Sort by country  
│   ├── 3-contact-finder.py          # Stage 3: Find emails/phones
│   └── 4-run-pipeline.py            # Stage 4: Run everything
│
├── data/                             # 📊 ORGANIZED BY STAGE
│   ├── 1-veo-scraper/               # Raw scraped data
│   │   ├── veo_clubs.csv            # 5,681 clubs from VEO
│   │   └── feasible_customers.csv   # 2,469 prospects
│   │
│   ├── 2-by-country/                # Geographic sorted data
│   │   ├── clubs_by_location.csv    # All clubs with scores
│   │   ├── clubs_england.csv        # 140 English clubs
│   │   ├── clubs_ireland.csv        # 3 Irish clubs (HIGH VALUE)
│   │   ├── clubs_northern_ireland.csv
│   │   ├── clubs_scotland.csv
│   │   ├── clubs_united_states.csv  # 882 US clubs
│   │   └── clubs_wales.csv          # 1 Welsh club (SUPER HIGH)
│   │
│   └── 3-contact-details/           # Contact information
│       ├── club_contacts.csv        # 12 clubs with emails/phones
│       ├── contact_progress.json    # Progress tracking
│       └── contact_finder.log       # Search logs
│
├── requirements.txt                  # Dependencies for hooper-ai
└── README.md                        # Main documentation
```

---

## 🚀 **How to Use the Organized Pipeline**

### **Option 1: Run Full Pipeline (Recommended)**
```bash
conda activate hooper-ai
cd /home/ubuntu/CLANNAI/crm/crm-clean
python src/4-run-pipeline.py --full
```

### **Option 2: Run Individual Stages**
```bash
# Stage 1: Get clubs from VEO
python src/1-veo-scraper.py

# Stage 2: Sort by country & score  
python src/2-location-sorter.py

# Stage 3: Find contact details
python src/3-contact-finder.py

# Stage 4: Interactive pipeline runner
python src/4-run-pipeline.py
```

### **Option 3: Check Pipeline Status**
```bash
python src/4-run-pipeline.py --status
```

---

## 🎯 **The 4-Stage Workflow**

| **Stage** | **Script** | **Input** | **Output** | **Purpose** |
|-----------|------------|-----------|------------|-------------|
| **1** | `1-veo-scraper.py` | VEO website | `1-veo-scraper/veo_clubs.csv` | Get ALL clubs |
| **2** | `2-location-sorter.py` | Stage 1 data | `2-by-country/clubs_*.csv` | Sort by country |
| **3** | `3-contact-finder.py` | Stage 2 data | `3-contact-details/club_contacts.csv` | Find emails/phones |
| **4** | `4-run-pipeline.py` | All stages | Complete workflow | Run everything |

---

## 📊 **What You Currently Have**

### **✅ Stage 1 Complete:** 
- **5,681 clubs** from VEO directory
- **2,469 qualified prospects** with activity scores

### **✅ Stage 2 Complete:**
- **Clubs sorted by country** with activity scores
- **Country-specific files** for targeted outreach
- **High-value targets identified**

### **✅ Stage 3 In Progress:**
- **12 clubs with contact details** (60% success rate!)
- **Professional contacts found** (Fleetwood Town, etc.)
- **Ready to scale contact finding**

---

## 🎯 **Benefits of Organized Structure**

✅ **Clear workflow** - numbered stages show exact order  
✅ **Organized data** - each stage has its own folder  
✅ **Progress tracking** - resume any stage where it left off  
✅ **Easy scaling** - run stages independently or together  
✅ **Clean outputs** - no confusion about what files do what  

---

## 📈 **Current High-Value Prospects**

### **🇮🇪 Ireland (3 clubs, 53.77 avg activity):**
- High engagement, English-speaking market

### **🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales (1 club, 91.90 activity):**
- **SUPER HIGH VALUE** - 91.90 activity score!

### **🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (140 clubs, 43.91 avg activity):**
- Sheffield United Academy (1,739 activity!)
- Fleetwood Town (1,276 activity) ✅ **CONTACT FOUND**

---

## 🚀 **Next Actions**

### **Immediate (Today):**
```bash
# Email these prospects immediately:
- fleetwood.info@fleetwoodtownfc.com (Fleetwood Town)
- estevenson@ambassadorsfootball.org (Ambassadors FC)
- admin@theucl.co.uk (NEWARK FC)
```

### **This Week:**
```bash
# Scale contact finding (wait 24h to avoid rate limits):
python src/3-contact-finder.py
# Then enter: 50 (to find 50 more contacts)
```

### **Pipeline Status:**
```bash
# Check what's completed:
python src/4-run-pipeline.py --status
```

---

## 🛠️ **Environment Setup**

```bash
# Activate environment
conda activate hooper-ai

# Install dependencies (if needed)
pip install -r requirements.txt

# Navigate to CRM
cd /home/ubuntu/CLANNAI/crm/crm-clean
```

---

**Your CRM is now perfectly organized and ready to scale!** 🚀

*From chaos (63+ scripts) to clarity (4 numbered stages)*