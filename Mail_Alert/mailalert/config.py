class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

    # theme for admin panel. can find other themes at http://bootswatch.com/3/
    FLASK_ADMIN_SWATCH = 'lumen'

    ALLOWED_EXTENSIONS = {'csv'}
    UPLOAD_FOLDER = '/home/taylor/Projects/emailAlert/Mail_Alert/mailalert/static/student_files'

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kutztownmail@gmail.com'
    MAIL_PASSWORD = 'KutztownMail10'
