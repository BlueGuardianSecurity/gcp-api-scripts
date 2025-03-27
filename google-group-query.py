import os
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_all_google_groups(domain, credentials_file, admin_email):
    """
    Retrieves all Google Groups in your enterprise domain including aliases.
    
    Args:
        domain (str): Your enterprise domain (e.g., 'example.com')
        credentials_file (str): Path to your service account JSON key file
        admin_email (str): Email of an admin user to impersonate
    
    Returns:
        list: List of Google Groups with their details and aliases
    """
    SCOPES = ['https://www.googleapis.com/auth/admin.directory.group.readonly']
    
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES)
    
    delegated_credentials = credentials.with_subject(admin_email)
    
    service = build('admin', 'directory_v1', credentials=delegated_credentials)
    
    #get the groups
    results = []
    page_token = None
    
    while True:
        try:
            response = service.groups().list(
                customer='my_customer', #this value covers all groups within the domain
                pageToken=page_token,
                maxResults=2000
            ).execute()
        except Exception as e:
            
            # falls back to domain-specific query if customer-wide query fails
            print(f"Customer-wide query failed, falling back to domain-specific query: {e}")
            response = service.groups().list(
                domain=domain,
                pageToken=page_token,
                maxResults=2000
            ).execute()
        
        groups = response.get('groups', [])
        
        for group in groups:
            group_email = group.get('email')
            group_key = group.get('id')
            
            #get the aliases
            try:
                aliases_response = service.groups().aliases().list(
                    groupKey=group_key
                ).execute()
                
                aliases = aliases_response.get('aliases', [])
                alias_emails = [alias.get('alias') for alias in aliases]
                
                #append
                group['aliases'] = alias_emails
            except Exception as e:
                print(f"Error fetching aliases for {group_email}: {e}")
                group['aliases'] = []
        
        results.extend(groups)
        
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    return results

def export_to_csv(groups, output_file):
    """
    Export groups data to a CSV file.
    
    Args:
        groups (list): List of Google Groups with their details
        output_file (str): Path to output CSV file
    """
    fieldnames = ['name', 'email', 'description', 'id', 'aliases']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for group in groups:
            aliases_str = '; '.join(group.get('aliases', []))
        
            row = {
                'name': group.get('name', ''),
                'email': group.get('email', ''),
                'description': group.get('description', ''),
                'id': group.get('id', ''),
                'aliases': aliases_str
            }
            
            writer.writerow(row)
    
    print(f"Data exported to {output_file}")

def main():
    DOMAIN = ''
    
    #service account json path
    CREDENTIALS_FILE = ''
    
    #email of a credentialed admin, not service account's email
    ADMIN_EMAIL = ''
    
    OUTPUT_FILE = ''
    
    print(f"Fetching Google Groups for domain {DOMAIN}...")
    groups = get_all_google_groups(DOMAIN, CREDENTIALS_FILE, ADMIN_EMAIL)
    
    print(f"Found {len(groups)} groups")
    
    export_to_csv(groups, OUTPUT_FILE)
    
    print(f"Process completed. Groups exported to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
