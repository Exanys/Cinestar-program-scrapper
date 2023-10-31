import json
import urllib.request
from datetime import datetime

from bs4 import BeautifulSoup

ANY_PROGRAM_URL = "https://www.cinestar.cz/cz/?option=com_csevents&view=eventsforday&date={}&cinema=8&titleId=0&format=raw&tpl=program"
DATES_GET_URL = "https://www.cinestar.cz/index.php?option=com_csevents&task=DaysWithEvents.getEventDays&format=json&startDate={}&cinema=8&title=0"


def main() -> None:
    dates = get_dates()
    data = get_data(dates)
    print(json.dumps(data, indent=4))


def get_tables(date: str) -> list:
    html = urllib.request.urlopen(ANY_PROGRAM_URL.format(date))
    soup = BeautifulSoup(html, 'html.parser')
    return soup.findAll('table', {'id': 'tableProgram'})


def get_data_from_row(row) -> dict:
    title_name = row.find('td', {'class': 'tdTitle'}).find('div', {'class': 'divTitle'}).span.text.strip()
    title_length = row.css.select('td > span > div.detail > em')[1].text.strip()
    title_starts = [time.text.strip() for time in row.css.select('td > span > a')]
    title_times = [f'{title_starts[i]};{title_end}'
                   for title_end in row.css.select('td > span > div.detail > em')[2]
                   for i in range(len(title_starts))]
    return {
        'title_name': title_name,
        'title_length': title_length,
        'title_times': title_times
    }


def get_data_from_table_program(table_html) -> dict:
    program_type = table_html.find('th', {'class': 'title-table'}).text.strip()
    rows = table_html.findAll('tr', {'class': ['even', 'odd']})
    titles = []
    for row in rows:
        titles.append(get_data_from_row(row))
    return {
        'program_type': program_type,
        'titles': titles,
    }


def get_data(dates_list: list) -> list:
    programs = []
    for date in dates_list:
        tables = get_tables(date)
        date_program = []
        for table in tables:
            program_data = get_data_from_table_program(table)
            date_program.append(program_data)
        programs.append({
            'date': date,
            'programs': date_program
        })
    return programs


def get_dates() -> list:
    response = urllib.request.urlopen(DATES_GET_URL.format(datetime.now().strftime("%Y-%m-%d")))
    json_response = response.read()
    return json.loads(json_response)['data']


if __name__ == '__main__':
    main()
