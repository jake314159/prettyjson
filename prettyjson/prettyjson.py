#!/usr/bin/env python

"""
prettyjson

Script that takes data from stdin and attempts to format
it as JSON. Will (probably) NOT fail if poorly formatted
so you can still get a look at what the data is even if
it is not correct JSON

For more information on how to use prettyjson run:
  $ prettyjson --help


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

"""

help_text = """
prettyjson

Attempts to format JSON strings inputted on standard input without
requiring it to be correctly formatted.

Author: Jake Causon (Github: @jake314159)

Usage:
  $ [some_other_command] | prettyjson [args]
  $ prettyjson [args] < [json_file]
  $ prettyjson [json_file]
  $ prettyjson -f [json_file]
Examples:
  $ curl 'example.com/api/test.json' | prettyjson --step-size 2
  $ prettyjson < data.json
  $ prettyjson data.json
  $ prettyjson -f data1.json data2.json
  $ cat data.json | prettyjson > pretty_data.json


Options:
  -h, --help                Display help text (and exit).
  -s INT, --step-size INT   Set the tab size used. Default 4
  --strict                  Ensure input is correct JSON and error if not.
                            Opposite of --relax.
  --relax                   Attempt to format without verifying the structure
                            Opposite of --strict and selected by default.
  -p, --space               Use spaces for alignment, -s is tab size so use -p
                            Default: True
  -t, --tab                 Use tabs rather than spaces for alignment,
                            --step-size will be ignored if set. Default False
  --multi-line-strings      Don't break out of a string when a new line is
                            encountered in relax mode only. Default False
  -b, --basic-parse         Run a simple parser that does not include language
                            specific formatting.
  -f, --file                Load the input from a file rather than stdin.
                            If more than one file is specified then all the
                            files will be concatinated before parsing
  --hard-error              Exit on error with no attempt to recover
  --soft-error              Attempt to recover from an error

"""

class pretty_json_builder:
    """
    Interface for the json builder that takes a series of characters & commands and builds the final formatted output string
    """
    def init_string_process(self, s):
        return s
    def append_to_output(self, c):
        pass
    def newline_to_output(self):
        pass
    def increase_step(self):
        pass
    def decrease_step(self):
        pass
    def to_string(self, step_size=4, multi_line_strings=False, advanced_parse=False, tab=False):
        return ''

class _pretty_json_builder_strict(pretty_json_builder):
    def __init__(self):
        self.s = ''
    def init_string_process(self, s):
        self.s = s
        return None  # We have everything we need so stop any more parsing
    def to_string(self, step_size=4, multi_line_strings=False, advanced_parse=False, tab=False):
        import json
        return json.dumps(json.loads(s), indent=step_size, separators=(',',': '))

class _pretty_json_builder_relaxed(pretty_json_builder):
    def __init__(self):
        self.stack = [['']]

    def _special_escape(self):
        # Returns a Bool indicating if we are in a special escape that should not have it's formatting changed
        return ('datetime' in self.stack[-1][-1] and ')' not in self.stack[-1][-1])

    def append_to_output(self, c):
        self.stack[-1][-1] += c

    def newline_to_output(self):
        if not self._special_escape():
            self.stack[-1].append('')

    def increase_step(self):
        if not self._special_escape():
            self.stack[-1].append([''])  # Add the new array to the correct part of the structure
            self.stack.append(self.stack[-1][-1])  # Add the new focus to the top of the stack

    def decrease_step(self):
        if not self._special_escape():
            if len(self.stack) > 1:
                self.stack.pop()
            self.newline_to_output()

    # Do any processing of the structure, eg. flattening lists with 1 element
    def _process(self, thing):
        change = 0  # The number of things this function call has changed

        if isinstance(thing, list):
            # We have a list so deal with each element in turn
            max_length = 0  # The max length of the elements in this list
            consider_compress = True
            for i in range(0, len(thing)):
                if isinstance(thing[i], list):
                    consider_compress = False  # Don't try to compress a list
                max_length = max(max_length, len(thing[i]))
                if isinstance(thing[i], list) and len(thing[i]) == 1 and len(thing) > i+1:
                    # We have a list with 1 element so colapse it
                    output1, c1 = self._process(thing[i][0])
                    output2, c2 = self._process(thing[i+1])
                    thing[i-1] = '%s%s%s' % (thing[i-1], output1, output2)
                    thing[i] = thing[i+1] = ''
                    change += 1 + c1 + c2
                else:
                    # Recursively parse this element of the list
                    output, c = self._process(thing[i])
                    change += c
                    thing[i] = output

            # Merge a few short string elements into the same line
            if consider_compress and max_length <= 5 and len(thing) <= 6 and len(thing) > 1:
                change += 1
                thing = [' '.join(thing)]

            # Remove any empty strings
            for i in range(len(thing)-1, 0, -1):
                if thing[i] == '':
                    thing.pop(i)

        return thing, change

    def to_string(self, step_size=4, multi_line_strings=False, advanced_parse=False, tab=False):
        step_char = ' '
        if tab:
            step_char = '\t'
            step_size = 1  # Only 1 tab per step

        # Process until no more changes are made
        changes = 1
        output = self.stack[0]
        runs = 100000  # Maximum number of process runs to allow
        while changes:
            if runs >= 0:
                output, changes = self._process(output)
                runs -= 1
            else:
                sys.stderr.write("warning: Unable to finish output formatting\n")
                break

        def _to_string(thing, depth=0):
            o = ''
            for t in thing:
                if isinstance(t, list):
                     o += _to_string(t, depth+1)
                elif t != '':
                    o += '%s%s\n' % (step_char*depth*step_size, t)
            return o

        return _to_string(output)

def prettify(s, step_size=4, multi_line_strings=False, tab=False, builder=None):
    if not builder:
        builder = _pretty_json_builder_relaxed()

    s = builder.init_string_process(s) or '' # Give the builder a chance to process the raw string

    # Parse over the string passing the appropriate commands to the builder class
    in_marks = False  # Are we in speech marks? What character will indicate we are leaving it?
    escape = False  # Is the next character escaped?
    for c in s:
        if escape:
            # This character is escaped so output it without looking at it
            escape = False
            builder.append_to_output(c)
        elif c in ['\\']:
            # Escape the next character
            escape = True
            builder.append_to_output(c)
        elif in_marks:
            # We are in speech marks
            if c == in_marks or (not multi_line_strings and c in ['\n', '\r']):
                # but we just got to the end of them
                in_marks = False
            builder.append_to_output(c)
        elif c in ['"', "'"]:
            in_marks = c  # Enter speech marks
            builder.append_to_output(c)
        elif c in ['{', '[', '(']:
            # Increase step and add new line
            builder.append_to_output(c)
            builder.increase_step()
        elif c in ['}', ']', ')']:
            # Decrease step and add new line
            builder.decrease_step()
            builder.append_to_output(c)
        elif c in [':']:
            # Follow with a space
            builder.append_to_output(c)
            builder.append_to_output(' ')
        elif c in [',']:
            # Follow with a new line
            builder.append_to_output(c)
            builder.newline_to_output()
        elif c in [' ', '\n', '\r', '\t']:
            pass  # Ignore this character
        else:
            # Character of no special interest, so just output it as it is
            builder.append_to_output(c)

    return builder.to_string(step_size=step_size, multi_line_strings=multi_line_strings, tab=tab)

# aliases for prettify
stringify = prettify
dumps = prettify

if __name__ == '__main__':
    ## Run as a terminal script ##
    import sys
    import re

    # Settings
    in_files = []
    hard_error = True
    step_size = 4
    strict = False
    multi_line_strings = False
    tab = False

    # Parse command line arguments
    key = ''
    sys.argv.pop(0)
    while len(sys.argv) > 0:
        try:
            key = sys.argv.pop(0)
            if key == 'prettyjson':
                pass
            elif key in ['-h', '--help']:
                print help_text
                sys.exit(0)
            elif key in ['-s', '--step-size']:
                try:
                    step_size = int(sys.argv.pop(0))
                except:
                    pass
            elif key in ['--strict']:
                strict = True
            elif key in ['--relax', '--relaxed']:
                strict = False
            elif key in ['-t','--tab', '--tabs']:
                tab = True
            elif key in ['-p', '--space', '--spaces']:
                tab = False
            elif key in ['--multi-line-strings', '--multi-line-string']:
                multi_line_strings = True
            elif key in ['-b', '--basic', '--basic-parse', '--basic-parser']:
                advanced_parse = False
            elif key in ['--soft-error']:
                hard_error = False
            elif key in ['--hard-error']:
                hard_error = True
            elif key in ['-f', '--file', '--in-file', '--input', '--input-file', '--in']:
                in_files.append(sys.argv.pop(0))
            elif not key.startswith('-'):
                # Is not a command argument so is most likely a file path
                in_files.append(key)
        except Exception:
            print "Error reading command line argument '%s'" % key
            if hard_error:
                sys.exit(1)

    builder = None
    if strict:
        builder = _pretty_json_builder_strict()

    s = ''
    if len(in_files) == 0:
        # Load stdin into a string
        for line in sys.stdin.read():
            s += line
    else:
        # Load the specified files into a string
        for f in in_files:
            try:
                with open(f, "r") as file_handle:
                    s += file_handle.read()
            except IOError:
                print "Error: Unable to read the file '%s'" % f
                if hard_error:
                    sys.exit(2)

    # Print the result to stdout
    print ""  # New line
    print prettify(s, step_size=step_size, multi_line_strings=multi_line_strings, tab=tab, builder=builder)
    