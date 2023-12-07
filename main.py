from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    requested_post = db.session.get(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/new_post', methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        # Check if the image URL is accessible
        img_url = form.img_url.data
        try:
            response = requests.head(img_url)
            if response.status_code != 200:
                print(f"Warning: The image URL seems to be invalid or inaccessible. Status Code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error accessing the image URL: {e}")

        # Proceed to create the new blog post
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=date.today().strftime("%B %d, %Y"),
            body=form.body.data,
            author=form.author.data,
            img_url=img_url
        )
        db.session.add(new_post)
        db.session.commit()
        print("New post added:", new_post)
        return redirect(url_for('get_all_posts'))
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")

    return render_template("make-post.html", form=form, form_action="add_new_post")

@app.route('/edit_post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    # Fetch the existing post to edit
    post_to_edit = db.session.get(BlogPost, post_id)

    form = CreatePostForm()

    if request.method == "POST" and form.validate_on_submit():
        # Update the existing blog post with new data from the form
        post_to_edit.title = form.title.data
        post_to_edit.subtitle = form.subtitle.data
        post_to_edit.body = form.body.data
        post_to_edit.author = form.author.data
        post_to_edit.img_url = form.img_url.data

        db.session.commit()
        print("Post edited:", post_to_edit)

        return redirect(url_for('show_post', post_id=post_id))

    elif request.method == "GET":
        # Populate the form with the existing post data
        form.title.data = post_to_edit.title
        form.subtitle.data = post_to_edit.subtitle
        form.body.data = post_to_edit.body
        form.author.data = post_to_edit.author
        form.img_url.data = post_to_edit.img_url

    return render_template("make-post.html", form=form, form_action="edit_post", post_id=post_id)

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    post_to_delete = db.session.get(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    print("Post deleted:", post_to_delete)
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
