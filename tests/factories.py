import factory

from data.database import db
from data.models import CaseData, Location


class LocationFactory(factory.alchemy.SQLAlchemyModelFactory):
    name = factory.Faker("city")

    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")

    api_id = factory.Sequence(lambda n: n)
    api_name = factory.SelfAttribute("name")

    minzdrav_name = factory.SelfAttribute("name")

    class Meta:
        model = Location
        sqlalchemy_session = db.session


class CaseDataFactory(factory.alchemy.SQLAlchemyModelFactory):
    location = factory.SubFactory(LocationFactory)
    date = factory.Faker("date_this_month")
    confirmed = factory.Faker("pyint", min_value=1, max_value=1000)
    recovered = factory.Faker("pyint", min_value=1, max_value=1000)
    fatal = factory.Faker("pyint", min_value=1, max_value=1000)

    class Meta:
        model = CaseData
        sqlalchemy_session = db.session
