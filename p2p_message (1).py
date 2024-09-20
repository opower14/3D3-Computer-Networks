import re

class P2PMessage:
    protocol_name = "p2p_message"
    protocol_version = "1.1"

    def __init__(self, message_type, sender_id, recipient_id, message = "-"):
        self.message_type = message_type  # 'request' or 'response'
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message = message # darf nicht leer bleiben

    def encode(self):
        """
        konvert message from P2P message to String
        """
        lines = [
            f"Protocol-Name: {self.protocol_name}",
            f"Protocol-Version: {self.protocol_version}",
            f"Message-Type: {self.message_type}",
            f"Sender-ID: {self.sender_id}",
            f"Recipient-ID: {self.recipient_id}",
            f"Message: {self.message}",
            ""  # Leerzeile als Abschluss
        ]
        return "\n".join(lines)

    @staticmethod
    def decode(message_str):
        pattern = "Protocol-Name:(.+)\nProtocol-Version:(.+)\nMessage-Type:(.+)\nSender-ID:(.+)\nRecipient-ID:(.+)\nMessage:(.+)\n"

        if not re.match(pattern, message_str):
            raise ValueError("No p2p_message structure")

        """Erstellt eine P2PMessage-Instanz aus einem String und prüft das Protokoll und die Version."""
        lines = message_str.strip().split("\n")
        fields = {line.split(": ")[0]: line.split(": ")[1] for line in lines}

        # Überprüfung des Protokollnamens und der Version
        if fields["Protocol-Name"] != P2PMessage.protocol_name or fields["Protocol-Version"] != P2PMessage.protocol_version:
            raise ValueError("Protokollname oder -version stimmt nicht überein")

        return P2PMessage(
            message_type=fields["Message-Type"],
            sender_id=fields["Sender-ID"],
            recipient_id=fields["Recipient-ID"],
            message=fields["Message"]
        )

