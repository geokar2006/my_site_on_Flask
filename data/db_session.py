import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f'{db_file.strip()}'
    engine = sa.create_engine(conn_str, echo=False, pool_size=20, max_overflow=0)
    __factory = orm.sessionmaker(bind=engine)
    __factory.expire_on_commit = False
    from . import __all_models
    SqlAlchemyBase.metadata.create_all(engine)
    init_settings()


def init_settings():
    db_sess = create_session()
    from data.site_settings import site_settings
    settings = db_sess.query(site_settings).filter(site_settings.id == 1).first()
    if not settings:
        sett = site_settings()
        sett.id = 1
        sett.debug_mode = False
        db_sess.add(sett)
        db_sess.commit()


def create_session() -> Session:
    global __factory
    return __factory()
