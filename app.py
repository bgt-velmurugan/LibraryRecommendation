from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    major = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)

class BookBorrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)

# Forms
class AddBookForm(FlaskForm):
    name = StringField('Book Name', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    department = SelectField('Department', choices=[('CS', 'Computer Science'), ('ENG', 'English'), ('MATH', 'Mathematics')], validators=[DataRequired()])
    major = SelectField('Major', choices=[('SE', 'Software Engineering'), ('AI', 'Artificial Intelligence'), ('DS', 'Data Science')], validators=[DataRequired()])
    year = SelectField('Year', choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Book')

class BookBorrowForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    department = SelectField('Department', choices=[('CS', 'Computer Science'), ('ENG', 'English'), ('MATH', 'Mathematics')], validators=[DataRequired()])
    year = SelectField('Year', choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')], coerce=int, validators=[DataRequired()])
    book = SelectField('Book', coerce=int, validators=[DataRequired()])
    borrow_date = DateField('Borrow Date', validators=[DataRequired()])
    submit = SubmitField('Borrow Book')

class BookSuggestionForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    department = SelectField('Department', choices=[('CS', 'Computer Science'), ('ENG', 'English'), ('MATH', 'Mathematics')], validators=[DataRequired()])
    year = SelectField('Year', choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Get Suggestions')

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        new_book = Book(
            name=form.name.data,
            author=form.author.data,
            serial_number=form.serial_number.data,
            department=form.department.data,
            major=form.major.data,
            year=form.year.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))
    return render_template('add_book.html', form=form)

@app.route('/book_borrow', methods=['GET', 'POST'])
def book_borrow():
    form = BookBorrowForm()
    form.book.choices = [(book.id, f"{book.name} by {book.author}") for book in Book.query.all()]
    if form.validate_on_submit():
        new_borrow = BookBorrow(
            student_name=form.student_name.data,
            student_id=form.student_id.data,
            department=form.department.data,
            year=form.year.data,
            book_id=form.book.data,
            borrow_date=form.borrow_date.data
        )
        db.session.add(new_borrow)
        db.session.commit()
        flash('Book borrowed successfully!', 'success')
        return redirect(url_for('book_borrow'))
    return render_template('book_borrow.html', form=form)

@app.route('/book_suggestions', methods=['GET', 'POST'])
def book_suggestions():
    form = BookSuggestionForm()
    suggestions = []
    if form.validate_on_submit():
        student_id = form.student_id.data
        department = form.department.data
        year = form.year.data

        # Get books borrowed by the student
        borrowed_books = BookBorrow.query.filter_by(student_id=student_id).all()
        borrowed_book_ids = [borrow.book_id for borrow in borrowed_books]

        # Get books in the same department and year, excluding already borrowed books
        suggested_books = Book.query.filter(
            Book.department == department,
            Book.year == year,
            ~Book.id.in_(borrowed_book_ids)
        ).all()

        suggestions = suggested_books

    return render_template('book_suggestions.html', form=form, suggestions=suggestions)

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

