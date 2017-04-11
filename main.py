import webapp2
import jinja2
import os

from google.appengine.ext import db
# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty (auto_now_add = True)


class MainHandler(Handler):
    def render_front(self, title ="", post = "", error = ""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, post=post, error=error, posts=posts)

    def get(self):
        self.render_front()

class NewPostHandler(Handler):
    def render_form(self, title ="", post = "", error = ""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("newpost.html", title=title, post=post, error=error, posts=posts)
        
    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title = title, post = post)
            p.put()

            self.redirect("/blog")
        else:
            error = "We need both a title and a post!"
            self.render_form(error = error, title=title, post=post)

app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/newpost', NewPostHandler)
], debug=True)
