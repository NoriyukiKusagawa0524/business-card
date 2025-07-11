import json
import os
import sys
import httpx
from visionApi import detect_text
from createChat import create_chat
# from postStein import post_stein_api
from setSheets import set_sheets
from dotenv import load_dotenv;load_dotenv()
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
  AsyncApiClient,
  AsyncMessagingApi,
  Configuration,
  PushMessageRequest,
  ReplyMessageRequest,
  TextMessage
)
from linebot.v3.exceptions import (
  InvalidSignatureError,
)
from linebot.v3.webhooks import (
  MessageEvent,
  TextMessageContent,
  ImageMessageContent
)
from starlette.exceptions import HTTPException

# 環境設定(トークンの確認)
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
  print('Specify CHANNEL_SECRET as environment variable.')
  sys.exit(1)
if channel_access_token is None:
  print('Specify CHANNEL_ACCESS_TOKEN as environment variable.')
  sys.exit(1)

configuration = Configuration(
  access_token=channel_access_token
)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

## =========== エクスポートしている関数 ==========

# 検証と取得
def handle_signature(body, signature):
  try:
    events = parser.parse(body, signature)
    return events
  except InvalidSignatureError:
    raise HTTPException(status_code=400, detail="Invalid signature")
  
# イベントハンドラー 画像、もしくはテキスト
async def events_handler(events):
  for event in events:
    if not isinstance(event, MessageEvent):
      continue
    if isinstance(event.message, ImageMessageContent):
      await reply_sender(event.reply_token, [TextMessage(text='画像を受け付けました')])
      await image_handler(event.source.user_id, event.message.id)
      return 'OK'
    if isinstance(event.message, TextMessageContent):      
      await reply_sender(event.reply_token, [TextMessage(text=event.message.text)])
      return 'OK'
    else:
      continue
  
## ========== 以下ヘルパー関数 ==========

async def reply_sender(reply_token: str, messages: list[str]):
  await line_bot_api.reply_message(
    ReplyMessageRequest(
      reply_token=reply_token,
      messages=messages
    )
  )

async def push_sender(user_id: str, messages: list[str]):
  await line_bot_api.push_message(
    PushMessageRequest(
      to=user_id,
      messages=messages
    )
  )
  
async def image_handler(user_id: str, message_id: str):
  # 画像取得
  image_content = await get_image_content(message_id=message_id)
  try: 
    # visonapi に画像を投げる
    res_text = detect_text(content=image_content)
  except Exception as e:
    print(e)
    return await push_sender(user_id, [TextMessage(text='OCRに失敗しました')])
  
  try:
    # gpt api に文字列を投げる
    name_card_text = create_chat(res_text)
    res_gpt = json.loads(name_card_text.choices[0].message.content)
  except Exception as e:
    print(e)
    return await push_sender(user_id, [TextMessage(text='テキスト解析に失敗しました')])
  
  try:
    # gpt api から返ってきた文字列をスプシに投げる
    res = set_sheets(res_gpt)
    print(res)
    if res == '200':
      return await push_sender(user_id, [TextMessage(text='データのアップロードに成功しました')])
    else:
      return await push_sender(user_id, [TextMessage(text='データのアップロードに失敗しました')])
  except Exception as e:
    print(e)
    return await push_sender(user_id, [TextMessage(text='データのアップロードに失敗しました')])
  
# LineBot から画像を取得する
async def get_image_content(message_id: str):
  url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
  headers = {"Authorization": f"Bearer {channel_access_token}"}
  async with httpx.AsyncClient() as client:
    response = await client.get(url, headers=headers)
  if response.status_code == 200:
    return response.content
  else:
    raise HTTPException(status_code=response.status_code, detail="Failed to get image content")