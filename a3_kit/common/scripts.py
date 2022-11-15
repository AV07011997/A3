# Common Scripts
from dateutil import parser
import uuid
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from collections import deque



def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data


def generate_random_file_name(string_length=20):
    """Returns a random string of length string_length."""
	# Convert UUID format to a Python string.
    random = str(uuid.uuid4())
	# Make all characters uppercase.
    random = random.upper()
	# Remove the UUID '-'.
    random = random.replace("-","")
	# Return the random string.
    return random[0:string_length]


def normalize_date(date):
	# normalize date
    if date is None:
        return date

    string_check= re.compile('[@_!#$%^&*()<>?/\|}{~:,;]')
    try:
        if string_check.search(date) is None:
            if date.isdigit():
                s1 = date[0:2]
                s2 = date[2:4]
                s3 = date[4:]
                return parser.parse(s1+"/"+s2+"/"+s3, dayfirst=True).date()
            else:
                return parser.parse(date, dayfirst=True).date()
        else:
            date = date.replace("," , "/")
            return parser.parse(date, dayfirst=True).date()
    except:
        return None


def previous_months_list(how_many_previous_months):
	today = datetime.now()
	# Get next month and year using relativedelta
	# next_month = today + relativedelta(months=+1)
	# How many months do you want to go back?
	num_months_back = how_many_previous_months

	i = 0
	deque_months = deque()

	while i <= num_months_back:
	    curr_date = today + relativedelta(months=-i)
	    deque_months.appendleft(curr_date.strftime('%b-%y'))

	    # if i == num_months_back:
	    #     deque_months.append(next_month.strftime('%B %Y'))

	    i = i+1

	# Convert deque to list
	return list(deque_months)[1:]
