from dashboard.layout import render_layout
from tests.factories import CaseDataFactory


def test_layout_no_data(use_db):
    CaseDataFactory.create_batch(10)

    render_layout()
