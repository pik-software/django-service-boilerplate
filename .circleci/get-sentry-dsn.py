import argparse
from datetime import datetime

import requests

parser = argparse.ArgumentParser()

parser.add_argument('-t', '--team',
                    dest="team",
                    help="Team slug", default="nsi")

parser.add_argument('-o', '--organization',
                    dest="organization",
                    help="Organization slug", default="sentry")

parser.add_argument('-p', '--project',
                    dest="project",
                    help="Project slug", default="default")

parser.add_argument('-k', '--api-key',
                    dest="api_key", action='store',
                    help="Sentry api key", required=True)

parser.add_argument('-a', '--api-prefix',
                    dest="api_prefix", action='store',
                    help="Sentry api prefix", required=True)

args = parser.parse_args()

API_VERSION = '0'
API_URL = f'{args.api_prefix}{API_VERSION}/'

ORGANIZATION_LIST_URL = f'{API_URL}organizations/'
ORGANIZATION_URL = f'{ORGANIZATION_LIST_URL}{args.organization}/'

TEAM_LIST_URL = f'{ORGANIZATION_URL}teams/'
TEAM_URL = f'{API_URL}teams/{args.organization}/{args.team}/'

PROJECT_LIST_URL = f'{TEAM_URL}projects/'
PROJECT_URL = f'{API_URL}projects/{args.organization}/{args.project}/'

KEYS_URL = f'{PROJECT_URL}keys/'

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {args.api_key}"})


response = session.get(ORGANIZATION_URL)
if response.status_code == 404:
    response = session.post(ORGANIZATION_LIST_URL, data={'name': args.organization, 'slug': args.organization, 'agreeTerms': True})
    response.raise_for_status()
else:
    response.raise_for_status()
organization = response.json()


response = session.get(TEAM_URL)
if response.status_code == 404:
    response = session.post(TEAM_LIST_URL, data={'name': args.team, 'slug': args.team})
    response.raise_for_status()
else:
    response.raise_for_status()
team = response.json()


response = session.get(PROJECT_URL)
if response.status_code == 404:
    response = session.post(PROJECT_LIST_URL, data={'organization': args.organization, 'team': args.team, 'name': args.project, 'slug': args.project})
    response.raise_for_status()
else:
    response.raise_for_status()
project = response.json()


response = session.get(PROJECT_URL)
if response.status_code == 404:
    response = session.post(PROJECT_LIST_URL, data={'organization': args.organization, 'team': args.team, 'name': args.project, 'slug': args.project})
    response.raise_for_status()
else:
    response.raise_for_status()
project = response.json()


response = session.get(KEYS_URL)
response.raise_for_status()
keys = response.json()
if not keys:
    response = session.post(KEYS_URL, data={'organization': args.organization, 'team': args.team, 'name': datetime.now()})
    key = response.json()
else:
    key = keys[0]

print(key['dsn']['public'])
