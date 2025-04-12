import os
import django
import sys

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidyai.settings')
django.setup()

# Import Django's database connection
from django.db import connection

# SQL to add the estimated_duration column if it doesn't exist
sql = """
PRAGMA table_info(tutor_lesson);
"""

with connection.cursor() as cursor:
    cursor.execute(sql)
    columns = cursor.fetchall()
    
    has_estimated_duration = False
    for column in columns:
        if column[1] == 'estimated_duration':
            has_estimated_duration = True
            break
    
    if not has_estimated_duration:
        print("Adding estimated_duration column to tutor_lesson table...")
        cursor.execute("ALTER TABLE tutor_lesson ADD COLUMN estimated_duration INTEGER DEFAULT 20;")
        print("Column added successfully.")
    else:
        print("estimated_duration column already exists.")

print("Schema update complete.") 