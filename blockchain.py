from datetime import date
from block import Block, data
GENESIS_DATA = data(batch_id=-1, name="Genesis", manufacturer="System", expiry_date=date.today())

"""  
block0 = Block(0, "Manufactured: Paracetamol", "0", "Mumbai", "PharmaCorp")
print("Block 0 hash:", block0.hash)

block1 = Block(1, "Shipped: Paracetamol", block0.hash, "Delhi", "LogisticsHub")
print("Block 1 hash:", block1.hash)
"""

class BlockChain:
    def __init__(self, data , location ,add_by):
        self.data = data
        self.location = location
        self.add_by = add_by
        self.head = self.create_genesis_block() #i think i have done this thing write
        self.last_block = self.head # hey when we create a block chain its actually only one block so last and same will be one #i seriously cant figure out how to do this
    
    def create_genesis_block(self):
        genesis_block=Block(0 , GENESIS_DATA , None , "0" ,self.location,self.add_by) #fixed the Genesis issue as the root node is mostly symbolic should not have real data 
        return genesis_block
    #(self, index, data,previous_block, previous_hash,location,add_by ,timestamp=None
    def add_block(self,data,location,add_by): #here added the data as before it was taking same data shared resource which was kinda risky
        self.validate_data(data)  # It will raise if anything’s wrong # change this as self.validate_date(data) is not returning anything


        index=self.last_block.index+1
        previous_block=self.last_block
        previous_hash=self.last_block.hash        
        new_block=Block(index , data , previous_block , previous_hash , location ,add_by)
        self.last_block=new_block
   
   
    def validate_data(self, data_obj):
        if self.is_duplicate_batch(data_obj.batch_id):
            raise ValueError("Duplicate batch ID detected.")
        
        # Check expiry is in future
        if data_obj.expiry_date <= date.today():
            raise ValueError("Medicine is expired!")

        # Check required fields
        if not all([data_obj.name, data_obj.manufacturer, data_obj.batch_id]):
            raise ValueError("Missing important medicine info.")
    # Check for duplicate batch_id
    def is_duplicate_batch(self, batch_id): #move this is_duplicate_batch outside so that it can be reusable 
        current = self.last_block
        while current is not None:
            if current.data.batch_id == batch_id:
                return True
            current = current.previous_block
        return False
    def validate(self):
        current_block=self.last_block

        while current_block is not None:
            if current_block.hash!=current_block.calculate_hash():
                return False
            if  current_block.previous_block is not None:
                if current_block.previous_hash!=current_block.previous_block.calculate_hash():
                    return False
            current_block=current_block.previous_block

        return True
    
    def print_chain(self):
        current = self.last_block
        while current:
            print(f"Index: {current.index}, Location: {current.location}, By: {current.add_by}, Hash: {current.hash}")
            current = current.previous_block

"""
chain = BlockChain("Paracetamol 500mg", "Mumbai", "PharmaCorp")
chain.add_block("Delhi", "Logistics Hub")
chain.add_block("Lucknow", "Retail Store")

chain.print_chain()  # optional
"""
    