from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from models import Task
from forms import TaskForm

app = Flask(__name__)

# Flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the app with extensions
db.init_app(app)

@app.route('/')
@app.route('/')
def index():
    # Sort by priority and then by due date (ascending order for both)
    tasks = Task.query.order_by(Task.priority.asc(), Task.due_date.asc()).all()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title = form.title.data,
            description = form.description.data,
            due_date = form.due_date.data,
            priority = form.priority.data,
        )
        
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_task.html', form = form)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created before starting the app
    app.run(debug=True)