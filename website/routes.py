from main import app
from website.models import User

@app.route('/user/register/', methods=['POST'])
def signup():
    return User.signup()

