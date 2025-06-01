import pyodbc
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=os.path.join("..", ".env"))

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# Ensure logs directory exists
log_dir = os.path.join("..", "logs")
os.makedirs(log_dir, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename=os.path.join(log_dir, "sync.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_db_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USER};PWD={SQL_PASSWORD}"
        )
        logging.info("Connected to SQL Server successfully.")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        raise

def get_country_list():
    url = "https://date.nager.at/api/v3/AvailableCountries"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_holidays(country_code):
    current_year = datetime.now().year
    holidays = []

    for year in [current_year, current_year + 1, current_year + 2]:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
        response = requests.get(url)
        response.raise_for_status()
        holidays.extend(response.json())

    return holidays

def sync_holidays_to_db(holidays, conn):
    cursor = conn.cursor()
    new_count = 0
    updated_count = 0
    skipped_count = 0

    for hol in holidays:
        hol_date = datetime.strptime(hol['date'], "%Y-%m-%d")
        hol_name = hol['localName'].strip()

        cursor.execute("""
            SELECT HOL_NAME FROM HOLIDAYS WHERE HOL_DATE = ? AND SITE_CODEID = ?
        """, hol_date, 1)
        row = cursor.fetchone()

        if row is None:
            cursor.execute("""
                INSERT INTO HOLIDAYS (HOL_DATE, SITE_CODEID, HOL_PAID, HOL_CLOSEACCESS, HOL_NAME, HOLCAT_CODEID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, hol_date, 1, 1, 1, hol_name, 1)
            new_count += 1
            logging.info(f"Inserted: {hol_date.date()} - {hol_name}")
        else:
            existing_name = row[0].strip()
            if existing_name != hol_name:
                cursor.execute("""
                    UPDATE HOLIDAYS SET HOL_NAME = ? WHERE HOL_DATE = ? AND SITE_CODEID = ?
                """, hol_name, hol_date, 1)
                updated_count += 1
                logging.info(f"Updated: {hol_date.date()} - {existing_name} ➜ {hol_name}")
            else:
                skipped_count += 1
                logging.info(f"Skipped (no changes): {hol_date.date()} - {hol_name}")

    conn.commit()

    summary = (
        f"\n✅ Sync complete:\n"
        f"   ➕ {new_count} new holidays inserted\n"
        f"   🔄 {updated_count} existing holidays updated\n"
        f"   ⏭️ {skipped_count} holidays skipped (no changes)\n"
    )
    print(summary)
    logging.info(summary)

def main():
    logging.info("====== Holiday Sync Started ======")

    try:
        countries = get_country_list()
        for idx, country in enumerate(countries):
            print(f"{idx + 1}. {country['name']} ({country['countryCode']})")

        selected = int(input("\nEnter the number of the country: ")) - 1
        country = countries[selected]
        print(f"\nFetching holidays for: {country['name']} ({country['countryCode']})")
        logging.info(f"Selected country: {country['name']} ({country['countryCode']})")

        holidays = fetch_holidays(country['countryCode'])
        print(f"Found {len(holidays)} holidays to process.")
        logging.info(f"Fetched {len(holidays)} holidays from API.")

        conn = get_db_connection()
        sync_holidays_to_db(holidays, conn)
        conn.close()

    except Exception as e:
        logging.exception("❌ An error occurred during sync")
        print(f"\n❌ Error: {e}")

    logging.info("====== Holiday Sync Ended ======\n")

if __name__ == "__main__":
    main()
