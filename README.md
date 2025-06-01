# SQL Holiday Sync

A lightweight utility to sync public holidays from [Nager.Date API](https://date.nager.at) into an SQL Server database (e.g., XTime900). Useful for updating systems like time & attendance.

---

## 🚀 Features

- Retrieves all holidays for current and next 2 years
- Syncs them to your SQL Server table
- Updates existing holidays if names change
- Includes a config UI to set server/database credentials
- Logs all operations

---

## 🧰 Requirements

- Python 3.11+
- ODBC Driver 17 for SQL Server
- Internet access to fetch holidays from the API

---

## 🔧 Setup Instructions

### 1. Clone this repo

```bash
git clone https://github.com/ChilliPhantom/SQL_holiday_sync.git
cd SQL_holiday_sync
