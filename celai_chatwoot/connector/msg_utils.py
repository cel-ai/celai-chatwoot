import aiohttp
from typing import Any, Optional, Dict
from loguru import logger as log

ChatwootMessageTypes = ["incoming", "outgoing"]

async def send_text_message(
    base_url: str,
    account_id: str,
    conversation_id: str,
    access_key: str,
    content: str,
    content_attributes: Optional[Dict[str, Any]] = None,
    content_type: Optional[str] = None,
    message_type: Optional[str] = "outgoing",
    private: Optional[bool] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    assert message_type in ChatwootMessageTypes, f"message_type must be one of {ChatwootMessageTypes}"
    
    url = f"{base_url}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
    log.debug(f"Sending message to Chatwoot url: {url}")

    payload = {
        'content': content,
        'content_attributes': content_attributes,
        'content_type': content_type,
        'message_type': message_type,
        'private': private
    }
    
    # set default headers
    headers = headers or {}
    headers.update({
        'api_access_token': access_key
    })
    
    
    # Remove keys with None values
    payload = {k: v for k, v in payload.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response_data = await response.json()
            return response_data




if __name__ == "__main__":
    import asyncio
    import os
    
    async def main():
       
        res = await send_text_message(os.environ.get("CHATWOOT_URL"),
                                os.environ.get("CHATWOOT_ACCOUNT_ID"),
                                34,
                                os.environ.get("CHATWOOT_ACCESS_KEY"),
                                "Hello, world!",
                                message_type="outgoing",
                                private=False)
                
        
        print(res)
    
    
    asyncio.run(main())
