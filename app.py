import os
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
current_dir = os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir,'week7_database.sqlite3')
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Course(db.Model):
     __tablename__ = 'course'
     course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
     course_code = db.Column(db.String, unique=True, nullable=False)
     course_name = db.Column(db.String, nullable=False)
     course_description = db.Column(db.String)
     enrolls = db.relationship('Student', secondary='enrollments')
     
class Student(db.Model):
     __tablename__ = 'student'
     student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
     roll_number = db.Column(db.String, unique=True, nullable=False)
     first_name = db.Column(db.String, nullable=False)
     last_name  = db.Column(db.String)
     enrolls = db.relationship('Course', secondary='enrollments')
        
       
class Enrollments(db.Model):
     __tablename__ = 'enrollments'
     enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
     estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
     ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# retrive student data     

@app.route('/', methods=['GET'])  
def students():
       students = Student.query.all()
        
       return render_template('students.html', students=students) 
       
# retrive course data

@app.route('/courses', methods=['GET'])  
def courses():
       courses = Course.query.all()
       return render_template('courses.html', courses=courses)               

# update student data
       
@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update(student_id):
      #if request.method == 'GET':
      student = Student.query.get(student_id)
      courses = Course.query.all() 
                             
      if request.method == 'POST': 
          
          student.first_name = request.form['f_name']
          student.last_name = request.form['l_name']
          #import pdb; pdb.set_trace()        
          cid = request.form['course']
          
          c_id = db.session.query(Course).filter(Course.course_id==cid).one()
          student.enrolls.append(c_id)  
          db.session.commit()
                  
          return redirect(url_for('students'))
       
      return render_template('update.html', student=student, courses=courses)
      
# update course data
       
@app.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
def course_update(course_id):

      course = Course.query.get(course_id)
                               
      if request.method == 'POST': 
          
          course.course_name = request.form['c_name']
          course.course_description = request.form['desc']
          #import pdb; pdb.set_trace()        
          #cid = request.form['course']
          
          #c_id = db.session.query(Course).filter(Course.course_name==cid).one()
          #student.enrolls.append(c_id)  
          db.session.commit()
                  
          return redirect(url_for('courses'))
      return render_template('course_update.html', course=course) 
      
 
#delete student data
      
@app.route('/student/<int:student_id>/delete', methods=['GET', 'POST'])
def delete(student_id):          
        student = Student.query.get(student_id) 
        
        db.session.delete(student)
        db.session.commit()
        
        return redirect(url_for('students'))
        

#delete course data
      
@app.route('/course/<int:course_id>/delete', methods=['GET', 'POST'])
def course_delete(course_id):          
        course = Course.query.get(course_id) 
        
        db.session.delete(course)
        db.session.commit()
        
        return redirect(url_for('students'))        
        
        
#withdraw course 

@app.route('/student/<int:student_id>/withdraw/<int:course_id>', methods=['GET', 'POST'])
def withdraw(student_id,course_id):          
        student = Student.query.get(student_id) 
        course = Course.query.get(course_id)
        # delete a course
        db.session.delete(course)
        
        db.session.commit()
        
        return redirect(url_for('students'))        
        
# retrive student details

@app.route('/student/<int:student_id>', methods=['GET', 'POST'])
def studentDetails(student_id):
      student = Student.query.get(student_id)
      enrolls = Enrollments.query.with_entities(Enrollments.ecourse_id).filter_by(estudent_id=student_id).all()
      
      cid = []
      for enroll in enrolls:
          cid.append(enroll[0])
      courses = []    
      for i in range(len(cid)):    
          course = Course.query.filter(Course.course_id==cid[i])    
          courses.append(course)
          
      #courses = Course.query.filter(Course.course_id==enroll.ecourse_id).all()   
      return render_template('student_details.html', student=student, courses=courses)  
      
# retrive course details

@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
def courseDetails(course_id):
      course = Course.query.get(course_id)
      enrolls = Enrollments.query.with_entities(Enrollments.estudent_id).filter_by(ecourse_id=course_id).all()
      
      sid = []
      for enroll in enrolls:
          sid.append(enroll[0])
      students = []    
      for i in range(len(sid)):    
          student = Student.query.filter(Student.student_id==sid[i])    
          students.append(student)
          
      #courses = Course.query.filter(Course.course_id==enroll.ecourse_id).all()   
      return render_template('course_details.html', students=students, course=course)             

# create student data  
      
@app.route('/student/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
       return render_template('create.html')
    elif request.method == 'POST':
         roll_ = request.form['roll']
         first_ = request.form['f_name']
         last_ = request.form['l_name']
         #import pdb; pdb.set_trace()
         try:	
            student = Student(roll_number = roll_, first_name=first_, last_name=last_)

            db.session.add(student)
            db.session.commit()
         except IntegrityError:
            db.session.rollback()       
            return ('<p> Student already exists.Please use different Roll Number! </p> <a href="/">Go Back </a>')
                                     
         return redirect(url_for('students'))
         
# create course data

@app.route('/course/create', methods=['GET', 'POST'])
def course_create():

    if request.method == 'GET':
    
       return render_template('course_create.html')
       
    elif request.method == 'POST':
    
         code_ = request.form['code']
         c_name_ = request.form['c_name']
         desc_ = request.form['desc']
         #import pdb; pdb.set_trace()
         try:	
            course = Course(course_code=code_, course_name=c_name_, course_description=desc_)

            db.session.add(course)
            db.session.commit()
         except IntegrityError:
            db.session.rollback()       
            return ('<p> Course already exists.Please create different Course! </p> <a href="/courses">Go Back </a>')
                                     
         return redirect(url_for('courses'))         
         
 
if __name__ == '__main__':
#run the flask app
  app.run() 
       
               
  
