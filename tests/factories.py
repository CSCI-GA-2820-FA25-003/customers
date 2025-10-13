"""
Test Factory to make fake objects for testing
"""

import uuid
import factory
from service.models import Customers


class CustomersFactory(factory.Factory):
    """Creates fake customers for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Customers

    id = factory.LazyFunction(uuid.uuid4)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    address = factory.Faker("street_address")
