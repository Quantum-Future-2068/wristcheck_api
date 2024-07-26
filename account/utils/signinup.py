import requests
import json
from wristcheck_api.settings import env


def wristcheck_signinup(open_id, session_key):
    """Call WristCheck's signinup interface to register a user

    :param open_id: wechat mini program openid
    :param session_key: wechat mini program session_key
    :return:
        {
            "status": "OK",
            "user": {
                "id": "32bef362-d566-41c3-bf4f-7d7b0454fa03",
                "isPrimaryUser": true,
                "tenantIds": [
                    "public"
                ],
                "thirdParty": [
                    {
                        "id": "wechat",
                        "userId": "1234"
                    }
                ],
                "loginMethods": [
                    {
                        "recipeId": "thirdparty",
                        "recipeUserId": "32bef362-d566-41c3-bf4f-7d7b0454fa03",
                        "tenantIds": [
                            "public"
                        ],
                        "thirdParty": {
                            "id": "wechat",
                            "userId": "1234"
                        },
                        "timeJoined": 1721980198742,
                        "verified": true
                    }
                ],
                "timeJoined": 1721980198742
            },
            "createdNewRecipeUser": false
        }
    """
    api = env.str("WRISTCHECK_API", "")
    url = f"{api}/v1/auth/signinup"

    payload = {
        "thirdPartyId": "wechat",
        "clientType": "mp",
        "oAuthTokens": {"openId": open_id, "source": "mp", "session_key": session_key},
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if 200 <= response.status_code < 300:
        return response.json()
    else:
        response.raise_for_status()
