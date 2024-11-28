import os

env=os.environ.get
dir_path=os.path.dirname(__file__)

class Gpt4oConfig:
    API_ENDPOINT = os.getenv('API_ENDPOINT','https://ws-azure-openai-south-central-us.openai.azure.com/')
    API_KEY=os.getenv('API_KEY','3N9yd0NBoNuSLmSlXYvbc87JOAVp204XJBjBVicEPCOG470e6T9iJQQJ99AKACLArgHXJ3w3AAABACOGEuHH')
    MODEL_NAME=os.getenv('MODEL_NAME','gpt-4o')
    API_VERSION=os.getenv('API_VERSION','2024-02-15-preview')


base_config=Gpt4oConfig()