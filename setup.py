setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': None,
    'menu': {
        'uri': __package__,
        'name': 'WikimOTP',
        'list': [
            {
                'uri': 'base',
                'name': '기본설정',
                'list': [
                    {'uri': 'setting', 'name': '기본정보'},
                ]
            },
            {
                'uri':'otp',
                'name':'OTP관리',
                'list': [
                    {'uri': 'user', 'name': '사용자관리'},
                    {'uri': 'auth', 'name': '인증결과'},
                ]
            },
            {
                'uri': 'log',
                'name': '로그',
            },
        ]
    },
    'setting_menu': None,
    'default_route': 'normal',
}


from plugin import *

P = create_plugin_instance(setting)

try:
    from .mod_base import ModuleBase
    from .mod_otp import ModuleOtp
    P.set_module_list([ModuleBase, ModuleOtp])
except Exception as e:
    P.logger.error(f'Exception:{str(e)}')
    P.logger.error(traceback.format_exc())

logger = P.logger
