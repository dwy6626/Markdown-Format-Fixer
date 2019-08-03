import os
import shutil
from sys import argv
import re


INPUTDIR = argv[1]
OUTPUTDIR = 'output'
SKIP_TITLE = True


item_or_title = re.compile(r'^[\-\#+]')
enumerates = re.compile(r'^\d+\.')
empty = re.compile(r'(\s+|<br>)')
empty_wo_br = re.compile(r'\s+')
null_line = re.compile(r'^[\*_]{1,2}$')


def clear_unpaired(symbol, this_line):
    r = re.escape(symbol)
    block2 = re.compile(r'(' + r + r'{2}.+?' + r + r'{2})')
    matches2 = block2.finditer(this_line)
    x = block2.sub('', this_line)
    block1 = re.compile(r'(' + r + r'.+?' + r + r')')
    matches1 = block1.finditer(x)
    x = block1.sub('', x)

    redundant = re.compile(r)
    if redundant.search(x):
        stashed2 = []
        for match in matches2:
            stashed2.append((match.start(), match.end() - match.start()))
        stashed2.sort()

        stashed1 = []

        for match in matches1:
            ls = filter(lambda x: x[0] < match.start(), stashed2)
            loc = sum(map(lambda x: x[1], ls))
            stashed1.append((match.start() + loc, match.end() - match.start()))
        stashed2.sort()

        stash = stashed1 + stashed2
        stash.sort()

        cuts = []
        for match in redundant.finditer(x):
            cp_stash = stash.copy()
            i, s = match.start(), match.end() - match.start()
            while cp_stash:
                stash_i, stash_l = cp_stash.pop(0)
                if stash_i <= i:
                    i += stash_l

            cuts.append((i, i+s))

        while cuts:
            i, f = cuts.pop(0)
            this_line = this_line[:i] + this_line[f:]
            cuts = [(ci - f + i, cf - f + i) for ci, cf in cuts]

    empty_content = re.compile(r + r'{2}[ 　\t]+' + r + r'{2}')
    this_line = empty_content.sub('', this_line)
    empty_content = re.compile(r + r'[ 　\t]+' + r)
    this_line = empty_content.sub('', this_line)

    # clear ****
    four_repeat = re.compile(r + r'{4}')
    this_line = four_repeat.sub('', this_line)

    return this_line


if os.path.isdir(OUTPUTDIR):
    print('output dir exist')
    ans = input("remove output dir to exceed [Y]/n")
    if not ans or ans.lower() == 'y':
        shutil.rmtree(OUTPUTDIR)
    else:
        exit(0)


# all files in *.md
file_list = []
for root, dirs, files in os.walk(INPUTDIR):
    file_list += [os.path.join(root, f) for f in files if f[-3:] == '.md']
    output_path = root.replace(INPUTDIR, OUTPUTDIR, 1)
    os.makedirs(output_path)

for fname in file_list:
    print('proccessing {}'.format(fname))

    input_file = open(fname, 'r')
    output_fname = fname.replace(INPUTDIR, OUTPUTDIR, 1)
    output_file = open(output_fname, 'w')

    if SKIP_TITLE:
        input_file.readline()

    while True:
        next_line = input_file.readline()
        if not empty.match(next_line):
            break

    while True:
        this_line = next_line
        next_line = input_file.readline()

        if not this_line:
            break

        """
        auto delete for redundant symbels * or _
        - on empty lines
        - empty content
        - not paired but at end of line
        """
        if null_line.match(this_line):
            continue

        this_line = clear_unpaired('*', this_line)
        this_line = clear_unpaired('_', this_line)

        """
        insert double space after lines when next line is simple text
        the possible exclusions:
        1. enumerates
        - items
        # title
        ### h3
        """

        exclude = item_or_title.findall(next_line) or enumerates.findall(
            next_line) or empty.match(this_line)

        if not exclude:
            this_line = this_line[:-1] + '  \n'

        """
        insert <br> for multiple linebreaks
        """
        if empty.match(this_line) and empty_wo_br.match(next_line):
            next_line = '<br>\n'

        output_file.write(this_line)
    print('write to {}'.format(output_fname))

    input_file.close()
    output_file.close()
