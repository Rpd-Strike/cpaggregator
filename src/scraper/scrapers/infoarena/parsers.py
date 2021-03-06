import re
import datetime
import pytz
import time

from core.logging import log

MONTH_ENCODINGS = ['ian', 'feb', 'mar', 'apr', 'mai', 'iun', 'iul', 'aug', 'sep', 'oct', 'nov', 'dec']

TAG_DICT = {
    "Structuri de Date": "data-structures",
    "Geometrie": "geometry",
    "Matematica": "math",
    "Grafuri": "graphs",
    "Sortare": "sorting",
    "Backtracking": "backtracking",
    "Programare dinamica": "dp",
    "Greedy": "greedy",
    "Siruri de caractere": "strings",
    "Cautare": "search",
    "Divide et Impera": "divide",
}


def parse_tag(tag_text):

    if tag_text in TAG_DICT:
        return TAG_DICT[tag_text]

    log.warning(f"Unknown tag: '{tag_text}'.")
    return None


def parse_submission_count(submission_count_text: str):
    result = re.search(r"(\d+) rezultate", submission_count_text)
    if result is None:
        raise ValueError(f"Cannot parse submission count: {submission_count_text}")
    return int(result.group(1))


def parse_time_limit(time_limit_text: str):
    result = re.search(r'(\d+(\.\d+)?) sec', time_limit_text)
    if result is None:
        raise ValueError("Cannot parse time limit: %s" % time_limit_text)
    return int(1000 * float(result.group(1)))


def parse_memory_limit(memory_limit_text: str):
    result = re.search(r'(\d+) kbytes', memory_limit_text)
    if result is None:
        raise ValueError("Cannot parse memory limit: %s" % memory_limit_text)
    return int(result.group(1))


def parse_score(score_text: str):
    result = re.search(r'(Evaluare completa|Eroare de compilare): (\d+) puncte', score_text)
    if result is None:
        log.warning(f"Could not parse score from '{score_text}'")
        return None
    return int(result.group(2))


def parse_verdict(verdict_text: str):
    if ':' not in verdict_text:
        return None

    verdict, points = map(str.strip, verdict_text.split(':'))
    if verdict == 'Evaluare completa':
        if points == '100 puncte':
            return 'AC'
        return 'WA'
    if verdict == 'Eroare de compilare':
        return 'CE'
    log.warning(f"Could not parse verdict: '{verdict_text}'")
    return 'WA'


def parse_date(date_text: str):
    day, month, year, tm = date_text.split()
    hour, minute, second = tm.split(':')

    dt = datetime.datetime(
        year=2000 + int(year),
        month=MONTH_ENCODINGS.index(month) + 1,
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
    )
    ts = time.mktime(pytz.timezone("Europe/Bucharest").localize(dt).utctimetuple())
    return datetime.datetime.utcfromtimestamp(ts)


def parse_source_size(source_text: str):
    result = re.search(r'(\d+\.\d\d) kb', source_text)
    if result is None:
        raise ValueError(f"Could not parse source size: {source_text}")
    return int(float(result.group(1)) * 1000)