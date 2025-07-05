import os
import re
import sys

from bs4 import BeautifulSoup

ZETTELKASTEN_URL = 'https://mosmu.se/'

if len(sys.argv) < 3:
    print("Usage: python3 tmp.py <source file> <target file>")
    sys.exit(1)
source_file = sys.argv[1]
target_file = sys.argv[2]
if not os.path.exists(source_file):
    print(f"Source file '{source_file}' does not exist")
    sys.exit(1)

with open(source_file, encoding='utf-8') as f:
    bs = BeautifulSoup(f.read(), features='html.parser')

bs.find('title').string = 'Random Thoughts – Soren Bjornstad'

entry_number_tags = bs.find_all('span', class_='PreProc')
for tag in entry_number_tags:
    this_id = tag.string.strip('@').strip('.')
    tag.attrs['id'] = this_id

refs = bs.find_all('span', class_='Statement')
for ref in refs:
    # get text without the html tag of each ref
    ref_text = ref.text
    if m := re.match(r'#(\d+)$', ref_text):
        ref_tag = bs.new_tag('a', href=f"#{m.group(1)}")
        ref_tag.string = ref_text
        ref.replace_with(ref_tag)
    elif m := re.match(r'§(.+)', ref_text):
        link_target = ZETTELKASTEN_URL + '#' + m.group(1)
        ref_tag = bs.new_tag('a', href=link_target)
        ref_tag.string = '§' + m.group(1)
        ref.replace_with(ref_tag)
    elif m := re.match(r'{BL (.*)}$', ref_text):
        links = []
        for bl_item in (i.strip() for i in m.group(1).split(',')):
            match bl_item[0]:
                case '§':
                    link_target = ZETTELKASTEN_URL + '#' + bl_item[1:]
                    link_tag = bs.new_tag('a', href=link_target)
                    link_tag.string = bl_item
                    links.append(link_tag)
                case '#':
                    link_tag = bs.new_tag('a', href=bl_item)
                    link_tag.string = bl_item
                    links.append(link_tag)
                case _:
                    if re.match(r'^[A-Z]B[0-9]+\.[0-9]+$', bl_item):
                        # RP reference
                        pass
                    else:
                        # Enable for debugging
                        #print("Unhandled: ", bl_item)
                        pass
                    links.append(bs.new_string(bl_item))

        ref.string = bs.new_string('{BL ')
        for idx, link in enumerate(links):
            ref.append(link)
            if idx == len(links) - 1:
                ref.append('}')
            else:
                ref.append(bs.new_string(', '))
    elif m := re.match(r'#[a-zA-Z]+$', ref_text):
        # hashtag; might be nice to offer links somehow in the future,
        # but out of scope for now
        pass
    elif m := re.match(r'{BL [A-Z]B[0-9]+\.[0-9]+', ref_text):
        # RP reference; no public link
        pass
    elif m := re.match(r'[Cc]f.', ref_text):
        # artifact of current syntax highlighter
        pass
    else:
        # Enable for debugging
        #print("Unhandled: ", ref_text)
        pass



with open(target_file, 'w', encoding='utf-8') as f:
    f.write(bs.prettify())
