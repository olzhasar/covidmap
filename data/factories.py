import factory

from data.database import db
from data.models import CaseData


class CaseDataFactory(factory.alchemy.SQLAlchemyModelFactory):
    location_id = factory.Faker("pyint", min_value=1, max_value=10)
    date = factory.Faker("date_this_month")
    confirmed = factory.Faker("pyint", min_value=1, max_value=1000)
    recovered = factory.Faker("pyint", min_value=1, max_value=1000)
    fatal = factory.Faker("pyint", min_value=1, max_value=1000)

    class Meta:
        model = CaseData
        sqlalchemy_session = db.session
