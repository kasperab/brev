import json
import os
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
			return feed
		except:
			return None

def fetch_raw_feed(url):
	try:
		with urllib.request.urlopen(url) as response:
			if response.status == 200:
				return response.read().decode(response.headers.get_content_charset())
			else:
				return None
	except:
		return None

def error_log(error):
	print(error)
	return error + "\n"

def run(config_path):
	config = get_config(config_path)
	if config is None:
		return
	out = ""
	feed_paths = get_feed_paths(config["feeds_directory"], config["feeds_file_ending"])
	for path in feed_paths:
		feed_name = path[len(config["feeds_directory"]) + 1:-len(config["feeds_file_ending"])]
		feed = get_feed(path)
		if feed is None:
			out += error_log(f"FAILED TO LOAD FEED FILE '{path}'")
			continue
		raw_feed = fetch_raw_feed(feed["url"])
		if raw_feed is None:
			out += error_log(f"FAILED TO FETCH FEED '{feed_name}' FROM '{feed['url']}'")
			continue
	mode = "w"
	if os.path.isfile(config["output_file"]):
		mode = "a"
	with open(config["output_file"], mode) as file:
		file.write(out)

if __name__ == "__main__":
	run("config.json")
