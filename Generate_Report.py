#!/usr/bin/python

import re
import sys
from datetime import datetime, date, timedelta
from collections import Counter

# To define the number of days considered in the Apache common log format.
try:
  Number_of_Days = int(sys.argv[1])
except:
  Number_of_Days = 1
Day_Interval = date.today() - timedelta(Number_of_Days)
apacheDay = Day_Interval.strftime('[%d/%b/%Y:')

# Regex for the Apache common log format.
parts = [
    r'(?P<host>\S+)',                   # host %h
    r'\[(?P<time>.+)\]',                # time %t
    r'"(?P<request>.*)"',               # request "%r"
    r'(?P<status>[0-9]+)',              # status %>s
    r'(?P<size>\S+)',                   # size %b 
    r'"(?P<language>.*)"',              # Language%l
]
pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')

# Regex for request.
feed = re.compile(r'/all-this/(\d\d\d\d/\d\d/[^/]+/)?feed/(atom/)?')

# Change Apache log items into Python types.
def change_to_python_format(d):
  # Clean up the request.
  d["request"] = d["request"].split()[1]
  
  # Some dashes become None.
  for k in ("language"):
    if d[k] == "-":
      d[k] = None
      
  # The size dash becomes 0.
  if d["size"] == "-":
    d["size"] = 0
  else:
    d["size"] = int(d["size"])
  
  # Convert the timestamp into a datetime object. Accept the server's time zone.
  time, zone = d["time"].split()
  d["time"] = datetime.strptime(time, "%d/%b/%Y:%H:%M:%S")
  
  return d
# It checks if it downloaded or not?

def is_downloaded(hit):
  hit["status"] = int(hit["status"])
  if hit["status"] < 200 or hit["status"] >= 300:
    return False
  
  # Requests that aren't GET.
  if hit["request"][0:3] != "GET":
    return False

  # Audio
  if hit["request"].split()[1][-1] != '/':
    return False
  
  # Must be a page.
  return True  

# Regenumber of days considered.
internal = re.compile(r'https?://(www\.)?speechmatics\.com.*')

# It accepts a dictionary associated with a line from the Apache log file
def accessed(hit):
  if hit['language']:
    return not (
                internal.search(hit['language']))
  else:
    return False

# Initialize. 
pages = []

# Parse all the lines associated with the day of interest.
for line in sys.stdin:
  if apacheDay in line:
    m = pattern.match(line)
    hit = m.groupdict()
    if is_downloaded(hit):
      pages.append(change_to_python_format(hit))
    else:
      continue

# Show the top five pages and the total.
print '%s pages' % Day_Interval.strftime("%b %d, %Y")
Language_Downlaoded = Counter(x['request'] for x in pages)
top_5_languages = Language_Downlaoded.most_common(5)
for p in top_5_languages:
  print "  %5d  %s" % p[::-1]
print "  %5d  total" % len(pages)

# Show the top five languages.
print '''

%s languages''' % Day_Interval.strftime("%b %d, %Y")
languages = Counter(x['language'] for x in pages if accessed(x) )
top_5_languages = languages.most_common(5)
for r in top_5_languages:
  print "  %5d  %s" % r[::-1]

# Initiazlie required variables
log_data = []

status_counter = Counter(x['status'] for x in log_data)
# Prints the STATUS count sorted from the highest to lowest count
for x in status_counter.most_common():
  print "\t%s Status %d times" % x

