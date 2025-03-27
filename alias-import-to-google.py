import csv
import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def add_group_alias(service, group_email, alias_email):
    """
    Adds an alias to a Google Group.
    
    Args:
        service: Google Admin SDK Directory API service instance
        group_email (str): Email address of the existing Google Group
        alias_email (str): New alias email to add to the group
    
    Returns:
        dict or None: Response from the API or None if error
    """
    #alias object
    alias_object = {
        'alias': alias_email
    }
    
    try:
        response = service.groups().aliases().insert(
            groupKey=group_email,
            body=alias_object
        ).execute()
        
        print(f"✓ Added alias '{alias_email}' to group '{group_email}'")
        return response
    except HttpError as error:
        if error.resp.status == 409:
            print(f"✗ Alias '{alias_email}' already exists (conflict)")
        elif error.resp.status == 404:
            print(f"✗ Group '{group_email}' not found")
        elif error.resp.status == 403:
            print(f"✗ Permission denied to add alias to '{group_email}'")
        elif error.resp.status == 429:
            print(f"✗ Rate limit exceeded, waiting and trying again...")
            time.sleep(2)  #wait 2 secs before retrying
            return add_group_alias(service, group_email, alias_email)  #retry
        else:
            print(f"✗ Error adding alias '{alias_email}' to group '{group_email}': {error}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None

def add_aliases_from_csv(csv_file, credentials_file, admin_email):
    """
    Adds aliases to Google Groups based on mappings in a CSV file.
    
    Args:
        csv_file (str): Path to CSV file with group and alias mapping
        credentials_file (str): Path to service account JSON key file
        admin_email (str): Email of an admin user to impersonate
    """
    SCOPES = ['https://www.googleapis.com/auth/admin.directory.group']
    
    #service account json file
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES)
    
    #service account acts on behalf of admin user
    delegated_credentials = credentials.with_subject(admin_email)
    
    #build
    service = build('admin', 'directory_v1', credentials=delegated_credentials)
    
    total_aliases = 0
    successful_aliases = 0
    
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        group_idx = 0  #default group_email
        alias_idx = 1  #default all_aliases
        
        for i, col in enumerate(header):
            if col.lower() in ('group_email', 'email'):
                group_idx = i
            elif col.lower() in ('all_aliases', 'aliases', 'alias'):
                alias_idx = i
        
        print(f"Using column {group_idx+1} for group emails and column {alias_idx+1} for aliases")
        
        #execution
        for row in reader:
            if len(row) > max(group_idx, alias_idx):
                group_email = row[group_idx].strip()
                all_aliases_str = row[alias_idx].strip()
                
                if not group_email or not all_aliases_str:
                    continue
                
                alias_list = [a.strip() for a in all_aliases_str.split(';')]
                
                #process each alias
                for alias_email in alias_list:
                    if not alias_email:
                        continue
                        
                    total_aliases += 1
                    print(f"Processing: {group_email} -> {alias_email}")
                    
                    #append
                    response = add_group_alias(service, group_email, alias_email)
                    if response is not None:
                        successful_aliases += 1
                    
                    #rate limit
                    time.sleep(0.5)
    
    #output summary - simple
    print("\nSummary:")
    print(f"Total aliases processed: {total_aliases}")
    print(f"Successfully added: {successful_aliases}")
    print(f"Failed: {total_aliases - successful_aliases}")

#add variables here 
def main():
    CSV_FILE = ''
    CREDENTIALS_FILE = '.json'
    ADMIN_EMAIL = '@'
    
    print(f"Starting bulk alias addition from {CSV_FILE}...")
    add_aliases_from_csv(CSV_FILE, CREDENTIALS_FILE, ADMIN_EMAIL)
    print("Process completed.")

if __name__ == '__main__':
    main()
