# Trakt To IMDb Ratings Importer
Automatically import your movie ratings from Trakt to IMDb using this Python automation script.

## Overview

This script reads your Trakt export data and automatically adds ratings to your IMDb account. It uses Selenium to automate the browser, logging into IMDb and clicking through to add each rating.

If you enjoy using this tool, consider donating to: https://paypal.me/lmarianosegura

**Key Features:**
- 🔄 Resume functionality - saves progress and can continue where it left off
- ⏭️ Skip already-rated movies - doesn't re-rate movies you've already rated on IMDb
- 📊 Detailed progress reporting - shows success/failure status for each movie
- ⚡ Batch processing - automatically goes through your entire ratings library
- 🛡️ Error handling - gracefully handles missing IMDb IDs or page load issues

## Requirements

- Python 3.7 or higher
- Google Chrome browser installed
- A Trakt account with exported data
- An IMDb account

## Installation

### 1. Clone or download this repository

```bash
git clone <repository-url>
cd trakt-export
```

Or simply download the files directly.

### 2. Install Python dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or manually install each package:

```bash
pip install selenium webdriver-manager
```

### Python Dependencies

- **selenium** (4.x+) - Browser automation library
- **webdriver-manager** - Automatically manages ChromeDriver versions

## Setup

### Step 1: Download Your Trakt Data

1. Go to [Trakt.tv](https://trakt.tv) and log into your account
2. Navigate to **Settings** → **Data** (https://app.trakt.tv/settings/data?mode=media)
3. Click on **Export Now** to download your data as JSON files
4. Extract the downloaded files

### Step 2: Place Files in the Same Directory

1. Copy `trakt_to_imdb_movie_ratings_importer.py` to the folder containing your Trakt export files
2. Ensure `ratings-movies.json` is in the same directory as the script

**Directory structure should look like:**
```
trakt-export-folder/
├── trakt_to_imdb_movie_ratings_importer.py
├── ratings-movies.json
├── collection-movies.json
├── watched-movies.json
└── ... (other Trakt export files)
```

## How to Use

### Running the Script

1. Open a terminal/command prompt
2. Navigate to the folder containing `trakt_to_imdb_movie_ratings_importer.py`:
   ```bash
   cd path/to/trakt-export-folder
   ```

3. Run the script:
   ```bash
   python trakt_to_imdb_movie_ratings_importer.py
   ```

### What to Expect

1. Chrome will automatically launch and open IMDb's sign-in page
2. **You will have time to log in** - The script waits for a configurable duration (default 60 seconds) to give you time to:
   - Log into your IMDb account (if not already logged in)
   - Keep the tab open
   - The script will show a countdown timer

3. Once the countdown reaches zero, the script automatically:
   - Navigates to each movie's IMDb page
   - Opens the rating dialog
   - Clicks the appropriate star rating
   - Saves the rating
   - Moves to the next movie

4. The script displays progress:
   ```
   [1/245] Adding rating for 'The Shawshank Redemption' (1994) - 9/10
     📍 Opening: https://www.imdb.com/title/tt0111161/
     🖱️  Opening rating dialog...
     ⭐ Clicking 9-star rating...
     🖱️  Clicking Rate button to save...
     ✓ SUCCESS
   ```

5. At the end, you'll see a summary:
   ```
   ============================================================
   IMPORT SUMMARY
   ============================================================
   ✓ Successfully rated: 242
   ✗ Failed: 2
   ⊘ Skipped: 1
   📊 Total processed: 245/245
   💾 Progress saved to: imdb_import_progress.json
   ============================================================
   ```

## Progress Tracking

The script automatically saves progress to `imdb_import_progress.json`. This file tracks:
- Successfully rated movies
- Failed ratings (you can retry)
- Skipped movies (no IMDb ID available)

If the script is interrupted (Ctrl+C), you can simply run it again and it will:
- Skip already successfully rated movies
- Retry failed ones
- Continue where it left off

## Troubleshooting

### "ratings-movies.json not found"
- Make sure you've extracted the Trakt export files
- Ensure `ratings-movies.json` is in the same folder as `trakt_to_imdb_movie_ratings_importer.py`
- Check the file name spelling exactly matches

### Chrome fails to launch
- Ensure Google Chrome is installed
- Try reinstalling the dependencies: `pip install --upgrade selenium webdriver-manager`
- On Linux, you may need additional dependencies: `sudo apt-get install -y chromium-browser`

### Rating clicks aren't working
- IMDb's UI changes occasionally; this may require script updates
- Try manually rating a few movies to ensure your account works
- Check that you're logged into IMDb in the Chrome window

### Script runs too fast/slow
- Increase or decrease the `time.sleep()` values in the script if needed (line 203 controls the delay between movies)

## Advanced Usage

### Resume a Failed Import

Simply run the script again:
```bash
python imdb_importer.py
```

It will skip already successful ratings and retry failed ones.

### Manually Edit Progress

Edit `imdb_import_progress.json` to reset specific movies:
```json
{
  "tt0111161": "success",
  "tt0068646": "failed"
}
```

Remove entries to force re-rating of specific movies.

### Custom Login Timeout

To adjust the login timeout duration, edit line 18 in `trakt_to_imdb_movie_ratings_importer.py`:
```python
LOGIN_TIME_SECONDS = 60  # Change 60 to desired number of seconds
```

For example, if you need more time to log in:
```python
LOGIN_TIME_SECONDS = 120  # 2 minutes
```

## Notes

- ⚠️ **Keep Chrome window open** - Don't close it while the script is running
- 🔐 **Stay logged in** - Ensure you remain logged into your IMDb account
- ⏱️ **Be patient** - Importing hundreds of ratings takes time (typically 3-5 seconds per movie)
- 🚫 **Don't interact** - Try not to click in the Chrome window while the script runs

## License

This script is provided as-is for personal use.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Trakt export file is valid JSON
3. Ensure your IMDb account is working properly
4. Check that `ratings-movies.json` has valid data

Enjoy syncing your ratings!
