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
import cgi
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, ** kw))

class Blog(db.Model): #inherits from db.Model class (imported above, line 5)
    title = db.StringProperty(required = True) #constraint which requires property to be included for entry into database
    text_body = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True) #automatically sets date/time according to submission

class MainPage(Handler):
    def render_front(self, title="", text_body="", error="", blog_posts=""):
        blog_posts = db.GqlQuery("SELECT * FROM Blog " #this line is "looking up" art in our database for including on front page following various user submissions
                            "ORDER BY created DESC "
                            "LIMIT 5 ")
        self.render("front.html", title=title, text_body=text_body, error=error, blog_posts=blog_posts)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_newpost(self, title="", text_body="", error=""):
        self.render("newpost.html", title=title, text_body=text_body, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        text_body = self.request.get("text_body")

        if title and text_body: #basic error handling
            a = Blog(title = title, text_body = text_body) #auto_now_add automatically stores created parameter, not necessary to add here
            a.put() #adds Blog to database

            p = str(a.key().id())
            self.redirect('/blog/'+p)
        else:
            error = "We need both a title and some text!"
            self.render_newpost(title, text_body, error)

class ViewPostHandler(Handler):
    def render_singlepost(self, title="", text_body="", error="", id=""):
        self.render("singlepost.html", title=title, text_body=text_body, error=error)

    def get(self, id):
        blog_post_id = Blog.get_by_id(int(id))
        title = blog_post_id.title
        text_body = blog_post_id.text_body
        if blog_post_id:
            self.render_singlepost(title, text_body, "")
        else:
            error = "That blog post does not exist."
            self.render_singlepost(error)



app = webapp2.WSGIApplication([(('/'), MainPage),
                               (('/newpost'), NewPost),
                               (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))],
                               debug=True)
