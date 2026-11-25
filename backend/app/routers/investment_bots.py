"""Paper investment controls have a separate namespace, state and kill switch."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict
from typing import Literal

from investment_bots.catalog import definition, SPECS
from investment_bots.service import manager
from .trading_bots import local_origin

router = APIRouter(prefix='/investment-bots', tags=['investment-bots'], dependencies=[Depends(local_origin)])


class Control(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: str


class PaperTest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    mode:Literal['fresh','keep']='fresh'
    policy:dict|None=None


def call(fn, *args):
    try:
        return fn(*args)
    except (ValueError, KeyError) as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get('/dashboard')
def dashboard():
    return manager().dashboard()


@router.post('/run')
def run(background: BackgroundTasks):
    background.add_task(manager().tick, force=True)
    return {'accepted': True, 'mode': 'paper', 'real_orders_submitted': 0}


@router.post('/paper-testing')
def paper_testing(value:PaperTest):
    return call(manager().configure_paper,value.policy,value.mode)


@router.post('/global/control')
def global_control(value: Control):
    return call(manager().global_control, value.action)


@router.get('/{bot_id}/specification')
def specification(bot_id: str):
    d = call(definition, bot_id)
    return Response((SPECS / (d['name'] + '.md')).read_text(encoding='utf-8'),
                    media_type='text/markdown', headers={'Content-Disposition': f'inline; filename="{d["name"]}.md"'})


@router.get('/{bot_id}/export')
def export(bot_id: str, kind: str = Query('orders', pattern='^(orders|executions|equity)$'),scope:Literal['active','reference']='active'):
    content = call(manager().export, bot_id, kind,scope=='reference')
    return Response(content, media_type='text/csv',
                    headers={'Content-Disposition': f'attachment; filename="{bot_id}-{kind}.csv"'})


@router.get('/{bot_id}')
def detail(bot_id: str):
    return call(manager().detail, bot_id)


@router.get('/{bot_id}/archive')
def archive(bot_id:str):
    return call(manager().detail,bot_id,True)


@router.post('/{bot_id}/control')
def control(bot_id: str, value: Control):
    return call(manager().control, bot_id, value.action)
