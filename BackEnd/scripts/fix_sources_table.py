import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'newspulse.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add missing columns to news_sources
missing_columns = [
    'ALTER TABLE news_sources ADD COLUMN website_url VARCHAR(500)',
    'ALTER TABLE news_sources ADD COLUMN language VARCHAR(10)',
    'ALTER TABLE news_sources ADD COLUMN priority INTEGER',
    'ALTER TABLE news_sources ADD COLUMN last_scraped DATETIME'
]

for sql in missing_columns:
    try:
        cursor.execute(sql)
        print(f'Added: {sql.split("ADD COLUMN ")[1].split()[0]}')
    except sqlite3.OperationalError as e:
        print(f'Column exists or error: {e}')

# Update existing records with default values
cursor.execute('UPDATE news_sources SET website_url = "https://example.com" WHERE website_url IS NULL')
cursor.execute('UPDATE news_sources SET language = "en" WHERE language IS NULL')
cursor.execute('UPDATE news_sources SET priority = 1 WHERE priority IS NULL')

conn.commit()
conn.close()
print('News sources table updated successfully')