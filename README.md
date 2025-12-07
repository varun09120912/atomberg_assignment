# Atomberg Share of Voice AI Agent

## 🚀 Quick Start

### ⚡ Start the Dashboard (3 Steps)

1. **Install Dependencies** (first time only)
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   python app_enhanced.py
   ```

3. **Open Dashboard**
   ```
   http://localhost:5000
   ```

### 📊 Using the Dashboard

1. **Load Demo Data**
   - Click the **"Load Default"** button to see sample analysis

2. **View Analysis**
   - See metrics: SoV %, Keywords Analyzed, Top Keywords, Competitors
   - View interactive charts: SoV Distribution, Sentiment, Rankings
   - Check detailed results table

3. **Download Reports**
   - Scroll to **"Generate & Download Report"** section
   - Choose format: **HTML** | **JSON** | **CSV** | **TXT**
   - Click to download instantly

4. **Custom Analysis** (Optional)
   - Edit Configuration fields: Brand, Keywords, Competitors, Search Terms
   - Click **"Run Analysis"** to analyze your custom parameters

## 📋 Available Report Formats

| Format | Use Case | Opens With |
|--------|----------|-----------|
| **HTML** | Professional reports, presentations | Any browser |
| **JSON** | API integration, automation | Text editor |
| **CSV** | Spreadsheet analysis | Excel, Google Sheets |
| **TXT** | Plain text, archiving | Notepad, any text editor |

## 🛠️ Tech Stack

- **Backend**: Flask 3.1.2 (Python)
- **Frontend**: Bootstrap 5.3 + Chart.js 4.4.0
- **API**: RESTful JSON
- **Database**: JSON files
- **Analysis**: NLTK, TextBlob, scikit-learn

## 📊 Features

### Dashboard Features
- ✅ **Real-time Metrics** - Live SoV, keywords, rankings
- ✅ **Interactive Charts** - 3 Chart.js visualizations
- ✅ **Detailed Reports** - 4 export formats (HTML, JSON, CSV, TXT)
- ✅ **One-Click Download** - Generate and download instantly
- ✅ **Responsive UI** - Works on all devices
- ✅ **Professional Design** - Beautiful gradient interface

### Report Formats

1. **HTML Reports** 
   - Professional formatting with CSS styling
   - Executive summary and recommendations
   - Competitive analysis tables
   - Ready to print or present

2. **JSON Export**
   - Complete analysis data structure
   - Machine-readable format
   - API integration ready

3. **CSV Reports**
   - Keyword-by-keyword breakdown
   - Competitive rankings
   - Sentiment metrics
   - Excel/Google Sheets compatible

4. **TXT Reports**
   - Plain text format
   - ASCII formatting
   - All findings and recommendations
   - Easy to archive

## 🚀 Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
python app_enhanced.py
```

### Step 3: Open Dashboard
```
http://localhost:5000
```

## � How to Use

### Load Demo Analysis
1. Open http://localhost:5000
2. Click **"Load Default"** button
3. View metrics and charts automatically

### Run Custom Analysis
1. Edit configuration fields:
   - **Primary Brand**: atomberg (or your brand)
   - **Brand Keywords**: comma-separated terms
   - **Competitors**: competitor brands
   - **Search Keywords**: terms to analyze
2. Click **"Run Analysis"**
3. Wait for results to display

### Download Reports
1. Scroll to **"Generate & Download Report"** section
2. Click desired format button:
   - **HTML** - Professional report
   - **JSON** - Raw data
   - **CSV** - Spreadsheet format
   - **TXT** - Plain text
3. File automatically downloads to your computer

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Dashboard page |
| `/api/demo` | GET | Demo analysis data |
| `/api/analyze` | POST | Run custom analysis |
| `/api/generate-report` | POST | Generate report |
| `/api/status` | GET | Server status |
| `/api/config` | GET | Default config |

## � Project Structure

```
atomberg_assignment/
├── app_enhanced.py       # Flask server (START HERE)
├── main.py               # Analysis engine
├── requirements.txt      # Dependencies
├── README.md             # This file
├── WORKING_STATUS.md     # Feature status
├── src/
│   ├── analyzers/        # Analysis modules
│   ├── scrapers/         # Data collection
│   └── utils/            # Report generator
├── templates/
│   └── dashboard_new.html  # Dashboard UI
├── static/
│   └── dashboard.js      # Dashboard logic
├── data/                 # Analysis results
└── output/               # Generated reports
```

## ⚙️ Configuration

Default configuration in dashboard form:
- **Brand**: Atomberg
- **Keywords**: atomberg, smart fan atomberg
- **Competitors**: havells, orient, agni
- **Search Terms**: smart fan, WiFi fan, ceiling fan

Edit these values directly in the dashboard form before running analysis.

## 🎯 What It Does

1. **Analyzes Multiple Keywords** - Evaluates share of voice across keywords
2. **Tracks Competitors** - Monitors Havells, Orient, Agni, etc.
3. **Calculates SoV Metrics** - Mention-based, engagement-based, sentiment-based
4. **Displays Results** - Interactive charts and detailed tables
5. **Generates Reports** - Professional reports in 4 formats
6. **Enables Downloads** - One-click download of analysis

## ✅ Tested & Verified

- ✅ Flask server runs without errors
- ✅ Dashboard loads successfully
- ✅ Charts display correctly
- ✅ Reports generate in all formats
- ✅ Downloads function properly
- ✅ API endpoints working
- ✅ Analysis runs smoothly
- ✅ Database saves correctly

## � Troubleshooting

### Port 5000 Already in Use
```bash
# Use a different port
python app_enhanced.py --port 5001
# Then visit http://localhost:5001
```

### Report Not Downloading
- Check browser download settings
- Try a different browser
- Check file permissions

### Analysis Not Running
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Flask server is running
- Refresh the dashboard page

## � Support

For issues or questions:
1. Check WORKING_STATUS.md for feature overview
2. Verify all dependencies installed
3. Ensure Flask server is running on port 5000
4. Check browser console for errors (F12)

---

**Version**: 2.0  
**Last Updated**: 2025-12-08  
**Status**: ✅ Production Ready

---

**Last Updated**: December 2025  
**Version**: 1.0.0  
**Maintainer**: Analytics Team
