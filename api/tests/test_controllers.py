from fastapi import status
import pytest

from ..controllers import order_details, orders, recipes, resources, sandwiches
from ..models import models, schemas


CASES = [
    {
        "controller": sandwiches,
        "model": models.Sandwich,
        "create_schema": schemas.SandwichCreate(sandwich_name="BLT", price=8.5),
        "update_schema": schemas.SandwichUpdate(price=9.0),
        "id_field": "sandwich_id",
        "assertions": {"sandwich_name": "BLT", "price": 8.5},
    },
    {
        "controller": resources,
        "model": models.Resource,
        "create_schema": schemas.ResourceCreate(item="Bread", amount=10),
        "update_schema": schemas.ResourceUpdate(amount=12),
        "id_field": "resource_id",
        "assertions": {"item": "Bread", "amount": 10},
    },
    {
        "controller": recipes,
        "model": models.Recipe,
        "create_schema": schemas.RecipeCreate(sandwich_id=1, resource_id=2, amount=3),
        "update_schema": schemas.RecipeUpdate(amount=4),
        "id_field": "recipe_id",
        "assertions": {"sandwich_id": 1, "resource_id": 2, "amount": 3},
    },
    {
        "controller": orders,
        "model": models.Order,
        "create_schema": schemas.OrderCreate(customer_name="Jane", description="Club sandwich"),
        "update_schema": schemas.OrderUpdate(description="Updated order"),
        "id_field": "order_id",
        "assertions": {"customer_name": "Jane", "description": "Club sandwich"},
    },
    {
        "controller": order_details,
        "model": models.OrderDetail,
        "create_schema": schemas.OrderDetailCreate(order_id=1, sandwich_id=2, amount=1),
        "update_schema": schemas.OrderDetailUpdate(amount=2),
        "id_field": "order_detail_id",
        "assertions": {"order_id": 1, "sandwich_id": 2, "amount": 1},
    },
]


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.mark.parametrize("case", CASES, ids=[case["model"].__name__ for case in CASES])
def test_create_records(case, db_session):
    created_record = case["controller"].create(db_session, case["create_schema"])

    assert isinstance(created_record, case["model"])
    for field, value in case["assertions"].items():
        assert getattr(created_record, field) == value

    db_session.add.assert_called_once_with(created_record)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_record)


@pytest.mark.parametrize("case", CASES, ids=[case["model"].__name__ for case in CASES])
def test_read_all_records(case, db_session):
    expected = [object()]
    db_session.query.return_value.all.return_value = expected

    result = case["controller"].read_all(db_session)

    assert result == expected
    db_session.query.assert_called_once_with(case["model"])


@pytest.mark.parametrize("case", CASES, ids=[case["model"].__name__ for case in CASES])
def test_read_one_record(case, db_session):
    query = db_session.query.return_value.filter.return_value
    expected = object()
    query.first.return_value = expected

    result = case["controller"].read_one(db_session, 7)

    assert result == expected
    db_session.query.assert_called_once_with(case["model"])
    query.first.assert_called_once()


@pytest.mark.parametrize("case", CASES, ids=[case["model"].__name__ for case in CASES])
def test_update_record(case, db_session):
    query = db_session.query.return_value.filter.return_value
    expected = object()
    query.first.return_value = expected

    result = case["controller"].update(db_session, 7, case["update_schema"])

    assert result == expected
    query.update.assert_called_once_with(case["update_schema"].model_dump(exclude_unset=True), synchronize_session=False)
    db_session.commit.assert_called_once()
    query.first.assert_called_once()


@pytest.mark.parametrize("case", CASES, ids=[case["model"].__name__ for case in CASES])
def test_delete_record(case, db_session):
    response = case["controller"].delete(db_session, 7)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    db_session.query.return_value.filter.return_value.delete.assert_called_once_with(synchronize_session=False)
    db_session.commit.assert_called_once()