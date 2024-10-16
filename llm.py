import os
import json
import requests
from dotenv import load_dotenv
from typing import Optional,List,Any
from langchain_core.language_models.llms import LLM
from langchain_core.pydantic_v1 import Field
from langchain_core.callbacks import CallbackManagerForLLMRun
load_dotenv()

class Baidullm(LLM):
    model_name: str = Field(default='')
    @property
    def _llm_type(self):
        return 'baidu_model'
    
    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        API_KEY = os.environ.get("BAIDU_API_KEY")
        SECRET_KEY = os.environ.get("BAIDU_SECRET_KEY")

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
        return str(requests.post(url, params=params).json().get("access_token"))
    
    def _call(self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any):

        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{}?access_token={}".format(self.model_name, self.get_access_token())
        print('Prompt:',prompt)
        request_data = {
         "messages": [
            {
                "role": "user",
                "content": prompt
            }
            ]
        }
        payload = json.dumps(request_data)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            # print(response.text)
            ans = response.json()['result']
        except Exception as err:
            ans = '调用接口错误' + response['err_msg']
            print("ans: {}, err: {}".format(ans, err))
            
        return ans
