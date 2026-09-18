import calendar
import hashlib
import json
import re
from datetime import date, datetime, timezone
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from django.conf import settings


REQUEST_TIMEOUT = (5, 15)
INTERRUPTION_TITLE_PREFIX = 'service interruption:'
VECO_DOMAIN = 'visayanelectric.com'
GOOGLE_CALENDAR_DOMAIN = 'docs.google.com'
CALENDAR_REQUIRED_COLUMNS = {
    'exactdate',
    'category',
    'title',
    'timeinfo',
    'locations',
    'status',
    'maplinks',
}
CALENDAR_REQUIRED_FIELDS = {'exactdate', 'title', 'timeinfo', 'locations'}
GOOGLE_DATE_PATTERN = re.compile(
    r'^Date\((?P<year>\d{4}),(?P<month>\d{1,2}),(?P<day>\d{1,2})'
    r'(?:,[^)]*)?\)$'
)
MONTH_NAMES = (
    'January|February|March|April|May|June|July|August|September|October|'
    'November|December'
)
MONTH_NUMBERS = {
    month: number
    for number, month in enumerate(
        (
            'january',
            'february',
            'march',
            'april',
            'may',
            'june',
            'july',
            'august',
            'september',
            'october',
            'november',
            'december',
        ),
        start=1,
    )
}
WEEKDAY_LABEL_PATTERN = re.compile(r'\s*\([^)]*\)')
DATE_HEADING_START_PATTERN = re.compile(rf'^(?:{MONTH_NAMES})\s+\d', re.IGNORECASE)
SINGLE_DATE_PATTERN = re.compile(
    rf'^(?P<month>{MONTH_NAMES})\s+(?P<day>\d{{1,2}}),\s*(?P<year>\d{{4}})$',
    re.IGNORECASE,
)
SAME_MONTH_RANGE_PATTERN = re.compile(
    rf'^(?P<month>{MONTH_NAMES})\s+(?P<start_day>\d{{1,2}})\s*-\s*'
    r'(?P<end_day>\d{1,2}),\s*(?P<year>\d{4})$',
    re.IGNORECASE,
)
CROSS_MONTH_RANGE_PATTERN = re.compile(
    rf'^(?P<start_month>{MONTH_NAMES})\s+(?P<start_day>\d{{1,2}})\s*-\s*'
    rf'(?P<end_month>{MONTH_NAMES})\s+(?P<end_day>\d{{1,2}}),\s*'
    r'(?P<year>\d{4})$',
    re.IGNORECASE,
)
FULL_DATE_RANGE_PATTERN = re.compile(
    rf'^(?P<start_month>{MONTH_NAMES})\s+(?P<start_day>\d{{1,2}}),\s*'
    r'(?P<start_year>\d{4})\s*-\s*'
    rf'(?P<end_month>{MONTH_NAMES})\s+(?P<end_day>\d{{1,2}}),\s*'
    r'(?P<end_year>\d{4})$',
    re.IGNORECASE,
)


class InterruptionServiceError(Exception):
    """Base exception for expected VECO integration failures."""


class LatestInterruptionNotFound(InterruptionServiceError):
    """Raised when the feed contains no service interruption entry."""


class UpstreamRequestError(InterruptionServiceError):
    """Raised when a VECO resource cannot be retrieved."""


class FeedParsingError(InterruptionServiceError):
    """Raised when the VECO feed cannot be interpreted reliably."""


class ArticleParsingError(InterruptionServiceError):
    """Raised when the full schedule cannot be extracted from an article."""


class CalendarParsingError(InterruptionServiceError):
    """Raised when the live calendar dataset cannot be interpreted reliably."""


def _normalize_text(value):
    normalized = ' '.join((value or '').replace('\xa0', ' ').split())
    return re.sub(r'\s+([,.;:!?])', r'\1', normalized)


def _request(url, accept, *, allow_redirects=True):
    try:
        response = requests.get(
            url,
            headers={
                'Accept': accept,
                'Cache-Control': 'no-cache',
                'User-Agent': 'VECO-Rotational-Outage/1.0',
            },
            timeout=REQUEST_TIMEOUT,
            allow_redirects=allow_redirects,
        )
        if not allow_redirects and 300 <= response.status_code < 400:
            raise UpstreamRequestError('The upstream service redirected the request.')
        response.raise_for_status()
    except requests.RequestException as exc:
        raise UpstreamRequestError(f'Unable to retrieve {url}.') from exc
    return response


def _entry_datetime(entry):
    parsed_time = entry.get('published_parsed') or entry.get('updated_parsed')
    if not parsed_time:
        raise FeedParsingError('A matching interruption entry has no valid publication date.')
    return datetime.fromtimestamp(calendar.timegm(parsed_time), tz=timezone.utc)


def _entry_category(entry):
    tags = entry.get('tags') or []
    if not tags:
        return ''
    return _normalize_text(tags[0].get('term', ''))


def _entry_image_url(entry):
    enclosures = entry.get('enclosures') or []
    if enclosures:
        return enclosures[0].get('href') or enclosures[0].get('url')

    media_content = entry.get('media_content') or []
    if media_content:
        return media_content[0].get('url')
    return None


def _parse_feed_entries(feed_content):
    parsed_feed = feedparser.parse(feed_content)
    if parsed_feed.bozo:
        raise FeedParsingError('VECO returned an invalid RSS feed.')

    matches = [
        entry
        for entry in parsed_feed.entries
        if _normalize_text(entry.get('title', '')).casefold().startswith(
            INTERRUPTION_TITLE_PREFIX
        )
    ]
    dated_entries = [(entry, _entry_datetime(entry)) for entry in matches]
    return sorted(dated_entries, key=lambda item: item[1], reverse=True)


def _validate_article_url(url):
    parsed_url = urlparse(url)
    hostname = (parsed_url.hostname or '').casefold()
    is_veco_host = hostname == VECO_DOMAIN or hostname.endswith(f'.{VECO_DOMAIN}')
    if parsed_url.scheme != 'https' or not is_veco_host:
        raise ArticleParsingError('The feed returned an unsafe article URL.')


def _make_date(year, month_name, day):
    try:
        return date(int(year), MONTH_NUMBERS[month_name.casefold()], int(day))
    except (KeyError, TypeError, ValueError) as exc:
        raise ArticleParsingError('A schedule has an invalid calendar date.') from exc


def _parse_date_label(date_label):
    normalized = _normalize_text(date_label).replace('–', '-').replace('—', '-')
    normalized = _normalize_text(WEEKDAY_LABEL_PATTERN.sub('', normalized))

    match = FULL_DATE_RANGE_PATTERN.fullmatch(normalized)
    if match:
        start_date = _make_date(
            match['start_year'], match['start_month'], match['start_day']
        )
        end_date = _make_date(match['end_year'], match['end_month'], match['end_day'])
    else:
        match = CROSS_MONTH_RANGE_PATTERN.fullmatch(normalized)
        if match:
            start_date = _make_date(match['year'], match['start_month'], match['start_day'])
            end_date = _make_date(match['year'], match['end_month'], match['end_day'])
        else:
            match = SAME_MONTH_RANGE_PATTERN.fullmatch(normalized)
            if match:
                start_date = _make_date(match['year'], match['month'], match['start_day'])
                end_date = _make_date(match['year'], match['month'], match['end_day'])
            else:
                match = SINGLE_DATE_PATTERN.fullmatch(normalized)
                if not match:
                    raise ArticleParsingError(
                        f'Unsupported schedule date heading: {date_label}'
                    )
                start_date = _make_date(match['year'], match['month'], match['day'])
                end_date = start_date

    if end_date < start_date:
        raise ArticleParsingError('A schedule date range ends before it starts.')
    return start_date, end_date


def _looks_like_date_heading(element, text):
    return (
        element.name == 'p'
        and element.find_parent('table') is None
        and DATE_HEADING_START_PATTERN.match(text) is not None
        and re.search(r'\b\d{4}\b', text) is not None
    )


def _map_url(value_cell, article_url):
    image = value_cell.find('img')
    if image is None:
        return None

    image_url = image.get('data-pin-media') or image.get('data-src') or image.get('src')
    if not image_url:
        return None

    absolute_url = urljoin(article_url, image_url)
    if urlparse(absolute_url).scheme not in {'http', 'https'}:
        return None
    return absolute_url


def _parse_schedule_table(
    table,
    date_label,
    date_start,
    date_end,
    article_url,
):
    fields = {}
    for row in table.find_all('tr'):
        cells = row.find_all(['th', 'td'], recursive=False)
        if len(cells) < 2:
            continue

        label = _normalize_text(cells[0].get_text(' ', strip=True)).rstrip(':').casefold()
        value_cell = cells[1]
        if label == 'map':
            fields['map_url'] = _map_url(value_cell, article_url)
        elif label in {'time', 'purpose', 'areas affected'}:
            fields[label] = _normalize_text(value_cell.get_text(' ', strip=True))

    required_fields = {'time', 'purpose', 'areas affected'}
    if not required_fields.issubset(fields) or any(
        not fields[field] for field in required_fields
    ):
        raise ArticleParsingError('A schedule table is missing required fields.')

    return {
        'date_label': date_label,
        'date_start': date_start,
        'date_end': date_end,
        'time': fields['time'],
        'purpose': fields['purpose'],
        'areas_affected': fields['areas affected'],
        'map_url': fields.get('map_url'),
    }


def _parse_article(article_html, article_url):
    soup = BeautifulSoup(article_html, 'html.parser')
    content = soup.select_one('[data-hook="post-description"]')
    if content is None:
        raise ArticleParsingError('The VECO article content could not be located.')

    current_date_label = None
    current_date_start = None
    current_date_end = None
    schedule = []
    for element in content.find_all(['p', 'table']):
        text = _normalize_text(element.get_text(' ', strip=True))
        if _looks_like_date_heading(element, text):
            current_date_label = text
            current_date_start, current_date_end = _parse_date_label(text)
            continue

        if element.name != 'table' or element.get('data-hook') != 'table-component':
            continue
        if current_date_label is None:
            raise ArticleParsingError('A schedule table has no date heading.')
        schedule.append(
            _parse_schedule_table(
                element,
                current_date_label,
                current_date_start,
                current_date_end,
                article_url,
            )
        )

    if not schedule:
        raise ArticleParsingError('The VECO article contains no schedule tables.')
    return schedule


def _fetch_article(entry, published_at):
    article_url = entry.get('link', '').strip()
    _validate_article_url(article_url)
    article_response = _request(
        article_url,
        'text/html, application/xhtml+xml;q=0.9',
        allow_redirects=False,
    )
    final_article_url = article_response.url or article_url
    _validate_article_url(final_article_url)
    schedule = _parse_article(article_response.text, final_article_url)

    description_html = entry.get('description') or entry.get('summary') or ''
    description = _normalize_text(
        BeautifulSoup(description_html, 'html.parser').get_text(' ', strip=True)
    )

    return {
        'id': _normalize_text(entry.get('id') or entry.get('guid') or article_url),
        'title': _normalize_text(entry.get('title', '')),
        'description': description,
        'url': final_article_url,
        'category': _entry_category(entry),
        'published_at': published_at,
        'image_url': _entry_image_url(entry),
        'author': _normalize_text(entry.get('author', '')),
        'schedule': schedule,
    }


def _fetch_feed_entries():
    feed_response = _request(
        settings.VECO_FEED_URL,
        'application/rss+xml, application/xml;q=0.9, text/xml;q=0.8',
    )
    return _parse_feed_entries(feed_response.content)


def get_latest_interruption():
    dated_entries = _fetch_feed_entries()
    if not dated_entries:
        raise LatestInterruptionNotFound('No service interruption was found.')
    return _fetch_article(*dated_entries[0])


def _validate_calendar_data_url(url):
    parsed_url = urlparse(url)
    is_calendar_path = (
        parsed_url.path.startswith('/spreadsheets/d/')
        and parsed_url.path.endswith('/gviz/tq')
    )
    if (
        parsed_url.scheme != 'https'
        or (parsed_url.hostname or '').casefold() != GOOGLE_CALENDAR_DOMAIN
        or not is_calendar_path
    ):
        raise CalendarParsingError('VECO_CALENDAR_DATA_URL is not a supported URL.')


def _calendar_payload(response_text):
    object_start = response_text.find('{')
    object_end = response_text.rfind('}')
    if object_start < 0 or object_end <= object_start:
        raise CalendarParsingError('VECO returned an invalid calendar response.')

    try:
        payload = json.loads(response_text[object_start : object_end + 1])
    except (TypeError, json.JSONDecodeError) as exc:
        raise CalendarParsingError('VECO returned an invalid calendar response.') from exc

    if payload.get('status') != 'ok' or not isinstance(payload.get('table'), dict):
        raise CalendarParsingError('VECO returned an unsuccessful calendar response.')
    return payload


def _calendar_columns(table):
    columns = []
    for index, column in enumerate(table.get('cols') or []):
        label = column.get('label', '') if isinstance(column, dict) else ''
        normalized_label = re.sub(r'[^a-z0-9]', '', label.casefold())
        columns.append(normalized_label or f'column{index}')

    if not CALENDAR_REQUIRED_COLUMNS.issubset(columns):
        raise CalendarParsingError('The VECO calendar columns have changed.')
    return columns


def _calendar_rows(table, columns):
    rows = table.get('rows')
    if not isinstance(rows, list):
        raise CalendarParsingError('The VECO calendar rows are missing.')

    parsed_rows = []
    for row in rows:
        cells = row.get('c') if isinstance(row, dict) else None
        if not isinstance(cells, list):
            raise CalendarParsingError('The VECO calendar contains a malformed row.')

        parsed_row = {}
        for index, column in enumerate(columns):
            cell = cells[index] if index < len(cells) else None
            if not isinstance(cell, dict):
                parsed_row[column] = ''
                continue

            value = cell.get('v')
            if column == 'exactdate' and cell.get('f'):
                value = cell['f']
            parsed_row[column] = '' if value is None else str(value)

        relevant_values = [
            parsed_row.get(column, '') for column in CALENDAR_REQUIRED_COLUMNS
        ]
        if not any(value.strip() for value in relevant_values):
            continue
        parsed_rows.append(parsed_row)
    return parsed_rows


def _calendar_date(value):
    normalized_value = _normalize_text(value)
    try:
        return date.fromisoformat(normalized_value)
    except ValueError:
        match = GOOGLE_DATE_PATTERN.fullmatch(normalized_value)
        if not match:
            raise CalendarParsingError('A VECO calendar row has an invalid date.')
        try:
            return date(
                int(match['year']),
                int(match['month']) + 1,
                int(match['day']),
            )
        except ValueError as exc:
            raise CalendarParsingError('A VECO calendar row has an invalid date.') from exc


def _calendar_map_url(value):
    map_url = _normalize_text(value)
    if not map_url:
        return None
    if urlparse(map_url).scheme not in {'http', 'https'}:
        raise CalendarParsingError('A VECO calendar row has an invalid map URL.')
    return map_url


def _calendar_status(value):
    status = _normalize_text(value)
    words = status.split()
    if words and all(word.casefold() == words[0].casefold() for word in words):
        return words[0]
    return status


def _calendar_source_id(row, event_date):
    identity = '\x1f'.join(
        (
            event_date.isoformat(),
            row['category'],
            row['title'],
            row['timeinfo'],
            row['locations'],
        )
    )
    digest = hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]
    return f'veco-calendar-{digest}'


def _parse_calendar(response_text):
    payload = _calendar_payload(response_text)
    table = payload['table']
    columns = _calendar_columns(table)
    rows = _calendar_rows(table, columns)

    events = []
    for row in rows:
        normalized_row = {
            column: _normalize_text(row.get(column, ''))
            for column in CALENDAR_REQUIRED_COLUMNS
        }
        if any(not normalized_row[field] for field in CALENDAR_REQUIRED_FIELDS):
            raise CalendarParsingError(
                'A VECO calendar row is missing required schedule information.'
            )

        event_date = _calendar_date(normalized_row['exactdate'])
        events.append(
            {
                'date_label': (
                    f'{event_date.strftime("%B")} {event_date.day}, '
                    f'{event_date.year} ({event_date.strftime("%A")})'
                ),
                'date_start': event_date,
                'date_end': event_date,
                'category': normalized_row['category'],
                'time': normalized_row['timeinfo'],
                'purpose': normalized_row['title'],
                'areas_affected': normalized_row['locations'],
                'status': _calendar_status(normalized_row['status']),
                'map_url': _calendar_map_url(normalized_row['maplinks']),
                'source_id': _calendar_source_id(normalized_row, event_date),
                'source_title': 'VECO Interruption Calendar',
                'source_url': settings.VECO_CALENDAR_PAGE_URL,
                'source_published_at': None,
            }
        )
    return events


def get_all_interruptions(target_date=None):
    _validate_calendar_data_url(settings.VECO_CALENDAR_DATA_URL)
    calendar_response = _request(
        settings.VECO_CALENDAR_DATA_URL,
        'application/json, text/javascript;q=0.9, text/plain;q=0.8',
        allow_redirects=False,
    )
    events = _parse_calendar(calendar_response.text)
    if target_date is not None:
        events = [
            event
            for event in events
            if event['date_start'] <= target_date <= event['date_end']
        ]
    return events
