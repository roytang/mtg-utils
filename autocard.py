# BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
from BeautifulSoup import BeautifulSoup     
from google.appengine.ext.webapp import template

def render_to_string(path, context):
   return template.render(path, context)
   
import re    
def autocard(content):
    """Render a decklist."""
    soup = BeautifulSoup(content)
    card_blocks = soup.findAll('card')
    for block in card_blocks:
        card_name = block.string
        if card_name and card_name != "":
            block.replaceWith(autocard_link(card_name))
    deck_blocks = soup.findAll('deck')
    for block in deck_blocks:
        try:
            MAX_COLS = int(block["cols"])
        except KeyError:
            MAX_COLS = 3
        if block.string:
            list_for_parsing = block.string
        else:
            child_tags = block.findAll()
            list_for_parsing = ""
            for tag in child_tags:
                if tag.string:
                    list_for_parsing = list_for_parsing + "\n" + tag.string + "\n"
        lines = list_for_parsing.split("\n")
        new_deck = ""
        groups = []
        new_group = { 'title' : '', 'cards' : [] }
        for line in lines:
            header = True
            line = line.strip()
            # Apprentice format has "SB:" for sideboard cards
            if line.startswith("SB:"):
                line = line[3:].strip()
            if line == "":
                continue
            if re.match('(\d+)', line):
                count = re.sub(
                             '(\d+)(\s*)([^\<]*)', 
                             '\g<1>', 
                             line)
                name = re.sub(
                             '(\d+)(\s*)([^\<]*)', 
                             '\g<3>', 
                             line)
                # remove stuff inside hard brackets
                p = re.compile('\[[A-Za-z0-9]*\]')
                name = p.sub('', name)
                # remove stuff inside paren
                p = re.compile('\([A-Za-z0-9]*\)')
                name = p.sub('', name)
                new_group['cards'].append({ 'count' : int(count), 'name' : name })
                header = False
            if header:
                # end the previous group
                if len(new_group['cards']) > 0:
                    groups.append(new_group)
                #new_deck = new_deck + "<ul class='decklist_group'>%s</ul>" % new_group
                title = line
                if title.startswith("//"):
                    title = title[2:].strip()
                new_group = { 'title' : title, 'cards' : [] }
            #new_group = new_group + "<li%s>%s</li>\n" % (cls, line)
        # end the previous group
        if len(new_group['cards']) > 0:
            groups.append(new_group)
        groups_per_col = len(groups)/MAX_COLS
        if groups_per_col < 1:
            groups_per_col = 1
        cols = []
        col = []
        for group in groups:
            if len(col) >= groups_per_col and len(cols) < MAX_COLS - 1:
                cols.append(col)
                col = []
            col.append(group)
        cols.append(col)
        block.replaceWith(render_to_string('autocard/deck.html', { 'cols' : cols }))
    
    #print str(soup)
    return str(soup)
    
def autocard_link(card_name):
    if card_name:
        card_name = card_name.strip()
        return render_to_string('autocard/card.html', { 'name' : card_name })
    return card_name