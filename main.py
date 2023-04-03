from flask import Flask, render_template, request,redirect
import pymysql
import pymysql.cursors
from flask_login import LoginManager, login_required, login_user, current_user, logout_user



login_manager = LoginManager()




app = Flask(__name__)
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'something_random'

@login_manager.user_loader
def user_loader(user_id):
     cursor = connection.cursor()

     cursor.execute("SELECT * from `User` WHERE `id` = " + user_id)

     result = cursor.fetchone()

     if result is None:
          return None
     
     return User(result['id'], result['username'], result['banned'])

@app.route("/home")
def index():

    return render_template(
        "home.html.jinja"
        

    )

@app.route('/post')
def post_feed():
      
      cursor = connection.cursor()
      
      cursor.execute("SELECT * FROM `Post` JOIN `User` ON `Post` . `user_id` = `User`.`id` ORDER BY `timestamp` DESC;")

      results = cursor.fetchall()

      return render_template(
        "post.html.jinja",

        posts=results
        

    )
@app.route('/sign-out')
def sign_out():
     logout_user()

     return redirect('/sigm-in')

@app.route('/sign-in', methods = ['POST', 'GET'])  
def sign_in():
      if current_user.is_authenticated:
           return redirect('/post')
      

      if request.method == 'POST':
           cursor = connection.cursor()

           cursor.execute(f"SELECT * FROM `User` WHERE `username` = '{request.form['username']}'")

           result = cursor.fetchone()

           if result is None:
                return render_template("sign.in.html.jinja")
           

           
           if request.form['password'] == result['password']:
                user = User(result['id'], result['username'], result['banned'])

                login_user(user)

                return redirect('/post')


           
           return request.form

      elif request.method == 'GET':
        return render_template("sign.in.html.jinja")

@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
       
      if current_user.is_authenticated:
        return redirect('/post')
       
      if request.method == 'POST':
        cursor = connection.cursor()

        photo = request.files['profile_image']

        file_name = photo.filename

        file_extension = file_name.split('.')[-1]

        print(file_extension)

        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
             
             photo.save('media/users/' + file_name)

        else:

            raise Exception('Invalid file type')

        cursor.execute("""
            INSERT INTO `User` (`username`, `password`, `email`, `birthday`, `bio`, `photo`, `display_name`)
            VALUES(%s,%s,%s,%s,%s,%s,%s)
        """, (request.form['username'], request.form['password'],request.form['email'],request.form['brithday'],request.form['bio'],file_name ,request.form['display_name']))

        
        return redirect('/post')
      elif request.method == 'GET':
      
        return render_template("sign.up.html.jinja")

class User:
     def __init__(self,id,username, banned):
          self.is_authenticated = True
          self.is_anonymous = False
          self.is_active = not banned

          self.username = username
          self.id = id
     def get_id(self):
        return str(self.id)
          


connection = pymysql.connect(
    host = "10.100.33.60",
    user = "wihezuo",
    password = "225380047",
    database= "wihezuo_social_media",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit = True


)





if __name__=='__main__':
        app.run(debug=True)