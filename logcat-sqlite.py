#!/usr/bin/python
''' Copyright 2009, The Android Open Source Project

    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License. 
    You may obtain a copy of the License at 

        http://www.apache.org/licenses/LICENSE-2.0 

    Unless required by applicable law or agreed to in writing, software 
    distributed under the License is distributed on an "AS IS" BASIS, 
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
    See the License for the specific language governing permissions and 
    limitations under the License.
'''

# Script to write adb logcat console output to sqlite3 database.
# Inspired by jsharkey's coloredlogcat.py https://github.com/jsharkey/android-tools/

import os, sys, re, StringIO
import fcntl, termios, struct, traceback
import sqlite3

# if someone is piping in to us, use stdin as input.  if not, invoke adb logcat
if os.isatty(sys.stdin.fileno()):
    # to pick up -d or -e
    adb_args = ' '.join(sys.argv[1:])
    input = os.popen("adb %s logcat -v time" % adb_args)
else:
    input = sys.stdin

v_time = re.compile(r'^(\d{2}-\d{2} \d{2}:\d{2}:[\d\.]{6})\s+([SFEWIDV])\/(.+): (.*)$')

db = sqlite3.connect(r'logcat.db')
db.text_factory = str
cur = db.cursor()
cur.execute(r'CREATE TABLE IF NOT EXISTS logcat(tstamp TIMESTAMP, level TEXT, source TEXT, message TEXT)')

count = 0
while True:
    try:
        line = input.readline()
    except KeyboardInterrupt:
        break

    line = line.expandtabs(4)
    if len(line) == 0: break
    
    match = v_time.match(line)
    if not match:
        print line,
        continue
    
#    month, day, hour, minute, seconds, level, source, message = match.groups()
    tstamp, level, source, message = match.groups()
    tstamp = '2019-' + str(tstamp)
    try:
        cur.execute(r'INSERT INTO logcat VALUES(?,?,?,?)', (str(tstamp), str(level), str(source), str(message)))
        count = count + 1
    except:
        traceback.print_exc(file=sys.stderr)
        print "Wrote ",count," messages"
        print tstamp, level, source, message
        break

db.commit()
cur.close()
db.close()

