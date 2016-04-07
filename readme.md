# prettyjson

A python script that reads JSON like data from *standard input*, attempts to format it in a nice human readable way and output it into *standard output*.

prettyjson does NOT require correctly formatted JSON, whatever it gets it will try to format it.

# Examples

## Example 1

Input:

```
{'name':'jake','social':{'github':"jake314159",'twitter': "@jake314159"}, 'my fav numbers': [π, 'e', 3]}
```

Output:
```
{
    'name': 'jake',
    'social': {
        'github': "jake314159",
        'twitter': "@jake314159"
    },
    'my fav numbers': [
        π,
        'e',
        3
    ]
}
```

## Example 2

This example includes a collection of things that are invalid JSON and would break a simple prettyjson implementation. This is using the '--advanced-parser' command line argument to improve handling of the python datetime object.

```
{	'no value':,
	:'no key',
	u'python unicode string?'  : True,
	'python date': datetime(2016, 3, 10, 18, 57, 11, 470965),
	'different quote types': "  'YES!'  ",
	'missing quotes':That Will Also Be Fine!,
	'extra commas and colons?'::,,
	'emoji':"👍😃😪🐼💩"
]}
```

The output:

```
{
    'no value': ,
    : 'no key',
    u'python unicode string?': True,
    'python date': datetime(2016, 3, 10, 18, 57, 11, 470965),
    'different quote types': "  'YES!'  ",
    'missing quotes': ThatWillAlsoBeFine!,
    'extra commas and colons?': : ,
    ,
    'emoji': "👍😃😪🐼💩"
]
}
```

# Usage

The output from 'prettyjson --help'

```
Usage:
  $ [some_other_command] | prettyjson [args]
  $ prettyjson [args] < [json_file]
Examples:
  $ curl 'example.com/api/test.json' | prettyjson --step-size 2
  $ prettyjson < data.json
  $ cat data.json | prettyjson > pretty_data.json


Options:
  -h, --help                    Display help text (and exit).
  -s [INT], --step-size [INT]   Set the tab size used when formatting the JSON. Default 4
  --strict                      Ensure input is correct JSON and error if not.
                                Opposite of --relax.
  --relax                       Attempt to format as JSON without verifying it's correctness
                                Opposite of --strict and selected by default.
  -p, --space                   Use spaces for alignment, -s is tab size so use -p
                                  Default: True
  -t, --tab                     Use tabs rather than spaces for alignment, --step-size will be
                                ignored if set. Default: False
  --multi-line-strings          Don't break out of a string when a new line is encountered
                                relax mode only and off by default. You probably don't need this.
  -a, --advanced-parse          Do a more complex advanced parsing of the input to improve formatting
                                for language specific constructs.
                                Opposite of --basic-parse off by default.
  -b, --basic-parse             Run a simpler parser that does not include some extra language specific
                                formatting.
                                Opposite of --advanced-parse, selected by default.
```

# Licence

The MIT License (MIT)

Copyright (c) 2016 Jake Causon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
