# tests/test_models_extra_branches.py
from service.models import Customers, db
from wsgi import app

def _reset():
    db.session.query(Customers).delete()
    db.session.commit()

def test_find_by_name_three_tokens_exact():
    with app.app_context():
        _reset()
        a = Customers(first_name="Alice", last_name="Jones", address="1 Ave")
        b = Customers(first_name="Alice", last_name="Smith", address="2 Ave")
        c = Customers(first_name="Bob",   last_name="Jones", address="3 Ave")
        for x in (a, b, c):
            x.create()

        rows = Customers.find_by_name("Alice Middle Jones", fuzzy=False)
        names = {(r.first_name, r.last_name) for r in rows}
        assert names == {("Alice", "Jones")}  # exact first+last ignoring middle

def test_find_by_name_empty_returns_none():
    with app.app_context():
        _reset()
        rows = Customers.find_by_name("")
        assert rows.count() == 0
