from ..controllers import orders
import pytest
from ..models import schemas


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_order(db_session):
    order_object = schemas.OrderCreate(
        customer_name="John Doe",
        description="Test order",
    )

    created_order = orders.create(db_session, order_object)

    assert created_order is not None
    assert created_order.customer_name == "John Doe"
    assert created_order.description == "Test order"
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_order)
