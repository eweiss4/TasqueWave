from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from models import Task, Tag
from forms import TaskForm

app = Flask(__name__)

# Flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the app with extensions
db.init_app(app)

@app.route('/')
def index():
    tasks = Task.query.order_by(Task.priority.asc(), Task.due_date.asc()).all()
    tags = Tag.query.all()
    form = TaskForm()  # Create an instance of the TaskForm
    return render_template('index.html', tasks=tasks, tags=tags, filter_tag=None, form=form)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        # Create the task
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
        )
        
        # Process tags
        tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            task.tags.append(tag)
        
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index')) 
    return render_template('add_task.html', form=form)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/filter/<string:tag_name>')
def filter_by_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    tasks = tag.tasks.order_by(Task.priority.asc(), Task.due_date.asc()).all() if tag else []
    tags = Tag.query.all()
    form = TaskForm()  # Create an instance of the TaskForm
    return render_template('index.html', tasks=tasks, tags=tags, filter_tag=tag_name, form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created before starting the app
    app.run(debug=True)