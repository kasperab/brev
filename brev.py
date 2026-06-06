import importlib
import json
import os
import re
import urllib.request

def get_config(config_path):
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

def get_feed_paths(top_directory, file_ending):
	paths = []
	for directory, _, files in os.walk(top_directory):
		for file in files:
			if file.endswith(file_ending):
				paths.append(os.path.join(directory, file))
	return paths

def get_feed(path):
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

def fetch_raw_feed(url):
	try:
		with urllib.request.urlopen(url) as response:
			if response.status == 200:
				encoding = response.headers.get_content_charset()
				if encoding is None:
					encoding = "utf-8"
				return True, response.read().decode(encoding)
			else:
				return False, response.status
	except Exception as e:
		return False, e

def import_parsers():
	parsers = {}
	for file in os.listdir():
		if file.endswith(".py"):
			name = file[:-len(".py")]
			parsers[name] = importlib.import_module(name)
	return parsers

def regex_parse(raw_feed, pattern_string):
	entries = []
	pattern = re.compile(pattern_string)
	for line in raw_feed.splitlines():
		if pattern.search(line):
			entries.append(line.strip())
	return entries

def get_new_entries(entries, old_entries, feed_name, output_format):
	out = ""
	for entry in entries:
		if entry not in old_entries:
			out += output_format.format(feed_name = feed_name, entry = entry) + "\n"
	return out

def save_feed(path, url, parser, entries):
	with open(path, "w") as file:
		file.write("{url}\n{parser}\n{entries}\n".format(url = url, parser = parser, entries = "\n".join(entries)))

def error_log(error):
	print(error)
	return error + "\n"

def run(config_path):
	config = get_config(config_path)
	if config is None:
		return
	out = ""
	feed_paths = get_feed_paths(config["feeds_directory"], config["feeds_file_ending"])
	parsers = import_parsers()
	for path in feed_paths:
		feed_name = path[len(config["feeds_directory"]) + 1:-len(config["feeds_file_ending"])]
		success, feed = get_feed(path)
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
	mode = "w"
	if os.path.isfile(config["output_file"]):
		mode = "a"
	with open(config["output_file"], mode) as file:
		file.write(out)

if __name__ == "__main__":
	run("config.json")
