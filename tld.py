# Parser for specifically https://data.iana.org/TLD/tlds-alpha-by-domain.txt
# Takes a string and returns a list of strings
def parse(raw_feed):
	return raw_feed.splitlines()[1:] # Every line except the first
