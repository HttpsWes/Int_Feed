from flask import Flask, render_template, request,redirect, send_from_directory,abort, g
import pymysql
import pymysql.cursors
from flask_login import LoginManager, login_required, login_user, current_user, logout_user



login_manager = LoginManager()




app = Flask(__name__)
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'something_random'

@login_manager.user_loader
def user_loader(user_id):
     cursor = get_db().cursor()

     cursor.execute("SELECT * from `User` WHERE `id` =%s ", (user_id)),
    
     result = cursor.fetchone()

     if result is None:
          return None
     
     return User(result['id'], result['username'], result['banned'])

@app.get('/media/<path:path>')
def send_media(path):
    return send_from_directory('media',path)

@app.route("/")
def index():

    return render_template(
        "home.html.jinja"
        

    )

@app.route('/feed')
@login_required
def post_feed():
      
      cursor = get_db().cursor()
      
      cursor.execute("SELECT * FROM `Post` JOIN `User` ON `Post` . `user_id` = `User`.`id` ORDER BY `timestamp` DESC;")
      

      results = cursor.fetchall()

      return render_template(
        "post.html.jinja",

        posts=results
        

    )

@app.route('/post', methods = ['POST'])
@login_required
def create_post():

    cursor = get_db().cursor()

    photo = request.files['image']

    file_name = photo.filename

    file_extension = file_name.split('.')[-1]

    print(file_extension)

    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
             
        photo.save('media/post/' + file_name)

    else:

        raise Exception('Invalid file type')
     

    user_id = current_user.id

    cursor.execute("INSERT INTO `Post` (`post_image`,`caption`,`user_id`) VALUES(%s,%s,%s)", (file_name, request.form['post'], user_id,))

    return redirect('/feed')

@app.route('/sign-out')
def sign_out():
     logout_user()

     return redirect('/sign-in')

@app.route('/sign-in', methods = ['POST', 'GET'])  
def sign_in():
      if current_user.is_authenticated:
           return redirect('/feed')
      

      if request.method == 'POST':
           cursor = get_db().cursor()


           cursor.execute("SELECT * FROM `User` WHERE `username` = %s", (request.form['username']))
           result = cursor.fetchone()

           if result is None:
                return render_template("sign.in.html.jinja")
           

           
           if request.form['password'] == result['password']:
                user = User(result['id'], result['username'], result['banned'])

                login_user(user)

                return redirect('/feed')


           
           return request.form

      elif request.method == 'GET':
        return render_template("sign.in.html.jinja")

@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
       
      if current_user.is_authenticated:
        return redirect('/feed')
       
      if request.method == 'POST':
        cursor = get_db().cursor()

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

        
        return redirect('/feed')
      elif request.method == 'GET':
      
        return render_template("sign.up.html.jinja")
      

@app.route('/profile/<username>')
def user_profile(username):

    cursor = get_db().cursor()

    cursor.execute("SELECT * FROM `User` WHERE `username` = %s", (username))

    result = cursor.fetchone()

    if result is None:
        abort(404)

    cursor.close()

    cursor = get_db().cursor()

    cursor.execute("SELECT * from `Post` WHERE `user_id` = %s", result['id'])    

    post_result = cursor.fetchall() 
            
    return render_template("user.profile.html.jinja", user=result,posts=post_result)      
      
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html.jinja'),404     



class User:
     def __init__(self,id,username, banned):
          self.is_authenticated = True
          self.is_anonymous = False
          self.is_active = not banned

          self.username = username
          self.id = id
     def get_id(self):
        return str(self.id)
          

def connect_db():
    return pymysql.connect(
        host="10.100.33.60",
        user="wihezuo",
        password="225380047",
        database="wihezuo_social_media",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def get_db():
    '''Opens a new database connection per request.'''        
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db    

@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close() 


if __name__=='__main__':
        app.run(debug=True)