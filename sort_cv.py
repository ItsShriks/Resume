#!/usr/bin/env python3
import re
import os
import sys

MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def parse_date_to_key(date_str):
    if not date_str:
        return (0, 0, 0, 0)
    
    # Clean up string
    date_str = date_str.strip()
    
    # Regex to find: Month Year -- Month/Present Year
    match = re.search(r'([A-Za-z]+)\.?\s+(\d{4})\s*--\s*([A-Za-z]+)\.?\s*(\d{4})?', date_str)
    if not match:
        return (0, 0, 0, 0)
    
    start_month_str, start_year_str, end_month_str, end_year_str = match.groups()
    
    start_year = int(start_year_str)
    start_month = MONTHS.get(start_month_str.lower()[:3], 1)
    
    if end_month_str.lower() == 'present':
        end_year = 9999
        end_month = 12
    else:
        end_year = int(end_year_str) if end_year_str else start_year
        end_month = MONTHS.get(end_month_str.lower()[:3], 12)
        
    return (end_year, end_month, start_year, start_month)

def extract_date_subheading(item_text):
    # Extracts the 4th argument of \resumeSubheading{arg1}{arg2}{arg3}{arg4}
    # Using a regex that matches balanced braces for the 4 arguments
    pattern = re.compile(r'\\resumeSubheading\s*\{([^{}]+)\}\s*\{([^{}]+)\}\s*\{([^{}]+)\}\s*\{([^{}]+)\}', re.DOTALL)
    match = pattern.search(item_text)
    if match:
        return match.group(4)
    return ""

def extract_date_subitem(item_text):
    # Extracts date like (Month Year -- Month/Present Year) from the end of the text
    # e.g., (Oct 2023 -- Mar 2024)
    pattern = re.compile(r'\(([A-Za-z]+\.?\s+\d{4}\s*--\s*(?:[A-Za-z]+\.?\s*\d{4}?|Present))\)', re.DOTALL)
    matches = pattern.findall(item_text)
    if matches:
        return matches[-1] # take the last match in the block
    return ""

def sort_work_experience(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    list_pattern = re.compile(r'(\\resumeSubHeadingListStart)(.*?)(\\resumeSubHeadingListEnd)', re.DOTALL)
    match = list_pattern.search(content)
    if not match:
        print("Could not find resumeSubHeadingList in work experience.")
        return False
        
    start_tag, list_content, end_tag = match.groups()
    
    # Split items by \resumeSubheading (including optional commented lines)
    item_pattern = re.compile(r'((?:%[^\n]*\n)*?\s*(?:%[^\n]*?)?\\resumeSubheading.*?)(?=(?:%[^\n]*\n)*?\s*(?:%[^\n]*?)?\\resumeSubheading|\Z)', re.DOTALL)
    items = item_pattern.findall(list_content)
    
    if not items:
        print("No work experience items found.")
        return False
        
    # Sort items
    sorted_items = sorted(
        items,
        key=lambda x: parse_date_to_key(extract_date_subheading(x)),
        reverse=True
    )
    
    # Clean up items and format nicely
    formatted_items = []
    for item in sorted_items:
        cleaned = item.strip()
        if cleaned:
            formatted_items.append("    " + cleaned)
            
    new_list_content = "\n\n" + "\n\n".join(formatted_items) + "\n\n"
    
    new_content = content.replace(list_content, new_list_content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully sorted and updated {file_path}")
    return True
 
def sort_projects(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    list_pattern = re.compile(r'(\\resumeSubHeadingListStart)(.*?)(\\resumeSubHeadingListEnd)', re.DOTALL)
    match = list_pattern.search(content)
    if not match:
        print("Could not find resumeSubHeadingList in projects.")
        return False
        
    start_tag, list_content, end_tag = match.groups()
    
    # Split items by \resumeSubItem (including optional commented lines)
    item_pattern = re.compile(r'((?:%[^\n]*\n)*?\s*(?:%[^\n]*?)?\\resumeSubItem.*?)(?=(?:%[^\n]*\n)*?\s*(?:%[^\n]*?)?\\resumeSubItem|\Z)', re.DOTALL)
    items = item_pattern.findall(list_content)
    
    if not items:
        print("No project items found.")
        return False
        
    # Sort items
    sorted_items = sorted(
        items,
        key=lambda x: parse_date_to_key(extract_date_subitem(x)),
        reverse=True
    )
    
    # Format projects with \vspace{2pt} in between
    formatted_items = []
    for item in sorted_items:
        # Strip vspace if it was captured
        cleaned = re.sub(r'\\vspace\{[^}]+\}', '', item)
        cleaned = cleaned.strip()
        if cleaned:
            formatted_items.append("    " + cleaned)
            
    # Join items with \vspace{2pt}
    separator = "\n    \n    \\vspace{2pt}\n    "
    new_list_content = "\n\n" + separator.join(formatted_items) + "\n\n"
    
    new_content = content.replace(list_content, new_list_content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully sorted and updated {file_path}")
    return True

if __name__ == '__main__':
    # Determine base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    work_exp_path = os.path.join(base_dir, '3_Work_Experience.tex')
    projects_path = os.path.join(base_dir, '4_Projects.tex')
    
    success = True
    if os.path.exists(work_exp_path):
        success &= sort_work_experience(work_exp_path)
    if os.path.exists(projects_path):
        success &= sort_projects(projects_path)
        
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
