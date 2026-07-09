import xml.etree.ElementTree as et

# Parser for RSS and Atom
# Takes a string and returns a list of strings
def parse(raw_feed):
	root = et.fromstring(raw_feed)
	ns = {}
	if root.tag == "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF": # RSS 1.0
		ns[""] = "http://purl.org/rss/1.0/"
		items = root.findall("item", namespaces = ns)
	elif root.tag == "rss": # RSS 2.0
		items = root.find("channel").findall("item")
	elif root.tag == "{http://www.w3.org/2005/Atom}feed": # Atom
		ns[""] = "http://www.w3.org/2005/Atom"
		items = root.findall("entry", namespaces = ns)
	else:
		raise RuntimeError(f"root tag of unknown type '{root.tag}'")
	entries = []
	for item in items:
		title = item.findtext("title", namespaces = ns) # RSS and Atom
		link = item.findtext("link", namespaces = ns) # RSS
		if link == "" or link is None:
			linktag = item.find("link", namespaces = ns)
			enclosuretag = item.find("enclosure", namespaces = ns)
			if linktag is not None:
				link = linktag.attrib["href"] # Atom
			elif enclosuretag is not None:
				link = enclosuretag.attrib["url"] # Podcasts without link tags, get link to audio/video file instead
		entries.append(" ".join(f"{title} {link}".splitlines()))
	return entries
