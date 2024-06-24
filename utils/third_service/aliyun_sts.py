from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
import json

from wristcheck_api.settings import (
    ALI_ACCESS_KEY_ID,
    ALI_ACCESS_KEY_SECRET,
    ALI_ROLE_ARN,
    ALI_ROLE_SESSION_NAME,
    ALI_REGION,
    ALI_STS_DURATION_SECONDS,
)


def get_sts_token():
    credentials = AccessKeyCredential(ALI_ACCESS_KEY_ID, ALI_ACCESS_KEY_SECRET)
    client = AcsClient(region_id=ALI_REGION, credential=credentials)

    request = AssumeRoleRequest.AssumeRoleRequest()
    request.set_RoleArn(ALI_ROLE_ARN)
    request.set_RoleSessionName(ALI_ROLE_SESSION_NAME)

    request.set_DurationSeconds(ALI_STS_DURATION_SECONDS)

    response = client.do_action_with_exception(request)
    return json.loads(response)
