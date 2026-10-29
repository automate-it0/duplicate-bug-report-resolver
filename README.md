# HackerOne Duplicate Bug Report Resolver

A Python command-line tool for security teams and bug bounty program managers that
detects duplicate vulnerability reports on HackerOne. It fetches your program's
reports through the HackerOne API v1, compares every pair using cosine similarity
over titles and vulnerability descriptions, and posts an internal comment on newer
reports that are near-duplicates of older ones — so triagers can close duplicates
faster and reporters get credited to the original submission.

## Features

- **HackerOne API v1 integration** — authenticates with HTTP Basic Auth using your
  API token identifier and token, and fetches your program's report stream directly
  from `api.hackerone.com`.
- **Cosine similarity engine** — pure-Python vector space model over word
  frequencies; no machine-learning stack required, so the tool stays lightweight and
  auditable.
- **Chronological duplicate detection** — reports are sorted by creation date before
  comparison, guaranteeing the newer submission is always the one flagged as a
  duplicate of the older original (no circular flagging).
- **Automatic internal comments** — posts an internal team comment on each suspected
  duplicate, referencing the original report ID and the computed similarity
  percentage, keeping the discussion visible only to your triage team.
- **Configurable threshold** — tune the similarity cutoff (`--threshold`, default
  `0.8`) to balance recall versus false positives.

## Installation

Clone the repository and install the dependency:

```bash
git clone https://github.com/automate-it0/duplicate-bug-report-resolver.git
cd duplicate-bug-report-resolver
pip install -r requirements.txt
```

Requires Python 3.8+.

## Getting HackerOne API Credentials

1. Open your HackerOne **Program Settings**.
2. Under **API Tokens**, generate a new token.
3. Note the **API Token Identifier** (username) and the **API Token** (secret).

The tool needs both values at runtime; they are only used for the API calls and are
never stored by the tool.

## Usage

Run the resolver with your credentials:

```bash
python main.py --api-identifier <YOUR_IDENTIFIER> --api-token <YOUR_TOKEN>
```

With a stricter similarity threshold (fewer false positives):

```bash
python main.py --api-identifier <YOUR_IDENTIFIER> --api-token <YOUR_TOKEN> --threshold 0.9
```

### Command-line options

| Option             | Required | Description                                                        |
| ------------------ | -------- | ------------------------------------------------------------------ |
| `--api-identifier` | yes      | HackerOne API token identifier (Basic Auth username).              |
| `--api-token`      | yes      | HackerOne API token secret (Basic Auth password).                  |
| `--threshold`      | no       | Similarity score above which a pair is treated as a duplicate.      |

The threshold ranges from `0.0` (completely different texts) to `1.0` (identical
texts). The default is `0.8`.

## How It Works

1. **Fetch** — all reports are retrieved from the HackerOne API v1
   (`GET /v1/reports`) using HTTP Basic Auth.
2. **Tokenize** — each report's title and vulnerability description are split into
   lowercase alphanumeric tokens.
3. **Vectorize** — term frequency vectors are built for every report from the
   combined title + description text.
4. **Compare** — for every pair, cosine similarity is computed:

   ```text
   similarity = (A · B) / (||A|| * ||B||)
   ```

5. **Flag** — pairs scoring at or above the threshold are treated as duplicates.
   Because reports are processed oldest-first, the newer report is always the one
   flagged, and an internal comment is posted on it citing the original report ID
   and the similarity percentage.

## Example Comment

The comment posted on a flagged duplicate (visible only to your team):

```text
[System Alert] Potential duplicate detected.
This report has a 91.3% similarity with older report #123456.
```

## Notes for Operators

- Similarity is lexical, not semantic: heavily reworded reports may fall below the
  threshold, and boilerplate-heavy reports may score high. Treat flags as triage
  hints, not verdicts.
- Passing secrets on the command line exposes them in shell history; prefer a
  controlled environment or a secrets manager wrapper.
- Comments are posted as `internal`, so reporters do not see the duplicate
  annotation until your team acts on it.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
