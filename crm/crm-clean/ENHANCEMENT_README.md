# Clubs Data Enhancement Script

This script enhances the `enhanced_clubs_england.csv` file by adding website URLs, contact information, and proper football tier categorization.

## Features

### 1. Website Discovery
- Searches for official club websites using known club mappings
- Attempts direct domain searches (e.g., `clubname.com`, `clubname.co.uk`)
- Identifies and validates working websites

### 2. Contact Information Extraction
- **Email Addresses**: Extracts contact emails from club websites
- **Phone Numbers**: Finds UK phone numbers (mobile and landline)
- **Contact Quality Score**: Rates completeness of contact information (0-3)

### 3. Football Tier Categorization
- **Tier 1**: Premier League
- **Tier 2**: Championship  
- **Tier 3**: League One
- **Tier 4**: League Two
- **Tier 5**: National League
- **Tier 6**: Non-League (Isthmian, Northern Premier, Southern League)
- **Tier 0**: Academy/Youth teams

## Installation

1. Install required dependencies:
```bash
pip install -r requirements_enhancement.txt
```

2. Ensure you're in the `crm/crm-clean` directory

## Usage

### Quick Test (Recommended First)
Test the functionality on a small subset:
```bash
cd src
python test_enhancement.py
```

### Full Enhancement
Run the complete enhancement on all clubs:
```bash
cd src
python enhance_clubs_data.py
```

### Custom Processing
```python
from enhance_clubs_data import ClubDataEnhancer

# Initialize with your CSV file
enhancer = ClubDataEnhancer('path/to/your/clubs.csv')

# Process specific range
enhancer.process_all_clubs(start_index=100, batch_size=25)

# Generate summary report
summary = enhancer.generate_summary_report()
```

## Output Files

- **Original CSV**: Updated in-place with new data
- **Backup**: `enhanced_clubs_england_backup.csv` (created automatically)
- **Enhanced Version**: `enhanced_clubs_england_enhanced.csv`
- **Log File**: `clubs_enhancement.log`
- **Summary Report**: `enhancement_summary.json`

## Data Structure

The enhanced CSV will contain these additional/updated columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Website` | Official club website URL | `https://www.arsenal.com` |
| `Emails` | Primary contact email | `info@arsenal.com` |
| `Phone Numbers` | Contact phone number | `+44 20 7619 5003` |
| `Contact_Quality` | Contact completeness score (0-3) | `3` |
| `Football_Tier` | Tier name | `Premier League` |
| `Tier_Number` | Numeric tier (1-6) | `1` |
| `Tier_Confidence` | Confidence in tier assignment (0.0-1.0) | `0.9` |

## Safety Features

- **Automatic Backup**: Creates backup before processing
- **Progress Saving**: Saves progress every 10 clubs and after each batch
- **Rate Limiting**: Built-in delays to avoid overwhelming websites
- **Error Handling**: Continues processing even if individual clubs fail
- **Resume Capability**: Can restart from any index

## Performance

- **Batch Processing**: Processes clubs in configurable batches (default: 50)
- **Rate Limiting**: 1-3 second delays between requests
- **Estimated Time**: ~2-3 hours for all 2,181 clubs
- **Memory Usage**: Low (processes in batches)

## Known Clubs

The script includes pre-mapped websites for major clubs:
- Arsenal, Chelsea, Manchester United, Manchester City
- Liverpool, Tottenham, Crystal Palace, Burnley
- Blackburn Rovers, Ipswich Town, Fleetwood Town
- And many more...

## Customization

### Adding More Known Clubs
Edit the `known_clubs` dictionary in the script:
```python
self.known_clubs = {
    'Your Club Name': 'https://www.yourclub.com',
    # ... existing entries
}
```

### Modifying Football Tiers
Update the `football_tiers` dictionary:
```python
self.football_tiers = {
    'Your Tier': 7,
    # ... existing entries
}
```

### Changing Batch Size
Modify the `batch_size` parameter:
```python
enhancer.process_all_clubs(start_index=0, batch_size=100)
```

## Troubleshooting

### Common Issues

1. **Rate Limiting**: If you get blocked, increase delays in the script
2. **Memory Issues**: Reduce batch size if processing large datasets
3. **Network Errors**: Check internet connection and firewall settings

### Log Files
Check `clubs_enhancement.log` for detailed error information and progress updates.

### Resume Processing
If the script stops, you can resume from any index:
```python
enhancer.process_all_clubs(start_index=500, batch_size=50)
```

## Example Output

After enhancement, your data will look like:

```csv
Club Name,Website,Emails,Phone Numbers,Contact_Quality,Football_Tier,Tier_Number,Tier_Confidence
Arsenal Football Club PLC,https://www.arsenal.com,info@arsenal.com,+44 20 7619 5003,3,Premier League,1,0.9
Chelsea Academy VEO,https://www.chelseafc.com,academy@chelseafc.com,+44 20 7385 5545,3,Premier League,1,0.9
Manchester City FC,https://www.mancity.com,info@mancity.com,+44 161 444 1894,3,Premier League,1,0.9
```

## Support

For issues or questions:
1. Check the log files for error details
2. Verify your CSV file structure matches the expected format
3. Ensure all dependencies are properly installed
4. Test with a small subset first using `test_enhancement.py`

