import os
import shutil
import time
from datetime import datetime
import psycopg2
from mega import Mega

def backup_postgresql(db_config, backup_folder, dbname):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Customize this query based on your PostgreSQL database structure
        cursor.execute(f"SELECT datname FROM pg_database WHERE datistemplate = false AND datname = '{dbname}';")
        databases = [row[0] for row in cursor.fetchall()]

        if not databases:
            print(f"No matching database found for backup: {dbname}")
            return False

        for database in databases:
            backup_file = os.path.join(backup_folder, f"{database}.dump")
            os.system(f"PGPASSWORD={db_config['password']} pg_dump -h {db_config['host']} -U {db_config['user']} -d {database} -F c -b -v -f {backup_file}")

        cursor.close()
        conn.close()

        print(f"PostgreSQL backup for {dbname} completed successfully.")
        return True
    except Exception as e:
        print(f"Error during PostgreSQL backup: {e}")
        return False
def upload_to_mega(folder_path, mega_email, mega_password, mega_folder):
    # Create Mega object
    mega = Mega()

    # Login to Mega account
    m = mega.login(mega_email, mega_password)

    # Check if the folder already exists on Mega
    mega_files = m.get_files()
    folder_exists = any(file['name'] == mega_folder and file['type'] == 'd' for file in mega_files if 'type' in file)

    if folder_exists:
        # Delete the existing folder
        m.delete(m.find(mega_folder)[0]['h'])

    # Create the Mega folder
    m.create_folder(mega_folder)

    # Get all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Upload each file to Mega
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        print(f"Uploading file {file_name} to Mega...")
        
        # Upload the file to Mega
        m.upload(file_path, m.find(mega_folder)[0])

    print("Upload complete.")
 
def delete_local_backups(backup_folder):
    files = os.listdir(backup_folder)

    for file in files:
        file_path = os.path.join(backup_folder, file)
        os.remove(file_path)

    print("Local backup files deleted.")

if __name__ == "__main__":
    # PostgreSQL database configuration


    backup_folder = "/home/alan/Documents/db/"
    mega_email = "agathicountai@gmail.com"
    mega_password = "@Aga$12ca#"
    mega_folder = "db"
    dbname="knitting"

    db_config = {
        "host": "localhost",
        "user": "postgres",
        "password": "soft",
        "dbname": dbname
    }
    

    while True:
        if backup_postgresql(db_config, backup_folder, dbname):
            upload_to_mega(backup_folder, mega_email, mega_password, mega_folder)
            delete_local_backups(backup_folder)

        # Sleep for 30 minutes
        time.sleep(1800)
