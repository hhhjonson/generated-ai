import requests
from config import learn_config

class MicrosoftLearnGet:
    def __init__(self):
        self.client_id=learn_config.client_id
        self.client_secret=learn_config.client_secret
        self.tenant_id=learn_config.tenant_id
        self.url=learn_config.url

    def get_access_token(self):
        url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = {
            "client_id":self.client_id,
            "client_secret":self.client_secret,
            "scope":"https://graph.microsoft.com/.default",
            "grant_type":"client_credentials"
        }

        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return access_token
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
    
    def get_courses_for_grade(self,grade):
        token = self.get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "filter": f"grade ge {grade}",  # 例如，过滤出成绩大于或等于给定值的课程
            "top": 5  # 获取前5个课程
        }
        
        response = requests.get(self.url, headers=headers, params=params)
        courses = response.json()
        return courses
