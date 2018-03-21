# This Python file uses the following encoding: utf-8
import urllib
from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def _strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


starts = {'monday': 'Måndag', 'tuesday': 'Tisdag', 'wednesday': 'Onsdag', 'thursday': 'Torsdag', 'friday': 'Fredag'}
ends = {'monday': 'Tisdag', 'tuesday': 'Onsdag', 'wednesday': 'Torsdag', 'thursday': 'Fredag', 'friday': 'Måndag'}


def _get_day_bramat(text, day):
    lines = text.splitlines()
    start_index = -1
    for i, line in enumerate(lines):
        if starts[day] in line:
            start_index = i
        if ends[day] in line or 'www.bramat.net' in line:
            end_index = i
            if start_index >= 0:
                break
    return '\n'.join(lines[start_index:end_index]).strip()


def _get_day_homemade(text, day):
    if day == 'friday':
        return text[text.index(starts[day]):].strip()
    else:
        return text[text.index(starts[day]):text.index(ends[day])].strip()

BRA_MAT=0
HOMEMADE=1
labels = {BRA_MAT: "Bra Mat", HOMEMADE: "Home Made"}


def _get_menu(day, link, readfunc):
    f = urllib.urlopen(link)
    myfile = f.read()
    try:
        menu_for_day = readfunc(_strip_tags(myfile), day)
    except:
        menu_for_day = "I failed reading the menu :flushed: you try: {}".format(link)
    return menu_for_day


def get_menu(day, restaurant=BRA_MAT):
    if restaurant == BRA_MAT:
        link = "http://www.bramat.net/lunch.aspx"
        readfunc = _get_day_bramat
    elif restaurant == HOMEMADE:
        link = "http://restauranghomemade.se/wp-content/themes/twentyten/week-menu.php"
        readfunc = _get_day_homemade
    else:
        return "I don't know that restaurant :flushed:"
    return "*{}*\n{}".format(labels[restaurant], _get_menu(day, link, readfunc))

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        print get_menu(sys.argv[1], int(sys.argv[2]))
    else:
        print get_menu("friday", HOMEMADE)
