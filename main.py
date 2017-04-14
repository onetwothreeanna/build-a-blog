import webapp2
import jinja2
import os

from google.appengine.ext import db
# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def get_posts(limit, offset):
#Retrieves posts from database.  Limit and Offset are string substitutions that are handled in MainHandler
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT {0} OFFSET {1}".format(limit, offset))
    return posts


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
    """Renders blog home"""
    def render_front(self, limit, offset, title ="", post = "", error = "", page = ""):
        posts = get_posts(limit, offset)
        self.render("front.html", title=title, post=post, error=error, posts=posts, page = page)

    def set_offset(self, page):
        offset = 0
        for i in range(page-1):
            offset+= 5
        return offset


    def get(self):
        page = self.request.get('page')
        if not page or page == 1:
            self.render_front(5, 0)
        else:
            page = int(page)
            offset = self.set_offset(page)  #Pass page through set_offset function above
            self.render_front(5, offset)


class NewPostHandler(Handler):
    """Renders new post form and handles submission to permalinks"""
    def render_form(self, title ="", post = "", error = ""):
        self.render("newpost.html", title=title, post=post, error=error)

    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title = title, post = post)
            p.put()
            post_id = str(p.key().id())
            self.redirect("/blog/" + post_id)

        else:
            error = "We need both a title and a post!"
            self.render_form(error = error, title=title, post=post)


class ViewPostHandler(Handler):
    """Handles permalinks to view specific blogposts"""
    def get(self, id):
        viewpost = Post.get_by_id(int(id))

        if viewpost:
            self.render("viewpost.html", post=viewpost)
        # if we can't find the movie, reject.
        else:
            error = "This post was not found."
            self.response.write(error)


app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/newpost', NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
