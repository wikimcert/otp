# Python Google OTP Plugin for FlaskFarm
- - - 
## 1. FlaskFarm
- FlaskFarm(FF)는 Flask 기반의 Python 패키지로 모듈형태의 플러그인을 자유롭게 붙일 수 있는 개발프레임워크입니다.
- FF에 관한 보다 상세한 정보는 아래 링크를 참고하세요. 
- github: <https://github.com/flaskfarm/flaskfarm>
- githubio: <https://flaskfarm.github.io/>
- PyPi: <https://pypi.org/project/FlaskFarm/>
- docker: <https://hub.docker.com/repository/docker/flaskfarm/flaskfarm>

## 2. OTP 플러그인
- FF기반의 플러그인 모듈로 Google OTP 연동을 위한 QR 생성 및 인증 API를 제공
### 2.1 관리자 기능
- OTP를 사용할 사용자 계정 생성 및 관리
- OTP 인증 이력 조회
### 2.2 사용자 기능
- Google OTP 연동을 위한 SecretKey 생성(QR이미지) 및 등록
- OTP 인증 API 연동
