[brev](https://en.wiktionary.org/wiki/brev#Swedish) lets you follow (almost) anything on the web

## Requirements

- [Python 3](https://www.python.org/downloads/)

## Usage

You can change things in `config.json`, but this guide assumes default values.

Add feeds by creating text files under `feeds/` with the file ending `.brev`. On the first line you put the URL you want to follow, and on the second line you put the parser to use. (Entries in the feed will be added on the subsequent lines when the feed is updated.)

Parsers are Python files in the top directory with a `parse` function that takes the raw feed (string) and returns the entries in the feed (list of strings). They don't need anything other than that to work. There are two example parsers:

- `rss.py` - general parser for RSS and Atom feeds
- `tld.py` - specific parser for https://data.iana.org/TLD/tlds-alpha-by-domain.txt

If the second line does not match any parser, there is a default parser that will use it as a regex and the feed entries will be any line in the raw feed matching that regex.

Run `python3 brev.py` to check for updates. New entries will be added to `brev.txt`. You can also run `python3 brev.py feeds/path/to/feed.brev` to update just the specified feed without adding new entries to `brev.txt`, which is recommended when first adding a feed to avoid clutter.

### Examples

Say you create the file `feeds/comics/xkcd.brev`:
```
https://xkcd.com/rss.xml
rss
```

You then run `python3 brev.py feeds/comics/xkcd.brev` and the entries get added:
```
https://xkcd.com/rss.xml
rss
Toasting Marshmallows https://xkcd.com/3270/
Airport Meeting https://xkcd.com/3269/
Offside https://xkcd.com/3268/
Types of Tornado Alert https://xkcd.com/3267/
```

Later on you can run `python3 brev.py` and in `brev.txt` see something like:
```
comics/xkcd: The Princess and the Pea https://xkcd.com/3271/
```

You can add another feed at `feeds/tld.brev`:
```
https://data.iana.org/TLD/tlds-alpha-by-domain.txt
tld
```

And one at `feeds/lainzine.brev`:
```
https://lainzine.org/archive
href="/all-releases
```

Then update both by running `python3 brev.py feeds/tld.brev` and `python3 brev.py feeds/lainzine.brev`. Later on you can run `python3 brev.py` again and in `brev.txt` see something like:
```
comics/xkcd: The Princess and the Pea https://xkcd.com/3271/
lainzine: <div class="zine-image"><a href="/all-releases/track44.pdf"><img alt="track44 (pdf)" src = "/img/track44-thumb.jpg"></a></div>
tld: MERCK
```

Note that the Lainzine feed uses a regex instead of an existing parser, and as such the resulting entries are quite busy lines of HTML. This can of course be improved with a custom parser, but using a regex is a quick and simple solution that you may be fine with.
