from flask import Flask, render_template, request, redirect, url_for, jsonify
from extensions import db
from models import Task, Tag
from forms import TaskForm

app = Flask(__name__)

# Flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the app with extensions
db.init_app(app)

# App routes were made with AI assistance

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
    task = Task.query.get_or_404(task_id)

    # Remove the relationship between the task and its tags
    for tag in task.tags:
        task.tags.remove(tag)

    # Delete the task itself
    db.session.delete(task)

    # Optionally, delete tags that are no longer associated with any tasks
    orphaned_tags = Tag.query.filter(~Tag.tasks.any()).all()
    for tag in orphaned_tags:
        db.session.delete(tag)

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/filter', methods=['GET'])
def filter_by_tag():
    tag_name = request.args.get('tag_name')  # Get the tag_name from the query string
    if tag_name:
        # Filter tasks by the selected tag
        tasks = Task.query.join(Task.tags).filter(Tag.name == tag_name).all()
    else:
        # If no tag is selected, return all tasks
        tasks = Task.query.all()
    tags = Tag.query.order_by(Tag.name.asc()).all()

    # Create the form object (if needed)
    form = TaskForm()  # Replace TaskForm with the actual form class you're using

    return render_template('index.html', tasks=tasks, tags=tags, filter_tag=tag_name, form=form)

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm()

    if form.validate_on_submit():
        # Update task details
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data

        # Update tags
        tag_names = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
        task.tags.clear()  # Clear existing tags
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            task.tags.append(tag)

        db.session.commit()
        return redirect(url_for('index'))

    # If validation fails, re-render the index page with the form and tasks
    tasks = Task.query.order_by(Task.priority.asc(), Task.due_date.asc()).all()
    tags = Tag.query.all()
    return render_template('index.html', tasks=tasks, tags=tags, filter_tag=None, form=form)

@app.route('/update_status/<int:task_id>', methods=['POST'])
def update_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status')

    if new_status in ['To Do', 'In Progress', 'Completed']:
        task.status = new_status
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()  # Fetch all tags sorted alphabetically
    return jsonify([{'id': tag.id, 'name': tag.name} for tag in tags])  # Return tags as JSON

@app.route('/delete_tags', methods=['POST'])
def delete_tags():
    tag_ids = request.json.get('tag_ids', [])  # Get the list of tag IDs to delete
    for tag_id in tag_ids:
        tag = Tag.query.get(tag_id)
        if tag:
            db.session.delete(tag)  # Delete the tag
    db.session.commit()
    return jsonify({'message': 'Tags deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created before starting the app
    app.run(debug=True)