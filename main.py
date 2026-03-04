import argparse
import logging
import requests
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_bug_reports(hackerone_api_key, hackerone_api_secret):
    """
    Fetch bug reports from HackerOne API.

    Args:
        hackerone_api_key (str): HackerOne API key.
        hackerone_api_secret (str): HackerOne API secret.

    Returns:
        list: List of bug reports.
    """
    try:
        url = 'https://api.hackerone.com/v1/reports'
        headers = {
            'Authorization': f'Bearer {hackerone_api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']
    except RequestException as e:
        logging.error(f'Error fetching bug reports: {e}')
        return []

def analyze_bug_reports(bug_reports):
    """
    Analyze bug reports to detect duplicates.

    Args:
        bug_reports (list): List of bug reports.

    Returns:
        list: List of duplicate bug reports.
    """
    duplicate_reports = []
    for report in bug_reports:
        # Simple duplicate detection based on title and description
        duplicate = next((r for r in bug_reports if r['title'] == report['title'] and r['description'] == report['description'] and r['id'] != report['id']), None)
        if duplicate:
            duplicate_reports.append((report, duplicate))
    return duplicate_reports

def appeal_duplicate_reports(hackerone_api_key, hackerone_api_secret, duplicate_reports):
    """
    Appeal duplicate bug reports.

    Args:
        hackerone_api_key (str): HackerOne API key.
        hackerone_api_secret (str): HackerOne API secret.
        duplicate_reports (list): List of duplicate bug reports.
    """
    try:
        url = 'https://api.hackerone.com/v1/reports'
        headers = {
            'Authorization': f'Bearer {hackerone_api_key}',
            'Content-Type': 'application/json'
        }
        for report, duplicate in duplicate_reports:
            data = {
                'report_id': report['id'],
                'appeal_reason': 'Duplicate report'
            }
            response = requests.post(url + '/appeal', headers=headers, json=data)
            response.raise_for_status()
            logging.info(f'Appealed duplicate report {report["id"]}')
    except RequestException as e:
        logging.error(f'Error appealing duplicate reports: {e}')

def main():
    parser = argparse.ArgumentParser(description='Duplicate Bug Report Resolver')
    parser.add_argument('--hackerone-api-key', required=True, help='HackerOne API key')
    parser.add_argument('--hackerone-api-secret', required=True, help='HackerOne API secret')
    args = parser.parse_args()

    bug_reports = fetch_bug_reports(args.hackerone_api_key, args.hackerone_api_secret)
    duplicate_reports = analyze_bug_reports(bug_reports)
    appeal_duplicate_reports(args.hackerone_api_key, args.hackerone_api_secret, duplicate_reports)

if __name__ == '__main__':
    main()