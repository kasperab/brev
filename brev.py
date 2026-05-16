import json
import os

def run(config):
	if not os.path.isfile(config):
		print("Config file not found")
		return
	output_file = None
	feeds_directory = None
	feeds_ending = None
	with open(config, "r") as file:
		data = json.load(file)
		if "outputFile" not in data or "feedsDirectory" not in data or "feedsFileEnding" not in data:
			print("Config file missing parameters")
			return
		output_file = data["outputFile"]
		feeds_directory = data["feedsDirectory"]
		feeds_ending = data["feedsFileEnding"]

if __name__ == "__main__":
	run("config.json")
