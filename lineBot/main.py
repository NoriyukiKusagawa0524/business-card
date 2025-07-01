# fastapi main
import os
import base64
import hashlib
import hmac
from dotenv import load_dotenv;load_dotenv()
from fastapi import Request, FastAPI
from fastapi.responses import FileResponse
from lineHandler import(
  handle_signature,
  events_handler
)

app = FastAPI()
favicon_path = './public/favicon.ico' # unused

@app.get("/")
def read_root():
  return {"message": "bot server start"}

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
  return FileResponse(favicon_path)

@app.post("/callback")
async def handle_callback(request: Request):
  # ヘッダー確認 -> 大文字小文字が予告なく変わる可能性への考慮
  sig_key = ''
  list_key = list(request.headers.keys())
  if 'X-Line-Signature' in list_key:
    sig_key = 'X-Line-Signature'
  elif 'x-line-signature' in list_key:
    sig_key = 'x-line-signature'
  else:
    # 中断
    print("no signature key.")
    return

  signature = request.headers[sig_key]
  body = await request.body()
  body = body.decode()

  # # 公式推奨の検証
  # if signature != checkSignature(body):
  #   # 中断
  #   print("invalid!")
  #   return

  events = handle_signature(body, signature)
  await events_handler(events)

# signature 検証
def checkSignature(req_body):
  channel_secret = os.getenv('CHANNEL_SECRET', None)
  hash = hmac.new(channel_secret.encode('utf-8'),
      req_body.encode('utf-8'), hashlib.sha256).digest()
  return base64.b64encode(hash)
