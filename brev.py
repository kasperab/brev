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

def run(config_path):
	config = get_config(config_path)
	if config is None:
		return

if __name__ == "__main__":
	run("config.json")
