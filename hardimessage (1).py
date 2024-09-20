class HardiMessage:
    
    def __init__(self, sourceID, destID, req, resp, message = "?"):
        self.sourceID = sourceID
        self.destID = destID
        self.req = bool(req)
        self.resp = bool(resp)
        self.msg = message
        self.Protocol = "hardimessage"
    
    def create_message(self):
        request = 'false' if not self.req else 'true'
        response = 'false' if not self.resp else 'true'
        fields = [
            f"{self.Protocol}", 
            f"{self.sourceID}", f"{self.destID}",
            f"{request}", f"{response}",
            f"{self.msg}"
        ]
        message = "/".join(fields)
        return message
    
    def read_message(self, recv):
        fields = recv.split("/")
        if fields[0] != self.Protocol:
            raise ValueError("Message format not compatible, try another")
        self.sourceID = fields[1]
        self.destID = fields[2]
        self.req = False
        self.resp = False
        if fields[3] == "true":
            self.req = True
        if fields[4] == "true":
            self.resp = True
        self.msg = fields[5]
        
        
        