from woot.api import AsyncChatwoot
from typing import Optional, Dict
from loguru import logger as log    
    
async def create_account_bot(chatwoo_url: str,
                             access_key: str,
                             account_id: int,
                             name: str,
                             description: str):
    
    chatwoot = AsyncChatwoot(chatwoot_url=chatwoo_url, access_key=access_key)

    bot = await chatwoot.account_agent_bot.create(
        account_id=account_id,
        name=name,
        description=description
    )
    return bot


async def find_bot_by_name(chatwoo_url: str,
                           access_key: str,
                           account_id: int,
                           name: str) -> Optional[Dict]:
    
    chatwoot = AsyncChatwoot(chatwoot_url=chatwoo_url, access_key=access_key)

    bots = chatwoot.account_agent_bot
    response = await bots.list(account_id=account_id)

    for bot in response.body:
        if bot["name"] == name:
            return bot
    return None


async def update_bot(chatwoo_url: str,
                     access_key: str,
                     account_id: int,
                     bot_id: int,
                     name: str,
                     description: Optional[str] = None,
                     webhook_url: Optional[str] = None):
        
        chatwoot = AsyncChatwoot(chatwoot_url=chatwoo_url, access_key=access_key)
    
        bot = await chatwoot.account_agent_bot.update(
            account_id=account_id,
            id=bot_id,
            name=name,
            description=description,
            outgoing_url=webhook_url
        )
        return bot


async def upsert_bot(chatwoo_url: str,
                     access_key: str,
                     account_id: int,
                     name: str,
                     webhook_url: str,
                     description: str):
        
        bot = await find_bot_by_name(chatwoo_url, access_key, account_id, name)
        if bot:
            log.info(f"Bot {name} already exists. Updating...")
            return await update_bot(chatwoo_url, 
                                    access_key, 
                                    account_id, 
                                    bot["id"], 
                                    name, 
                                    description, 
                                    webhook_url)
    
        log.info(f"Bot {name} does not exist. Creating...")
        return await create_account_bot(chatwoo_url, 
                                        access_key, 
                                        account_id, 
                                        name, 
                                        description)







# if __name__ == "__main__":
    # import asyncio
    # asyncio.run(main())
    
    # asyncio.run(create_account_bot(os.environ.get("CHATWOOT_URL"),
    #                                os.environ.get("CHATWOOT_ACCESS_KEY"),
    #                                os.environ.get("CHATWOOT_ACCOUNT_ID"),
    #                                "Ale Test Bot",
    #                                "Bot de prueba para Ale"))

    # res = asyncio.run(find_bot_by_name(os.environ.get("CHATWOOT_URL"),
    #                                 os.environ.get("CHATWOOT_ACCESS_KEY"),
    #                                 os.environ.get("CHATWOOT_ACCOUNT_ID"),
    #                                 "Ale Test Bot"))
    
    
    # res = asyncio.run(update_bot(os.environ.get("CHATWOOT_URL"),
    #                             os.environ.get("CHATWOOT_ACCESS_KEY"),
    #                             os.environ.get("CHATWOOT_ACCOUNT_ID"),
    #                             73,
    #                             "Ale Test Bot",
    #                             "Bot de prueba para Ale",
    #                             "https://alebot.com/webhook"))
    
    # print (res)