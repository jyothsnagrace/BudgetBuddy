import json

from app.main import ingest, plan, creative
from app.schemas import UserFinanceInput, PlanRequest


def test_ingest_and_plan():
    with open('data/sample_user.json') as f:
        payload = json.load(f)

    fin = UserFinanceInput(**payload)
    r = ingest(fin)
    assert r.get('status') == 'ok'

    plan_req = PlanRequest(user_id=payload["user_id"], months=3)
    r2 = plan(plan_req)
    assert r2["user_id"] == payload["user_id"]
    assert "plan" in r2
    assert len(r2["plan"]) > 0


def test_creative():
    with open('data/sample_user.json') as f:
        payload = json.load(f)
    # ensure data exists
    fin = UserFinanceInput(**payload)
    ingest(fin)
    from app.schemas import CreativeRequest
    creq = CreativeRequest(user_id=payload['user_id'], tone='friendly', format='letter')
    cres = creative(creq)
    assert cres.get('user_id') == payload['user_id']
    assert 'creative' in cres
    assert len(cres['creative']) > 0
