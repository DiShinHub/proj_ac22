import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()


class Slack():

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    def post_to_slack(self, msg):
        """ 
        def description : 슬랙 메세지 전송 

        Parameters
        ----------
        msg = 메세지

        Returns
        -------
        response_object : 결과 오브젝트 (dict)
        """
        msg = self.generate_post_form(msg)

        slack_data = json.dumps({"blocks": msg})
        response = requests.post(
            self.webhook_url, data=slack_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            response_object = {
                "status": "fail",
                "message": str(response.text)
            }
            return response_object

        response_object = {
            "status": "success",
            "message": "success"
        }
        return response_object

    def generate_post_form(self, msg):
        """ 
        def description : 슬랙 메세지 전송 데이터 포멧팅

        Parameters
        ----------
        msg = 메세지

        Returns
        -------
        data : 포멧팅 데이터 (list)
        """
        data = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": msg
                }
            }
        ]
        return data
