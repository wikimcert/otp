from .setup import *
from sqlalchemy import func, and_, not_

logger = P.logger

class ModelUserItem(ModelBase):
    P = P
    __tablename__ = '%s_users' % __package__
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = __package__

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime)
    reserved = db.Column(db.JSON)

    name = db.Column(db.String)
    company = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.LargeBinary)
    secret_key = db.Column(db.String)

    def as_mydict(self):
        ret = {}
        for x in self.__table__.columns:
            if x.name == 'password':
                ret[x.name] = getattr(self, x.name).decode('utf-8')
            elif isinstance(getattr(self, x.name), datetime):
                ret[x.name] = getattr(self, x.name).strftime('%m-%d %H:%M:%S')
            else:
                ret[x.name] = getattr(self, x.name)
        return ret

    def __init__(self, name, company, email, password, secret_key=None):
        self.created_time = datetime.now()
        self.name = name
        self.company = company
        self.password = password
        self.email = email
        self.secret_key = secret_key

    @classmethod
    def get_by_email(cls, email):
        with F.app.app_context():
            return F.db.session.query(cls).filter_by(email=email).first()

    @classmethod
    def get_all_entities(cls):
        with F.app.app_context():
            return F.db.session.query(cls).all()

    @classmethod
    def web_list(cls, req):
        try:
            ret = {}
            page = 1
            page_size = 30
            search = ''
            category = ''
            if 'page' in req.form:
                page = int(req.form['page'])
            if 'keyword' in req.form:
                search = req.form['keyword'].strip()
            order = req.form.get('order', 'desc')
            query = cls.make_query(search=search)
            count = query.count()
            query = query.limit(page_size).offset((page-1)*page_size)
            logger.debug('cls count:%s', count)
            lists = query.all()
            ret['list'] = [item.as_mydict() for item in lists]
            ret['paging'] = cls.get_paging_info(count, page, page_size)
            return ret
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return ret

    @classmethod
    def make_query(cls, search='', order='desc'):
        with F.app.app_context():
            query = F.db.session.query(cls)
            if search is not None and search != '':
                if search.find('|') != -1:
                    tmp = search.split('|')
                    conditions = []
                    for tt in tmp:
                        if tt != '':
                            conditions.append(cls.email.like('%'+tt.strip()+'%') )
                    query = query.filter(or_(*conditions))
                elif search.find(',') != -1:
                    tmp = search.split(',')
                    for tt in tmp:
                        if tt != '':
                            query = query.filter(cls.email.like('%'+tt.strip()+'%'))
                else:
                    query = query.filter(cls.email.like('%'+search+'%'))

            if order == 'desc': query = query.order_by(desc(cls.id))
            else: query = query.order_by(cls.id)
            return query

class ModelAuthItem(ModelBase):
    P = P
    __tablename__ = '%s_auth' % __package__
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = __package__

    id = db.Column(db.Integer, primary_key=True)
    auth_time = db.Column(db.DateTime)
    reserved = db.Column(db.JSON)

    email = db.Column(db.String)
    otpno = db.Column(db.String)
    status = db.Column(db.String)
    result = db.Column(db.String)

    def as_mydict(self):
        ret = {}
        for x in self.__table__.columns:
            if isinstance(getattr(self, x.name), datetime):
                ret[x.name] = getattr(self, x.name).strftime('%m-%d %H:%M:%S')
            else:
                ret[x.name] = getattr(self, x.name)
        return ret

    def __init__(self, email, otpno):
        self.auth_time = datetime.now()
        self.email = email
        self.otpno = otpno
        self.status = None
        self.result = None

    @classmethod
    def get_by_email(cls, email):
        with F.app.app_context():
            return F.db.session.query(cls).filter_by(email=email).first()

    @classmethod
    def get_all_entities(cls):
        with F.app.app_context():
            return F.db.session.query(cls).all()

    @classmethod
    def web_list(cls, req):
        try:
            ret = {}
            page = 1
            page_size = 30
            search = ''
            category = ''
            if 'page' in req:
                page = int(req['page'])
            if 'keyword' in req:
                search = req['keyword'].strip()
            if 'optauth' in req:
                option1 = req['optauth']
            order = 'desc'
            query = cls.make_query(search=search, option1=option1)
            count = query.count()
            query = query.limit(page_size).offset((page-1)*page_size)
            logger.debug('cls count:%s', count)
            lists = query.all()
            ret['list'] = [item.as_mydict() for item in lists]
            ret['paging'] = cls.get_paging_info(count, page, page_size)
            return ret
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return ret

    @classmethod
    def make_query(cls, search='', option1='all', order='desc'):
        with F.app.app_context():
            query = F.db.session.query(cls)
            if search is not None and search != '':
                if search.find('|') != -1:
                    tmp = search.split('|')
                    conditions = []
                    for tt in tmp:
                        if tt != '':
                            conditions.append(cls.email.like('%'+tt.strip()+'%') )
                    query = query.filter(or_(*conditions))
                elif search.find(',') != -1:
                    tmp = search.split(',')
                    for tt in tmp:
                        if tt != '':
                            query = query.filter(cls.email.like('%'+tt.strip()+'%'))
                else:
                    query = query.filter(cls.email.like('%'+search+'%'))

            if option1 != 'all':
                if option1 == 'success': query = query.filter(cls.status=='200')
                else: query = query.filter(not_(cls.status=='200'))

            if order == 'desc': query = query.order_by(desc(cls.id))
            else: query = query.order_by(cls.id)
            return query
