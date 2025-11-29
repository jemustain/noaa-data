# NOAA Data Scripts - Quick Reference Guide

## 🚀 Quick Setup (First Time Only)

1. **Install Python** (if not installed)
   - Download from Microsoft Store or python.org
   - Verify: `python --version`

2. **Install Required Packages**
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. **Configure API Key**
   - Get free API key from: https://www.ncdc.noaa.gov/cdo-web/token
   - Add to `.env` file:
     ```
     NOAA_API_KEY=your_key_here
     ```

---

## 📊 Available Scripts

### 1️⃣ Search for Stations
```powershell
python scripts\search_stations.py
```
- **Time:** <1 minute
- **Output:** List of 50+ weather stations in Tucson area
- **File:** `data/tucson_area_stations.json`

---

### 2️⃣ Quick Data Fetch (Last 30 Days)
```powershell
python scripts\fetch_noaa_data.py
```
- **Time:** <1 minute
- **Output:** Recent weather data (last 30 days)
- **Files:** 
  - `data/tucson_station_info.json`
  - `data/tucson_weather_[timestamp].json`

---

### 3️⃣ View & Export Data
```powershell
python scripts\view_data.py
```
- **Time:** <1 minute
- **Output:** Formatted tables + CSV export
- **File:** `data/tucson_weather.csv` (opens in Excel)

---

### 4️⃣ Complete Historical Data ⭐ **NEW!**
```powershell
python scripts\fetch_complete_history.py
```
- **Time:** 30-60 minutes (for full history from 1946)
- **Output:** Complete historical dataset in CSV format
- **Files:**
  - `data/tucson_weather_complete.json` (raw data)
  - `data/tucson_weather_complete.csv` (Excel-ready)

**Options when prompted:**
- Type `y` → Fetch all data since 1946
- Type `2000` → Fetch from year 2000 onwards
- Type `2020` → Fetch from year 2020 onwards

**What you get:**
- Every day from start year to present
- Columns: Date, Max Temp, Min Temp, Precipitation, Wind Speed, Snow, Snow Depth
- Ready to open in Excel for analysis

---

## 📁 Output Files

### JSON Files (Raw Data)
- `tucson_station_info.json` - Station metadata
- `tucson_area_stations.json` - List of nearby stations
- `tucson_weather_[timestamp].json` - Recent data
- `tucson_weather_complete.json` - Complete historical data

### CSV Files (Excel-Ready)
- `tucson_weather.csv` - Recent data in spreadsheet format
- `tucson_weather_complete.csv` - **Complete historical data** ⭐

---

## 🎯 Common Use Cases

### "I want to explore what's available"
```powershell
python scripts\search_stations.py
```

### "I want to test if everything works"
```powershell
python scripts\fetch_noaa_data.py
python scripts\view_data.py
```

### "I need all historical weather data for analysis"
```powershell
python scripts\fetch_complete_history.py
# Then open: data\tucson_weather_complete.csv in Excel
```

### "I want data from 2000 to present"
```powershell
python scripts\fetch_complete_history.py
# When prompted, type: 2000
```

---

## 📈 Data Columns in CSV

| Column | Description | Unit |
|--------|-------------|------|
| date | Date | YYYY-MM-DD |
| TMAX | Maximum temperature | °F |
| TMIN | Minimum temperature | °F |
| PRCP | Precipitation | inches |
| AWND | Average wind speed | mph |
| SNOW | Snowfall | inches |
| SNWD | Snow depth | inches |

---

## 💡 Tips

### Rate Limits
- API allows 5 requests/second, 10,000 requests/day
- Complete history script includes automatic delays
- If you hit limits, wait 60 seconds and it will auto-retry

### Best Practices
1. Run `search_stations.py` first to explore options
2. Test with `fetch_noaa_data.py` before fetching all history
3. Use `view_data.py` to preview data before Excel analysis
4. For large datasets, start with recent years (e.g., 2020)

### Changing Stations
1. Run `search_stations.py` to find station IDs
2. Edit `.env` file:
   ```
   STATION_ID=GHCND:USC00021357
   ```
3. Run any fetch script again

---

## ⏱️ Time Estimates

| Years of Data | Records | Estimated Time |
|---------------|---------|----------------|
| 1 month | ~90 | < 1 minute |
| 1 year | ~2,200 | ~3 minutes |
| 10 years | ~22,000 | ~10 minutes |
| 25 years | ~55,000 | ~25 minutes |
| Full (1946-2025) | ~175,000 | ~45-60 minutes |

---

## 🆘 Troubleshooting

**"NOAA_API_KEY not found"**
- Check `.env` file exists
- Verify API key is correct (no spaces)

**"Error 401"**
- API key is invalid
- Request new key from NOAA

**"Error 429"**
- Rate limit exceeded
- Script will auto-wait and retry

**"No data retrieved"**
- Check date range
- Verify station ID
- Try different data types

---

## 📞 Support

- **NOAA API Docs:** https://www.ncdc.noaa.gov/cdo-web/webservices/v2
- **Get API Key:** https://www.ncdc.noaa.gov/cdo-web/token
- **Email NOAA:** ncdc.orders@noaa.gov

---

**Created:** November 2025  
**For:** Tucson, AZ weather data analysis
