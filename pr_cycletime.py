#!/usr/bin/python

import argparse
import sys
import requests
import csv
import json

from dateutil import parser
from datetime import datetime

from bs4 import BeautifulSoup

# Outputs the result in csv file. VPN connection required, in order to access BB.
#
# Examples to call ./pr_cycletime.py --url https://bitbucket.tomtomgroup.com
#                   --username milosevi --password $BB_PASS --project NavKit2
#                   --repository nk2-navigation-trip --slugs milosevi zafirovi
#                   --since 08-08-2022 --until 25-09-2022


def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=True, help='Bitbucket URL')
    parser.add_argument('--project', type=str, required=True, help='project')
    parser.add_argument('--repository', type=str, required=True, help='Repository name')
    parser.add_argument('--username', type=str, required=True, help='Your account username')
    parser.add_argument('--password', type=str, required=True, help='Your account password')
    parser.add_argument("--authors", nargs="*", type=str, default=[],
        help="List of authors")
    parser.add_argument("--slugs", nargs="*", type=str, default=[],
        help="List of slugs")
    parser.add_argument("--output", type=str, required=False, help='Output file name')
    parser.add_argument('--since', type=lambda s: datetime.strptime(s, '%d-%m-%Y'),
        required=False, help='Since date in format DD-MM-YYYY')
    parser.add_argument('--until', type=lambda s: datetime.strptime(s, '%d-%m-%Y'),
        required=False, help='Until date in format DD-MM-YYYY')

    return parser.parse_args()
    # autopep8: on


class PullRequest:
    def __init__(self, pr_id, title, author, slug, state, created, closed):
        self.pr_id = pr_id
        self.title = title
        self.author = author
        self.slug = slug
        self.state = state
        self.created = created
        self.closed = closed


args = setup_parser()

bitbucket_url = args.url
project = args.project
repository = args.repository
since = args.since
until = args.until

START_STRING = "{initialData:"
END_STRING = ", gettingStarted: false, pullRequestOrder: 'newest', selectedAuthor: null"

s = requests.Session()
s.auth = (args.username, args.password)


def get_date_from_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000)


def subtract_dates(minuend, subtrahend):
    if minuend is None or subtrahend is None:
        return None
    else:
        return round(((minuend - subtrahend).total_seconds() / 86400), 2)


def get_pull_requests():
    pull_request_list = []
    get_prs_url = bitbucket_url + '/projects/' + project + \
        '/repos/' + repository + '/pull-requests?state=ALL'
    is_last_page = False

    while not is_last_page:
        response = s.get(
            get_prs_url,
            params={
                'start': len(pull_request_list),
                'limit': 1000,
                'sinceDate': since,
                'untilDate': until})

        parsed = BeautifulSoup(response.content.decode("utf-8"), 'html.parser')
        scripts = parsed.find_all('script')
        the_script = None

        for i in range(0, len(scripts)):
            if scripts[i].string and START_STRING in scripts[i].string:
                the_script = scripts[i].string
            i = i + 1

        the_script_string = the_script.string
        start_loc = the_script_string.find(START_STRING) + len(START_STRING)
        end_loc = the_script_string.rfind(END_STRING)
        useful_data = the_script_string[start_loc:end_loc]
        json_data = json.loads(useful_data)

        for pr_details in json_data['values']:

            pd_id = pr_details['id']
            title = pr_details['title']
            author = pr_details['author']['user']['displayName']
            slug = pr_details['author']['user']['slug']
            state = pr_details['state']
            created = get_date_from_timestamp(pr_details['createdDate'])

            if pr_details['closed'] is True:
                closed = get_date_from_timestamp(pr_details['closedDate'])
            else:
                closed = None

            pull_request_list.append(
                PullRequest(
                    pd_id,
                    title,
                    author,
                    slug,
                    state,
                    created,
                    closed))

        is_last_page = json_data['isLastPage']

    return pull_request_list


def get_pr_activities(pull_request):

    counter = 0
    comment_dates = []
    approval_dates = []

    pr_url = bitbucket_url + '/rest/api/latest/projects/' + project + '/repos/' + \
        repository + '/pull-requests/' + str(pull_request.pr_id) + '/activities'

    is_last_page = False

    while not is_last_page:

        pr_response = s.get(
            pr_url,
            params={
                'start': counter,
                'limit': 500}).json()

        for pr_activity in pr_response['values']:
            counter += 1

            if pr_activity['action'] == 'COMMENTED':
                comment_timestamp = pr_activity['comment']['createdDate']
                comment_dates.append(
                    get_date_from_timestamp(comment_timestamp))
            elif pr_activity['action'] == 'APPROVED':
                approval_timestamp = pr_activity['createdDate']
                approval_dates.append(
                    get_date_from_timestamp(approval_timestamp))

            is_last_page = pr_response['isLastPage']

    if not approval_dates:
        approval_time = None
    else:
        approval_time = approval_dates[0]

    return approval_time


print('Collecting a list of pull requests from the repository', repository)

output = args.output if args.output is not None else "pr_cycletime_{}.csv".format(
    repository)

with open(output, mode='w', newline='', encoding='utf-8') as report_file:
    report_writer = csv.writer(
        report_file,
        delimiter=',',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL)
    report_writer.writerow(['id',
                            'title',
                            'author',
                            'state',
                            'created',
                            'approved',
                            'closed',
                            'cycle_time_d',
                            'time_to_approve_d',
                            'time_to_merge_d'])

    for pull_request in get_pull_requests():

        if since and pull_request.created < since:
            continue

        if until and pull_request.closed and pull_request.closed > until:
            continue

        if args.authors and pull_request.author not in args.authors:
            continue

        if args.slugs and pull_request.slug not in args.slugs:
            continue

        print('Processing pull request', pull_request.pr_id)
        approval = get_pr_activities(pull_request)
        cycle_time = subtract_dates(pull_request.closed, pull_request.created)
        time_to_approve = subtract_dates(approval, pull_request.created)
        time_to_merge = subtract_dates(pull_request.closed, approval)

        if pull_request.state == "OPEN":
            cycle_time = subtract_dates(datetime.now(), pull_request.created)

        report_writer.writerow([pull_request.pr_id,
                                pull_request.title,
                                pull_request.author,
                                pull_request.state,
                                pull_request.created,
                                approval,
                                pull_request.closed,
                                cycle_time,
                                time_to_approve,
                                time_to_merge])

print('The resulting CSV file is saved to the current folder.')
