from enum import Enum, IntEnum
from pydantic import BaseModel, ValidationError

class delayEnum(IntEnum):
    d0 = 0
    d1 = 1

class pasteurizationEnum(str, Enum):
    on = 'ON'
    off = 'OFF'

class nanHandlingEnum(str, Enum):
    on = 'ON'
    off = 'OFF'

class regionEnum(str, Enum):
    usa = 'USA'
    chn = 'CHN'

class neutralizationEnum(str, Enum):
    subindustry = 'SUBINDUSTRY'
    industry = 'INDUSTRY'
    sector = 'SECTOR'
    market = 'MARKET'
    none = 'NONE'

class universeEnum(str, Enum):
    top3000 = 'TOP3000'
    top2000 = 'TOP2000'
    top1000 = 'TOP1000'
    top500 = 'TOP500'
    top200 = 'TOP200'

class Alpha(BaseModel):
    code: str
    delay: delayEnum = delayEnum.d1
    universe: universeEnum = universeEnum.top3000
    truncation: float = 0.1
    region: regionEnum = regionEnum.usa
    decay: int = 6
    neutralization: neutralizationEnum = neutralizationEnum.subindustry
    pasteurization: pasteurizationEnum = pasteurizationEnum.on
    nanHandling: nanHandlingEnum = nanHandlingEnum.off

# -------- DB STUFF

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class AlphaResult(Base):
    __tablename__ = 'alpha_results'

    id = Column(Integer, primary_key=True)
    alpha_id = Column(String, index=True)
    alpha_type = Column(String)
    author = Column(String)
    instrument_type = Column(String)
    region = Column(String)
    universe = Column(String)
    delay = Column(Integer)
    decay = Column(Integer)
    neutralization = Column(String)
    truncation = Column(Float)
    pasteurization = Column(String)
    unit_handling = Column(String)
    nan_handling = Column(String)
    language = Column(String)
    visualization = Column(Boolean)
    regular_code = Column(String)
    date_created = Column(String)
    date_submitted = Column(String)
    date_modified = Column(String)
    name = Column(String)
    grade = Column(String)
    stage = Column(String)
    status = Column(String)
    is_pnl = Column(Float)
    is_book_size = Column(Float)
    is_long_count = Column(Integer)
    is_short_count = Column(Integer)
    is_turnover = Column(Float)
    is_returns = Column(Float)
    is_drawdown = Column(Float)
    is_margin = Column(Float)
    is_fitness = Column(Float)
    is_sharpe = Column(Float)
    is_start_date = Column(String)
    is_check_low_sharpe_result = Column(String)
    is_check_low_sharpe_limit = Column(Float)
    is_check_low_sharpe_value = Column(Float)
    is_check_low_fitness_result = Column(String)
    is_check_low_fitness_limit = Column(Float)
    is_check_low_fitness_value = Column(Float)
    is_check_low_turnover_result = Column(String)
    is_check_low_turnover_limit = Column(Float)
    is_check_low_turnover_value = Column(Float)
    is_check_high_turnover_result = Column(String)
    is_check_high_turnover_limit = Column(Float)
    is_check_high_turnover_value = Column(Float)
    is_check_concentrated_weight_result = Column(String)
    is_check_low_sub_universe_sharpe_result = Column(String)
    is_check_low_sub_universe_sharpe_limit = Column(Float)
    is_check_low_sub_universe_sharpe_value = Column(Float)
    is_check_low_returns_result = Column(String)
    is_check_low_returns_limit = Column(Float)
    is_check_low_returns_value = Column(Float)
    is_check_low_robust_universe_sharpe_result = Column(String)
    is_check_low_robust_universe_sharpe_ratio = Column(Float)
    is_check_low_robust_universe_sharpe_limit = Column(Float)
    is_check_low_robust_universe_sharpe_value = Column(Float)
    is_check_low_robust_universe_returns_result = Column(String)
    is_check_low_robust_universe_returns_ratio = Column(Float)
    is_check_low_robust_universe_returns_limit = Column(Float)
    is_check_low_robust_universe_returns_value = Column(Float)
    is_check_units_result = Column(String)
    is_check_units_message = Column(String)
    is_check_self_correlation_result = Column(String)
    is_check_matches_competition_result = Column(String)
    alpha_link = Column(String)
    alpha_code = Column(String)

engine = create_engine('sqlite:///alphas/alpha_results.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
DBSession = Session()