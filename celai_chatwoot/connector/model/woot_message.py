from typing import Any
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.message import Message
from celai_chatwoot.connector.model.woot_attachment import WootAttachment
from celai_chatwoot.connector.model.woot_lead import WootLead


class WootMessage(Message):
    
    def __init__(self, 
                 lead: ConversationLead, 
                 text: str = None, 
                 metadata: dict = None, 
                 date: int = None,
                 attachments: list[Any] = None
                ):
        super().__init__(lead, text=text, date=date, metadata=metadata, attachments=attachments)
    
    
    def is_voice_message(self):
        #  check if the message has a voice attachment
        if self.attachments:
            for attach in self.attachments:
                if attach.type == "voice":
                    return True
        return False
    
    @classmethod
    async def load_from_message(cls, message_dict, connector: BaseConnector = None):
        msg : dict = message_dict.get("conversation", {}).get("messages", [None])[0]
        # get text from message or caption if it is a media message
        text = msg.get("content")
        date = msg.get("created_at")
        metadata = {}
        lead = WootLead.from_chatwoot_message(message_dict, connector=connector)
        attachs = await WootAttachment.load_from_message(message_dict)
        return WootMessage(lead=lead, text=text, date=date, metadata=metadata, attachments=attachs)#[attach] if attach else None)
        

    def __str__(self):
        return f"WootMessage: {self.text}"
        
    def __repr__(self):
        return f"WootMessage: {self.text}"
    
    