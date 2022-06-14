import os
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
current_dir = os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(current_dir,'database.sqlite3')
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Course(db.Model):
     __tablename__ = 'course'
     course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
     course_code = db.Column(db.String, unique=True, nullable=False)
     course_name = db.Column(db.String, nullable=False)
     course_description = db.Column(db.String)
     #enrolls = db.relationship('Student', secondary='enrollments')
     
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

# retrive data     

@app.route('/', methods=['GET', 'POST'])  
def students():
       students = Student.query.all()
       return render_template('students.html', students=students)         

# update data
       
@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update(student_id):
      
      student = Student.query.get(student_id)
                               
      if request.method == 'POST': 
          
          student.first_name = request.form['f_name']
          student.last_name = request.form['l_name']        
          cid = request.form.getlist('courses')
          course = []
         
          for i in range(len(cid)):
            if cid[i]=='course_1':
               course.append('1')
             
            if cid[i]=='course_2':
               course.append('2')
            
            if cid[i]=='course_3':
               course.append('3')

            if cid[i]=='course_4':
               course.append('4')
              
          d={}             
          for i in range(len(course)):
            d[i] = db.session.query(Course).filter(Course.course_id==course[i]).one()
          for i in range(len(course)):
            student.enrolls.append(d[i])    
          db.session.commit()
                  
          return redirect(url_for('students'))
      return render_template('update.html', student=student) 
 
#delete data
      
@app.route('/student/<int:student_id>/delete', methods=['GET', 'POST'])
def delete(student_id):          
        student = Student.query.get(student_id) 
        
        db.session.delete(student)
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

# create data  
      
@app.route('/student/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
       return render_template('create.html')
    elif request.method == 'POST':
         roll_ = request.form['roll']
         first_ = request.form['f_name']
         last_ = request.form['l_name']
         cid = request.form.getlist('courses')
         course = []
         
         for i in range(len(cid)):
            if cid[i]=='course_1':
               course.append('1')
             
            if cid[i]=='course_2':
               course.append('2')
            
            if cid[i]=='course_3':
               course.append('3')

            if cid[i]=='course_4':
               course.append('4')
              
         d={}             
         for i in range(len(course)):
            d[i] = db.session.query(Course).filter(Course.course_id==course[i]).one()
            
# for check integrity constraint
            
         try:   		
             student = Student(roll_number = roll_, first_name=first_, last_name=last_)
             for i in range(len(course)):
                student.enrolls.append(d[i])
         
             db.session.add(student)
             db.session.commit()
         except IntegrityError:
            db.session.rollback()       
            return ('<p> Student already exists.Please use different Roll Number! </p> <a href="/student/create">Go Back </a>')
                                     
         return redirect(url_for('students'))
         
 
if __name__ == '__main__':
#run the flask app
  app.run() 
       
               
  
