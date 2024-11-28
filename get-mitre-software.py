import requests
from bs4 import BeautifulSoup
import json
import os

def get_html_table(url, table_class):
    # Send a GET request to the URL
    response = requests.get(url)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the table with the specified class
    table = soup.find('table', class_=table_class)
    return table

def get_additional_data(software_url):
    response = requests.get(software_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract "Techniques Used" table
    techniques_table = soup.find('table', class_='table techniques-used background table-bordered')  # Replace with actual class name
    techniques = []
    if techniques_table:
        techniques_headers = [header.text.strip() for header in techniques_table.find_all('th')]
        for row in techniques_table.find_all('tr')[1:]:
            cells = row.find_all('td')
            technique_data = {techniques_headers[i]: cells[i].text.strip() for i in range(min(len(cells), len(techniques_headers)))}
            techniques.append(technique_data)
    
    # Extract "Groups That Use This Software" table
    groups_tables = soup.find_all('table', class_='table table-bordered table-alternate mt-2')  # Replace with actual class name
    groups = []
    if len(groups_tables) > 1:
        groups_table = groups_tables[1]  # Skip the first table and get the second one
        groups_headers = [header.text.strip() for header in groups_table.find_all('th')]
        for row in groups_table.find_all('tr')[1:]:
            cells = row.find_all('td')
            group_data = {groups_headers[i]: cells[i].text.strip() for i in range(min(len(cells), len(groups_headers)))}
            groups.append(group_data)
    elif len(groups_tables) == 1:
        groups_table = groups_tables[0]
        groups_headers = [header.text.strip() for header in groups_table.find_all('th')]
        for row in groups_table.find_all('tr')[1:]:
            cells = row.find_all('td')
            group_data = {groups_headers[i]: cells[i].text.strip() for i in range(min(len(cells), len(groups_headers)))}
            groups.append(group_data)

    # Extract additional information from divs
    additional_info = {}
    card_body = soup.find('div', class_='card-body')
    if card_body:
        rows = card_body.find_all('div', class_='row card-data')
        for row in rows:
            title_span = row.find('span', class_='h5 card-title')
            if title_span:
                title_text = title_span.text.strip()
                desired_titles = {
                    "Type",
                    "Platforms",
                    "Version",
                    "Created:",
                    "Last Modified:"
                }
                if title_text in desired_titles:
                    title = title_text.replace(':', '')
                    value = title_span.find_next_sibling(text=True).strip()
                    additional_info[title.lower().replace(' ', '_')] = value
    
    return {
        "techniques_used": techniques,
        "groups_that_use_this_software": groups,
        **additional_info
    }

def html_table_to_json(table, base_url):
    # Extract table headers
    headers = [header.text.strip() for header in table.find_all('th')]
    
    # Extract table rows
    rows = []
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        row_data = {headers[i]: cells[i].text.strip() for i in range(len(cells))}

        # Print the text of every second <td> in the row
        if len(cells) > 1:
            print(cells[1].text.strip())
        
        # Get the link from the first cell
        link_tag = cells[0].find('a')
        if link_tag and 'href' in link_tag.attrs:
            software_url = base_url + link_tag['href']
            additional_data = get_additional_data(software_url)
            row_data.update(additional_data)
        
        rows.append(row_data)
    
    # Save the JSON to a new file
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    with open(dir_path + 'output.json', 'w') as json_file:
        json.dump(rows, json_file, indent=4)

def main():
    url = 'https://attack.mitre.org/software/'  # Replace with the URL of the page containing the table
    table_class = 'table table-bordered table-alternate mt-2'  # Replace with the class of the table you want to extract
    base_url = 'https://attack.mitre.org'  # Base URL for constructing full URLs
    
    # Get the HTML table
    table = get_html_table(url, table_class)
    
    if table:
        # Convert the HTML table to JSON
        table_json = html_table_to_json(table, base_url)
        print(table_json)
    else:
        print(f"No table found with class '{table_class}'")

if __name__ == '__main__':
    main()