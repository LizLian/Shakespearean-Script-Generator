from bs4 import BeautifulSoup
import re

bracketed_dirs = re.compile("\[(.*?)\]")

#convert all consecutive whitespaces to single space
def fix_spaces(text):
    return ' '.join(text.split())

def strip_brackets(text):
    return text.lstrip("[").rstrip("]")

def fix_dir(text):
    return strip_brackets(fix_spaces(text))

#isolate tagged character
def tag_to_char(tag):
    character = fix_spaces(tag.get_text().strip())
    if "," in character:
        return character[:character.index(",")]
    return character

#given act tag, get attr name and name of act
def separate_act_tags(tag):
    return (tag.get('href')[1:], tag.get_text())

class Line:
    """
    Contains information for one line of dialogue in a play, in particular:
    -act in which line occurs (self.act)
    -speaker of line (self.speaker)
    -stage directions associated with line (self.stage_direction)
    -spoken dialogue (self.line)
    >>> line = Line(actname, soup, chartag, stagetag, characters)
    """

    def __init__(self, actname, soup, chartag, stagetag, characters):
        self._chartag = chartag
        self._stagetag = stagetag
        self.act = actname
        self._speaker_tagged = False
        self.speaker = self.get_speaker(soup, characters)
        self.stage_direction = self.get_stage_direction(soup)
        if not (self.speaker or self.stage_direction):
            self.stage_direction = self.get_line(soup)
            self.line = None
        else:
            self.line = self.get_line(soup)

    #given line, isolate speaker
    def get_speaker(self, soup, characters):
        text = soup.get_text().upper().strip()
        speaker = soup.find(attrs={"class": self._chartag})
        if speaker:
            #character tagged
            if text.startswith("["):
                #just a stage direction; no speaking
                return None
            self._speaker_tagged = True
            return tag_to_char(speaker)
        else:
            #character untagged but designated at start of line
            for char in characters:
                if text.startswith(char.upper()):
                    return char
        #no character specified

    #given line, isolate stage directions
    def get_stage_direction(self, soup):
        stage_dirs = soup.find_all(attrs={"class": self._stagetag})
        stage_dirs += soup.find_all(attrs={"class": "right"})
        if stage_dirs:
            return list(map(lambda stage: fix_dir(stage.get_text()), stage_dirs))
        else:
            return list(map(fix_dir, bracketed_dirs.findall(soup.get_text())))

    #given line, isolate actual spoken dialogue
    #PERMANENTLY REMOVES EXCESS TAGS FROM LINE
    def get_line(self, soup):
        #remove html tags, specifically speaker and stage description
        while soup.find("span"):
            soup.span.decompose()
        #removed speaker separately if untagged
        line = bracketed_dirs.subn("", fix_spaces(soup.get_text()))[0]
        if self.speaker and not self._speaker_tagged:
            line = line[len(self.speaker):]
        #clean resulting line and return
        return line.lstrip(".").strip()

class Play:
    """
    Contains information for play, in particular:
    -list of acts; both the tag used in html,
     and the name printed in the script (self.acts)
    -cast of characters in play (self.chars)
    -list of lines (see Line class) (self.lines)
    >>> play = Play(filename, chartag, stagetag)
    """

    def __init__(self, filename, chartag, stagetag):
        self._chartag = chartag
        self._stagetag = stagetag
        with open(filename) as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        self.acts = self.get_acts(soup)
        self.chars = self.get_characters(soup)
        self.lines = []
        for act in self.acts:
            act_attr_name = act[0]
            act_start = soup.find(attrs={"name": act_attr_name})
            #find all lines in given act
            line = act_start.find_parent().find_next_sibling("p")
            while line is not None and self.in_act(line):
                self.lines.append(Line(act_attr_name, line, chartag, stagetag, self.chars))
                line = line.find_next_sibling("p")
        self.chars.add(None)


    def in_act(self, line):
        return not line.find("a", attrs={"name": True})

    #get all act tags
    def get_acts(self, soup):
        return list(map(separate_act_tags, soup.find_all("a", attrs={"href": True})))

    #get list of characters
    def get_characters(self, soup):
        tagged_chars = soup.find_all(attrs={"class": self._chartag})
        return set(map(tag_to_char, tagged_chars))
