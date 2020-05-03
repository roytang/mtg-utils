from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from autocard import autocard

KEY_BASE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = 62

FORMATS_LOOKUP = {
  "S" : "Standard", "E" : "Extended", "B" : "Block Constructed", "L" : "Legacy", "V" : "Vintage",
  "O" : "Other/Casual"
}

FORMATS_MAP = [
  { "code" : "S", "desc" : "Standard"},
  { "code" : "E", "desc" : "Extended"},
  { "code" : "B", "desc" : "Block Constructed"},
  { "code" : "L", "desc" : "Legacy"},
  { "code" : "V", "desc" : "Vintage"},
  { "code" : "O", "desc" : "Other/Casual"},
]

def base62encode(number):
  if not isinstance(number, (int, long)):
    raise TypeError('number must be an integer')
  if number < 0:
    raise ValueError('number must be positive')

  alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghhijklmnopqrstuvwxyz'

  base62 = ''
  while number:
    number, i = divmod(number, 62)
    base62 = alphabet[i] + base62

  return base62 or alphabet[0]
  
def code_to_id(code):
  aid = 0L
  alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghhijklmnopqrstuvwxyz'
  for c in code:
    aid *= 62 
    aid += alphabet.index(c)
  return aid  

class Decklist(db.Model):
  code = db.StringProperty()
  title = db.StringProperty()
  raw_string = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  author_email = db.EmailProperty()
  author_nick = db.StringProperty()
  render = db.TextProperty()
  format = db.StringProperty()
  
  def url(self):
    return "/d/" + self.code
    
  def format_desc(self):
    return FORMATS_LOOKUP[self.format]
  
class BaseHandler(webapp.RequestHandler):

  def render(self, tmpl, context, auth=False):
  
    user = users.get_current_user()
    if user:
      url = users.create_logout_url(self.request.uri)
    else:
      url = users.create_login_url(self.request.uri)
      if auth:
        self.redirect(url)
        return
        
    object_list = db.GqlQuery("SELECT * FROM Decklist ORDER BY date DESC LIMIT 10")   

    context["object_list"] = object_list
    context["url"] = url
    context["user"] = user
    
    path = os.path.join(os.path.dirname(__file__), tmpl)
    self.response.out.write(template.render(path, context))
  
class MainPage(BaseHandler):
  def get(self):
    self.redirect("/deck/")
  
class UploadDecklist(webapp.RequestHandler):
  def post(self):
    decklist = Decklist()
    decklist.raw_string = self.request.get('decklist')
    decklist.title = self.request.get('title')
    decklist.format = self.request.get('format')
    decklist.render = autocard("<deck>" + decklist.raw_string + "</deck>")
    user = users.get_current_user()
    if user:
      decklist.author_email = user.email()
      decklist.author_nick = user.nickname()
    else:
      decklist.author_email = "none"
      decklist.author_nick = "Anonymous"
    
    decklist.put()
    decklist.code = base62encode(decklist.key().id())
    decklist.put()
    self.redirect(decklist.url())
    
class ViewDecklist(BaseHandler):
  def get(self, code):
    d = Decklist.get_by_id(code_to_id(code))
    if d is None:
      self.redirect("/deck/")
    else:
      deck_url = self.request.host_url + d.url()
      self.render("view.html", {"decklist" : d, "deck_url" : deck_url})

class DecksList(BaseHandler):
  def get(self):
    user = users.get_current_user()
    if user:  
      my_decks = db.GqlQuery("SELECT * FROM Decklist where author = USER('" + user.email() +"') ORDER BY date DESC LIMIT 1000")
    self.render("decks_list.html", {"my_decks" : my_decks}, True)

      
class DeckHome(BaseHandler):
  def get(self):
    self.render('decks_home.html', { "fmt_codes" : FORMATS_MAP })
    
application = webapp.WSGIApplication(
                   [
                   ('/', MainPage),
                   ('/deck/mine/', DecksList),
                   ('/deck/upload/', UploadDecklist),
                   ('/deck/', DeckHome),
                   ('/d/([a-zA-Z0-9]{1,6})?', ViewDecklist)
                   ],
                   debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()