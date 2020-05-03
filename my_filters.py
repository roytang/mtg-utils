from google.appengine.ext import webapp

register = webapp.template.create_template_register()

@register.filter
def jquote(jscript):
  return jscript.replace('\\', '\\\\').replace("'", "\\'").replace('\r', '\\n').replace('\n', '\\n')  