from data.database import db
from flask_migrate import Migrate

migrate = Migrate(db=db)
