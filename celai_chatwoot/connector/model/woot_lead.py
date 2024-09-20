from cel.gateway.model.conversation_lead import ConversationLead
from cel.gateway.model.conversation_peer import ConversationPeer


class WootLead(ConversationLead):

    def __init__(self, 
                 account_id: str, 
                 inbox_id:str, 
                 conversation_id:str,
                 message_type: str = None, 
                 **kwargs):
        super().__init__(connector_name="chatwoot", **kwargs)
        self.account_id = str(account_id)
        self.inbox_id = str(inbox_id)
        self.conversation_id = str(conversation_id)
        self.message_type = message_type


    def get_session_id(self):
        return f"{self.connector_name}:{self.account_id}:{self.inbox_id}:{self.conversation_id}"

    def to_dict(self):
        data = super().to_dict()
        data['account_id'] = self.account_id
        data['inbox_id'] = self.inbox_id
        data['conversaiton_id'] = self.conversation_id
        return data

    @classmethod
    def from_dict(cls, lead_dict):
        return WootLead(
            metadata=lead_dict.get("metadata"),
            account_id=lead_dict.get("account_id"),
            inbox_id=lead_dict.get("inbox_id"),
            conversation_id=lead_dict.get("conversaiton_id"),
        )

    def __str__(self):
        return f"TelegramLead: {self.chat_id}"
    
    
    @classmethod
    def from_chatwoot_message(cls, message: dict, **kwargs) -> 'WootLead':
        
        conversation_id = message.get('conversation', {}).get('id')
        account_id = message.get('account', {}).get('id')
        inbox_id = message.get('inbox', {}).get('id')
        message_type = message.get('message_type')
        
        assert conversation_id, "Conversation ID is required"
        assert account_id, "Account ID is required"
        assert inbox_id, "Inbox ID is required"
        
        metadata = {
            'inbox_id': inbox_id,
            'event': message.get('event'),
            'message_type': message_type,
            'private': message.get('private'),
            # 'message_id': str(message.get('message_id')),
            'date': message.get('created_at'),
            'raw': message
        }
        conversation_peer = ConversationPeer(
            name=message['sender'].get('name') if message.get('sender') else None,
            id=str(message['sender'].get('id')) if message.get('sender') else None,
            phone=message['sender'].get('phone_number') if message.get('sender') else None,
            avatarUrl=message['sender'].get('avatar') if message.get('sender') else None,
            email=message['sender'].get('email') if message.get('sender') else None,
            metadata=message['sender'].get('additional_attributes') if message.get('sender') else None
        )
        return WootLead(
            metadata=metadata,
            account_id=account_id,
            inbox_id=inbox_id,
            conversation_id=conversation_id,
            conversation_from=conversation_peer,
            message_type=message_type,
            **kwargs
        )
        
