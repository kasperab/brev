import json
import os

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
			error = f"ERROR LOADING FILE FOR FEED '{feed_name}'"
			print(error)
			out += error + "\n"
			continue
	if os.path.isfile(config["output_file"]):
		with open(config["output_file"], "a") as file:
			file.write(out)
	else:
		with open(config["output_file"], "w") as file:
			file.write(out)

if __name__ == "__main__":
	run("config.json")
