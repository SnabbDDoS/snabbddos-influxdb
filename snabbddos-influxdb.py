#!/usr/bin/env python3
import datetime
import os
import random
import struct
import time

from influxdb import InfluxDBClient

HOSTNAME = 'foo'

# connect to localhost and use database 'snabbddos' with credentials below
client = InfluxDBClient('localhost', 8086, 'username', 'password', 'snabbddos')

snabb_run = "/var/run/snabb"
snabb_dir = None

def read_file(filename):
	f = open(filename, "rb")
	content = struct.unpack('Q', f.read(8))[0]
	f.close()
	return content

# read counter
def rc(counter_name):
	return read_file(snabb_dir + counter_name)

while True:
	time.sleep(1)

	try:
		instances = os.listdir(snabb_run)
		if len(instances) == 0:
			print("No snabb instances - waiting")
			continue
		if len(instances) > 1:
			print("More than one snabb instance - dunno what to do")
			continue

		snabb_dir = snabb_run + "/" + instances[0]
		breaths = rc("/engine/breaths")
		dirty_packets = rc("/snabbddos/dirty_packets")
		dirty_bytes = rc("/snabbddos/dirty_bytes")

		ts = datetime.datetime.utcnow().isoformat().replace(" ", "T") + "Z"

		json_body = [
				{
					"measurement": "snabbddos",
					"tags": {
						"host": HOSTNAME
					},
					"time": ts,
					"fields": {
						"breaths": rc("/engine/breaths"),
						"blacklisted_hosts": rc("/snabbddos/blacklisted_hosts"),
						"running_mitigations": rc("/snabbddos/running_mitigations"),
						"num_sources": rc("/snabbddos/num_sources"),
						"dirty_packets": rc("/snabbddos/dirty_packets"),
						"dirty_bytes": rc("/snabbddos/dirty_bytes"),
						"non_ipv4_packets": rc("/snabbddos/non_ipv4_packets"),
						"non_ipv4_bytes": rc("/snabbddos/non_ipv4_bytes"),
						"blacklisted_packets": rc("/snabbddos/blacklisted_packets"),
						"blacklisted_bytes": rc("/snabbddos/blacklisted_bytes"),
						"no_mitigation_packets": rc("/snabbddos/no_mitigation_packets"),
						"no_mitigation_bytes": rc("/snabbddos/no_mitigation_bytes"),
						"no_rule_packets": rc("/snabbddos/no_rule_packets"),
						"no_rule_bytes": rc("/snabbddos/no_rule_bytes"),
						"blocked_packets": rc("/snabbddos/blocked_packets"),
						"blocked_bytes": rc("/snabbddos/blocked_bytes"),
						"passed_packets": rc("/snabbddos/passed_packets"),
						"passed_bytes": rc("/snabbddos/passed_bytes"),
						"exceed_packets": rc("/snabbddos/exceed_packets"),
						"exceed_bytes": rc("/snabbddos/exceed_bytes"),
						"conform_packets": rc("/snabbddos/conform_packets"),
						"conform_bytes": rc("/snabbddos/conform_bytes"),
					}
				},
			]
				
		res = client.write_points(json_body)
	except:
		continue
