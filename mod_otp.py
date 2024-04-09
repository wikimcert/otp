from flask import send_from_directory
from support import SupportSubprocess, SupportFile
import bcrypt

from .setup import *
from .models import *

name = 'otp'

@F.app.route("/optget/<path:path>", methods=['GET'])
def get_image(path):
    if path[0] != '/': path = '/' + path
    return send_from_directory(os.path.dirname(path), os.path.basename(path))

class ModuleOtp(PluginModuleBase):

    def __init__(self, P):
        super(ModuleOtp, self).__init__(P, name='otp', first_menu='user')
        self.web_list_model = ModelUserItem

    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        data = None
        logger.info(f'[{self.name}] process_command: {command}, {arg1}, {req}')

        if command == 'register_user':
            ret = self.registert_user(P.logic.arg_to_dict(arg1))
        elif command == 'modify_user':
            ret = self.modify_user(P.logic.arg_to_dict(arg1))
        elif command == 'auth_list':
            ret = ModelAuthItem.web_list(P.logic.arg_to_dict(arg1))
        elif command == 'init_skey':
            user = None
            user = ModelUserItem.get_by_id(int(arg1))
            if not user:
                ret = {'ret':'error', 'data':f'비밀키삭제 실패(잘못된ID:{db_id})'}
            else:
                user.secret_key = None
                ret = {'ret':'success', 'data':f'비밀키초기화 완료(계정:{user.email})'}
                user.save()
        elif command == 'remove_user':
            if ModelUserItem.delete_by_id(int(arg1)):
                ret = {'ret':'success', 'data':f'삭제 완료(ID:{arg1})'}
            else:
                ret = {'ret':'error', 'data':f'삭제 실패(ID:{arg1})'}

        return jsonify(ret)

    def process_menu(self, page, req):
        arg = P.ModelSetting.to_dict()
        logger.info(f'[{self.name}] req({req}, {req.args})')
        return render_template(f'{self.P.package_name}_{self.name}_{page}.html', arg=arg)

    def registert_user(self, req):
        try:
            name = req['name']
            company = req['company']
            email = req['email']
            plain_pw = req['password']
            password = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt())
            logger.info(f'[REG-USER] {name},{company},{email},{password}')

            item = ModelUserItem(name, company, email, password, None)
            item.save()
            return {'ret':'success', 'data':f'사용자등록완료: {name}({email})'}

        except Exception as e:
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            return {'ret':'error', 'data':f'{str(e)}'}

    def modify_user(self, req):
        try:
            mitem = None

            db_id = int(req['m_id'])
            new_name = req['m_name']
            new_company = req['m_company']
            new_email = req['m_email']
            new_password = req['m_password']
            mitem = ModelUserItem.get_by_id(db_id)

            if not mitem:
                return {'ret':'error', 'data':f'사용자 정보 수정 실패: Invalid ID({db_id})'}

            if new_name != mitem.name:
                logger.debug(f'[modify] name changed: {mitem.name} > {new_name}')
                mitem.name = new_name
            if new_company != mitem.company:
                logger.debug(f'[modify] company changed: {mitem.company} > {new_company}')
                mitem.company = new_company
            if new_email != mitem.email:
                logger.debug(f'[modify] email changed: {mitem.email} > {new_email}')
                mitem.email = new_email
            if new_password.encode('utf-8') != mitem.password:
                if not bcrypt.checkpw(new_password.encode('utf-8'), mitem.password):
                    logger.debug(f'[modify] password changed: {mitem.password} > {new_password}')
                    mitem.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            mitem.save()
            return {'ret':'success', 'data':f'사용자 정보 수정완료: {new_email}({db_id})'}

        except Exception as e:
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            return {'ret':'error', 'data':f'{str(e)}'}
