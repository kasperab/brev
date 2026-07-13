import importlib
import json
import os
import re
import sys
import urllib.request

# Takes path to config file
# Returns dictionary representing config if successful
# Returns None if not successful
def load_config(config_path):
	if not os.path.isfile(config_path):
		print("CONFIG FILE NOT FOUND")
		return None
	with open(config_path, "r") as file:
		data = json.load(file)
		complete = True
		if "output_file" not in data:
			print("CONFIG FILE MISSING 'output_file'")
			complete = False
		if "output_format" not in data:
			print("CONFIG FILE MISSING 'output_format'")
			complete = False
		if "feeds_directory" not in data:
			print("CONFIG FILE MISSING 'feeds_directory'")
			complete = False
		if "feeds_file_ending" not in data:
			print("CONFIG FILE MISSING 'feeds_file_ending'")
			complete = False
		if complete:
			return data
		return None

# Takes directory to look for feeds in and file ending for feeds
# Returns list containing paths to all found feeds
def get_feed_paths(top_directory, file_ending):
	paths = []
	for directory, _, files in os.walk(top_directory):
		for file in files:
			if file.endswith(file_ending):
				paths.append(os.path.join(directory, file))
	return paths

# Takes path to feed file
# Returns True and dictionary representing feed if successful
# Returns False and error message if not successful
def load_feed(path):
	with open(path, "r") as file:
		try:
			lines = file.read().splitlines()
			feed = {}
			feed["url"] = lines[0]
			feed["parser"] = lines[1]
			feed["entries"] = lines[2:]
			return True, feed
		except Exception as e:
			return False, e

# Takes URL
# Returns True and content at URL if successful
# Returns False and error message if not successful
def fetch_raw_feed(url):
	try:
		request = urllib.request.Request(url)
		request.add_header("User-Agent", "brev")
		with urllib.request.urlopen(request) as response:
			if response.status == 200:
				encoding = response.headers.get_content_charset()
				if encoding is None:
					encoding = "utf-8"
				return True, response.read().decode(encoding)
			else:
				return False, response.status
	except Exception as e:
		return False, e

# Returns dictionary containing imported modules from same directory as this file
def import_parsers():
	parsers = {}
	for file in os.listdir():
		if file.endswith(".py") and file != sys.argv[0]:
			name = file[:-len(".py")]
			parsers[name] = importlib.import_module(name)
	return parsers

# Takes raw feed string and regex pattern string
# Returns list containing all lines in raw feed that match regex pattern
def regex_parse(raw_feed, pattern_string):
	entries = []
	pattern = re.compile(pattern_string)
	for line in raw_feed.splitlines():
		if pattern.search(line):
			entries.append(line.strip())
	return entries

# Takes list containing current entries, list containing old entries, feed name, and output format
# Returns string containing every new entry in specified format on separate lines
def get_new_entries(entries, old_entries, feed_name, output_format):
	out = ""
	for entry in entries:
		if entry not in old_entries:
			out += output_format.format(feed_name = feed_name, entry = entry) + "\n"
	return out

# Takes feed path, URL, parser name, and list of entries
# Saves URL, parser name, and entries to file at specified path
def save_feed(path, url, parser, entries):
	with open(path, "w") as file:
		file.write("{url}\n{parser}\n{entries}\n".format(url = url, parser = parser, entries = "\n".join(entries)))

# Takes error
# Prints error
# Returns error with newline character appended
def error_log(error):
	print(error)
	return error + "\n"

# Takes path to config file
# Tries to load config file, update all feeds, and output new entries to file specified in config
def run(config_path):
	config = load_config(config_path)
	if config is None:
		return
	out = ""
	feed_paths = get_feed_paths(config["feeds_directory"], config["feeds_file_ending"])
	parsers = import_parsers()
	for path in feed_paths:
		feed_name = path[len(config["feeds_directory"]) + 1:-len(config["feeds_file_ending"])]
		success, feed = load_feed(path)
		if not success:
			out += error_log(f"FAILED TO LOAD FEED FILE '{path}' ({feed})")
			continue
		success, raw_feed = fetch_raw_feed(feed["url"])
		if not success:
			out += error_log(f"FAILED TO FETCH FEED '{feed_name}' FROM '{feed['url']}' ({raw_feed})")
			continue
		if feed["parser"] in parsers:
			try:
				entries = parsers[feed["parser"]].parse(raw_feed)
			except Exception as e:
				out += error_log(f"FAILED TO PARSE FEED '{feed_name}' WITH PARSER '{feed['parser']}' ({e})")
				continue
		else:
			entries = regex_parse(raw_feed, feed["parser"])
		out += get_new_entries(entries, feed["entries"], feed_name, config["output_format"])
		save_feed(path, feed["url"], feed["parser"], entries)
	with open(config["output_file"], "a") as file:
		file.write(out)

# Takes path to feed file
# Tries to update specified feed
def update_feed(path):
	success, feed = load_feed(path)
	if not success:
		print(feed)
		return
	success, raw_feed = fetch_raw_feed(feed["url"])
	if not success:
		print(raw_feed)
		return
	parsers = import_parsers()
	if feed["parser"] in parsers:
		try:
			entries = parsers[feed["parser"]].parse(raw_feed)
		except Exception as e:
			print(e)
			return
	else:
		entries = regex_parse(raw_feed, feed["parser"])
	save_feed(path, feed["url"], feed["parser"], entries)

if __name__ == "__main__":
	if len(sys.argv) > 1:
		update_feed(sys.argv[1])
	else:
		run("config.json")
