#!/usr/bin/env python3
"""
Duplicate Bug Report Resolver
Automates duplicate detection and flagging on HackerOne using text similarity and HTTP Basic Auth.
"""

import argparse
import collections
import logging
import math
import re
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def tokenize(text):
    """Tokenizes text into lowercase alphanumeric words."""
    if not text:
        return []
    return re.findall(r'\w+', text.lower())

def calculate_cosine_similarity(text1, text2):
    """Calculates cosine similarity between two texts using word frequencies."""
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    if not tokens1 or not tokens2:
        return 0.0
    
    freq1 = collections.Counter(tokens1)
    freq2 = collections.Counter(tokens2)
    
    all_words = set(freq1.keys()).union(set(freq2.keys()))
    
    dot_product = sum(freq1.get(w, 0) * freq2.get(w, 0) for w in all_words)
    mag1 = math.sqrt(sum(freq1[w]**2 for w in freq1))
    mag2 = math.sqrt(sum(freq2[w]**2 for w in freq2))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)

def fetch_bug_reports(api_identifier, api_token):
    """
    Fetch bug reports from HackerOne API using HTTP Basic Authentication.
    """
    url = 'https://api.hackerone.com/v1/reports'
    try:
        logging.info("Fetching reports from HackerOne...")
        # HackerOne API uses Basic Auth with (identifier, token)
        response = requests.get(url, auth=HTTPBasicAuth(api_identifier, api_token))
        response.raise_for_status()
        data = response.json().get('data', [])
        logging.info(f"Successfully fetched {len(data)} reports.")
        return data
    except RequestException as e:
        logging.error(f'Error fetching bug reports: {e}')
        return []

def analyze_bug_reports(bug_reports, threshold=0.8):
    """
    Analyze bug reports to detect duplicates chronologically.
    Returns pairs where the newer report is flaggable as a duplicate of the older report.
    """
    duplicates = []
    # Sort reports chronologically by creation date (oldest first)
    # Using 'created_at' if available, otherwise fallback to id
    sorted_reports = sorted(
        bug_reports, 
        key=lambda x: x.get('attributes', {}).get('created_at', x.get('id'))
    )
    
    for i in range(len(sorted_reports)):
        report_a = sorted_reports[i]
        title_a = report_a.get('attributes', {}).get('title', '')
        desc_a = report_a.get('attributes', {}).get('vulnerability_information', '')
        
        for j in range(i + 1, len(sorted_reports)):
            report_b = sorted_reports[j]
            title_b = report_b.get('attributes', {}).get('title', '')
            desc_b = report_b.get('attributes', {}).get('vulnerability_information', '')
            
            # Compare reports using cosine similarity on title and body
            similarity = calculate_cosine_similarity(f"{title_a} {desc_a}", f"{title_b} {desc_b}")
            
            if similarity >= threshold:
                logging.info(
                    f"Potential duplicate detected: Report #{report_b['id']} "
                    f"similar to older Report #{report_a['id']} (Similarity: {similarity:.2f})"
                )
                duplicates.append((report_b, report_a, similarity))
                
    return duplicates

def add_duplicate_comment(api_identifier, api_token, duplicate_report, original_report, similarity):
    """
    Adds a comment on the duplicate (newer) report referencing the original (older) report.
    """
    report_id = duplicate_report['id']
    url = f'https://api.hackerone.com/v1/reports/{report_id}/activities'
    
    payload = {
        "data": {
            "type": "activity-comment",
            "attributes": {
                "message": (
                    f"⚠️ [System Alert] Potential duplicate detected.\n"
                    f"This report has a {similarity*100:.1f}% similarity with older report #{original_report['id']}."
                ),
                "internal": True # Posted as an internal comment for team review
            }
        }
    }
    
    try:
        response = requests.post(
            url, 
            auth=HTTPBasicAuth(api_identifier, api_token), 
            json=payload
        )
        response.raise_for_status()
        logging.info(f"Flagged report #{report_id} as duplicate of #{original_report['id']}")
    except RequestException as e:
        logging.error(f"Error flagging duplicate report #{report_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description='HackerOne Duplicate Bug Report Resolver')
    parser.add_argument('--api-identifier', required=True, help='HackerOne API Token Identifier')
    parser.add_argument('--api-token', required=True, help='HackerOne API Token Secret')
    parser.add_argument('--threshold', type=float, default=0.8, help='Similarity threshold (0.0 to 1.0)')
    args = parser.parse_args()

    bug_reports = fetch_bug_reports(args.api_identifier, args.api_token)
    if not bug_reports:
        logging.warning("No reports retrieved. Exiting.")
        return

    duplicate_pairs = analyze_bug_reports(bug_reports, threshold=args.threshold)
    for dup_report, orig_report, similarity in duplicate_pairs:
        add_duplicate_comment(args.api_identifier, args.api_token, dup_report, orig_report, similarity)

if __name__ == '__main__':
    main()