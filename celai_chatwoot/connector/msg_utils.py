from woot.api import AsyncChatwoot
from typing import Optional, Dict
from loguru import logger as log    
    
async def send_text_message(chatwoo_url: str,
                            access_key: str,
                            account_id: int,
                            conversation_id: int,
                            text: str,
                            private: bool = False) -> Dict:
    
    chatwoot = AsyncChatwoot(chatwoot_url=chatwoo_url, access_key=access_key)   

    res = await chatwoot.messages.create(
        account_id=account_id,
        conversation_id=conversation_id,
        content=text,
        message_type="outgoing",
        private=private
    )

    return res



if __name__ == "__main__":
    import asyncio
    import os
    
    async def main():
        res = await send_text_message(os.environ.get("CHATWOOT_URL"),
                           os.environ.get("CHATWOOT_ACCESS_KEY"),
                           os.environ.get("CHATWOOT_ACCOUNT_ID"),
                           34,
                           "Hello, world!")
        print(res)
    
    
    asyncio.run(main())
