from pathlib import Path
import sys
from fastapi import APIRouter,HTTPException,Query,Depends,Request
from fastapi.responses import Response
from pydantic import BaseModel,ConfigDict
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from trading_bots.common.manager import manager
from trading_bots.common.config import BotConfig,GlobalConfig
from ..origins import allowed_application_origin
def local_origin(request:Request):
    if request.method in ('POST','PUT','DELETE'):
        from ..config import get_settings
        if not allowed_application_origin(request,get_settings().cors_list):raise HTTPException(403,'Bot controls require an allowed application origin. Open Trading Desk using its local app address or configure CORS_ORIGINS for your frontend.')


router=APIRouter(prefix='/trading-bots',tags=['trading-bots'],dependencies=[Depends(local_origin)])


class Control(BaseModel):
    model_config=ConfigDict(extra='forbid')
    action:str
    confirmation:str=''


class Configuration(BaseModel):
    config:BotConfig
    confirmation:str=''


def call(fn,*args):
    try:return fn(*args)
    except (ValueError,KeyError) as e:raise HTTPException(400,str(e)) from e


@router.get('/dashboard')
def dashboard():return manager().dashboard()


@router.put('/global')
def global_config(cfg:GlobalConfig):return call(manager().global_config,cfg.model_dump())


@router.post('/global/start')
def global_start():return call(manager().start_all)


@router.post('/startup')
def startup():return call(manager().startup)


@router.get('/{bot_id}/export')
def export(bot_id:str,kind:str=Query('trades',pattern='^(trades|orders|signals|events)$')):
    s=call(manager().store,bot_id)
    return Response(s.export(kind),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="{bot_id}-{kind}.csv"'})


@router.get('/{bot_id}')
def detail(bot_id:str):return call(manager().detail,bot_id)


@router.post('/{bot_id}/control')
def control(bot_id:str,value:Control):return call(manager().control,bot_id,value.action,value.confirmation)


@router.put('/{bot_id}/config')
def config(bot_id:str,value:Configuration):return call(manager().configure,bot_id,value.config.model_dump(),value.confirmation)
