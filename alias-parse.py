import csv

def main():
    #csv paths
    input_file = ''
    output_file = ''
    duplicates_file = ''
    
    #looks for both domain extensions
    original_domain = ''
    new_domain = ''
    
    existing_emails_and_aliases = set()
    
    with open(input_file, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:

            email = row.get('email', '').strip().lower()
            if email:
                existing_emails_and_aliases.add(email)
            
            alias = row.get('alias', '').strip().lower()
            if alias:
                existing_emails_and_aliases.add(alias)
                print(f"Found existing alias: {alias} (for {row.get('name')})")

    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile, \
         open(duplicates_file, 'w', newline='') as dupfile:
        
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        dup_writer = csv.writer(dupfile)
        
        writer.writerow(['group_email', 'all_aliases'])
        dup_writer.writerow(['group_email', 'proposed_alias', 'reason', 'existing_aliases'])
        
        aliases_created = 0
        duplicates_found = 0
        
        proposed_aliases = set()
        
        for row in reader:
            name = row.get('name', '').strip()
            email = row.get('email', '').strip()
            existing_alias = row.get('alias', '').strip()
            
            if email.endswith('@' + original_domain):
                #everything before the @
                local_part = email.split('@')[0]
                
                proposed_alias = f"{local_part}@{new_domain}"
                
                #skip if group already has this exact alias
                if existing_alias.lower() == proposed_alias.lower():
                    print(f"Skipping {email} - already has the exact alias we would create")
                    # Still include in output file with existing alias
                    writer.writerow([email, existing_alias])
                    continue
                
                #check for alias conflict
                if proposed_alias.lower() in existing_emails_and_aliases or proposed_alias.lower() in proposed_aliases:
                    reason = "Conflicts with existing email or alias"
                    dup_writer.writerow([email, proposed_alias, reason, existing_alias])
                    duplicates_found += 1
                    print(f"Skipping {email} -> {proposed_alias} (conflict detected)")
                    
                    #still include in outfile 
                    if existing_alias:
                        writer.writerow([email, existing_alias])
                else:
                    combined_aliases = existing_alias
                    
                    #if group already has alias, append the new one with a separatot=r
                    if combined_aliases:
                        combined_aliases += '; ' + proposed_alias
                    else:
                        combined_aliases = proposed_alias
                    
                    #add to outfile
                    writer.writerow([email, combined_aliases])
                    aliases_created += 1
                    proposed_aliases.add(proposed_alias.lower())
        
        print(f"Generated {aliases_created} new aliases and saved to {output_file}")
        print(f"Found {duplicates_found} conflicts and saved to {duplicates_file}")
        print(f"All groups with their combined aliases are in {output_file}")

if __name__ == "__main__":
    main()
