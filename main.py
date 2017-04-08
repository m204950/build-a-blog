#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Index(Handler):
    def get(self):
        self.write('<a href="/blog">blog</a>')

class BlogPage(Handler):
    def render_blog(self, title="", post="", error=""):
        posts = db.GqlQuery("SELECT * FROM Blog " +
                            "ORDER BY created DESC " +
                            "LIMIT 5")

        self.render("blog.html", pagetitle = "Latest Blog Entries", title=title, post=post, error=error, posts=posts)

    def get(self):
        self.render_blog()

class NewPost(Handler):
    def render_post(self, title="", post="", error=""):
        self.render("post.html", pagetitle = "New Post", title=title, post=post, error=error)

    def get(self):
        self.render_post()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")
        if title and post:
            b = Blog(title = title, post = post)
            b.put()

            self.redirect("/blog/" + str(b.key().id()))
        else:
            error = "we need both a title and a blog entry"
            self.render_post(title, post, error)

class ViewPostHandler(Handler):
    def render_post(self, id, title="", post="", error=""):
        post = Blog.get_by_id(int(id))
        if post:
            self.render("single_post.html", pagetitle = "Single Post", title=title, post=post, error=error)
        else:
            error = "Nothing found for ID: " + str(id)
            self.render("single_post.html", pagetitle = "Single Post", title=title, post=post, error=error)

    def get(self, id):
        self.render_post(id)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', BlogPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
