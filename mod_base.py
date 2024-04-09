from support import SupportSubprocess, SupportFile
from tool import ToolUtil

from .setup import *
from .models import *

import shutil

name = 'base'
ModelSetting = P.ModelSetting

class ModuleBase(PluginModuleBase):

    def __init__(self, P):
        super(ModuleBase, self).__init__(P, name='base', first_menu='setting')
        self.db_default = {
            'otp_db_version'         : '1',
            'otp_name'               : 'OTP_NAME',
            'data_path'              : f'/data/{__package__}/qr',
            'register_template_path' : f'/data/{__package__}/templates/otp_register.html',
            'validate_template_path' : f'/data/{__package__}/templates/otp_validate.html',
        }
        self.web_listmodel = None

    def plugin_load(self):
        if not os.path.exists(os.path.join(ModelSetting.get('data_path'), 'qr')):
            ret = os.makedirs(os.path.join(ModelSetting.get('data_path'), 'qr'))
            logger.info(f'make path: ({os.path.join(ModelSetting.get("data_path"), "qr")}), ret({ret})')
        template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
        logger.debug(f'[template_dir] {template_dir}')
        if not os.path.exists(ModelSetting.get('register_template_path')):
            if not os.path.exists(os.path.dirname(ModelSetting.get('register_template_path'))):
                os.makedirs(os.path.dirname(ModelSetting.get('register_template_path')))
            src_path = os.path.join(template_dir, os.path.basename(ModelSetting.get('register_template_path')))
            dst_path = ModelSetting.get('register_template_path')
            logger.debug(f'[template_copy] {src_path} > {dst_path}')
            shutil.copyfile(os.path.join(template_dir, os.path.basename(ModelSetting.get('register_template_path'))),
                    ModelSetting.get('register_template_path'))
        if not os.path.exists(ModelSetting.get('validate_template_path')):
            if not os.path.exists(os.path.dirname(ModelSetting.get('validate_template_path'))):
                os.makedirs(os.path.dirname(ModelSetting.get('validate_template_path')))
            src_path = os.path.join(template_dir, os.path.basename(ModelSetting.get('validate_template_path')))
            dst_path = ModelSetting.get('validate_template_path')
            logger.debug(f'[template_copy] {src_path} > {dst_path}')
            shutil.copyfile(os.path.join(template_dir, os.path.basename(ModelSetting.get('validate_template_path'))),
                    ModelSetting.get('validate_template_path'))

    def process_api(self, sub, req):
        try:
            import pyotp
            import qrcode
            import bcrypt

            arg = {}
            ret = {}
            item = None

            email = req.args.get('email', None)
            password = req.args.get('password', None)
            otpno = req.args.get('otpno', None)
            arg['email'] = email
            arg['password'] = password

            if sub == 'register':
                return render_template(f'{self.P.package_name}_register.html', arg=arg)

            if sub == 'generate':

                item = ModelUserItem.get_by_email(email)
                if not item:
                    ret['data'] = '등록되지 않은 메일주소 입니다. 담당자에게 문의해주세요'
                    ret['ret'] = 'error'
                    return jsonify(ret)

                if not bcrypt.checkpw(password.encode('utf-8'), item.password):
                    ret['data'] = '잘못된 비밀번호를 입력하셨습니다.'
                    ret['ret'] = 'error'
                    return jsonify(ret)

                if item.secret_key != None:
                    ret['data'] = f'{item.email} 님은 이미 인증키를 발급받으셨습니다.'
                    ret['ret'] = 'error'
                    return jsonify(ret)

                oname = ModelSetting.get('otp_name')
                skey = pyotp.random_base32()

                otp_url = pyotp.totp.TOTP(skey).provisioning_uri(name=email, issuer_name=oname)
                qr = qrcode.make(otp_url)
                qr_name = f'qrcode-{skey}.png'
                qr_path = os.path.join(ModelSetting.get('data_path'), qr_name)
                logger.debug(f'[datapath] {ModelSetting.get("data_path")}')
                logger.debug(f'[QRPATH] {qr_path}')
                qr.save(qr_path)

                item.secret_key = skey
                item.save()

                ret['data'] = {'secret_key':skey, 'otp_url':otp_url, 'qr_path':qr_path}
                ret['ret'] = 'success'
                return jsonify(ret);
            elif sub == 'validate':
                item = ModelUserItem.get_by_email(email)
                aitem = ModelAuthItem(email, otpno)
                if not item:
                    aitem.result = 'Bad Request(잘못된메일주소)'
                    aitem.status = '400'
                    aitem.save()
                    return {"msg": "인증실패: 잘못된 메일주소"}, 400

                totp = pyotp.totp.TOTP(item.secret_key)
                if totp.verify(otpno):
                    logger.info(f'[인증성공] {email} - OTP No.: {otpno}')
                    aitem.status = '200'
                    aitem.result = '200 Ok(인증성공)'
                    aitem.save()
                    return {"msg": "인증성공"}, 200
                else:
                    logger.warning(f'[인증실패] {email} - OTP No.: {otpno}')
                    aitem.status = '401'
                    aitem.result = '401 Unauthorized(인증실패:otpno불일치)'
                    aitem.save()
                    return {"msg": "인증실패: OTP코드 불일치"}, 401

            return jsonify(ret)
        except Exception as e:
            logger.exception("Exception while processing api requests:")
            return jsonify({"ret": "failed", "log": str(e)})


    def process_menu(self, page, req):
        arg = P.ModelSetting.to_dict()
        arg['register_url'] = F.SystemModelSetting.get('ddns') + f'/{self.P.package_name}/api/register?apikey={F.SystemModelSetting.get("apikey")}'
        arg['validate_url'] = F.SystemModelSetting.get('ddns') + f'/{self.P.package_name}/api/validate?apikey={F.SystemModelSetting.get("apikey")}&email=[메일주소]&otpno=[OTP번호]'
        logger.info(f'[{self.name}] req({req}, {req.args})')
        return render_template(f'{self.P.package_name}_{self.name}_{page}.html', arg=arg)

    def process_command(self, command, arg1, arg2, arg3, req):
        logger.info(f'[page_training] command({command}), {arg1}, {arg2}, {arg3}')
        ret = {'ret':'success', 'data':'success'}
        try:
            pass
        except Exception as e:
            logger.error(f"Exception:{str(e)}")
            logger.error(traceback.format_exc())
            ret = {'ret':'error', 'data':f'{str(e)}'}

        return jsonify(ret)
