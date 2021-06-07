import hashlib
import json
from time import time
from flask import Flask, jsonify, request
from uuid import uuid4
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        # Create the genesis blockchain
        self.new_block(previous_hash = '1', proof = 100)
    def new_block(self, proof, previous_hash = None):
        # Create a new Block and adds it to the chain
        block = {
        'index'         : len(self.chain) + 1,
        'timestamp'     : time(),
        'transactions'  : self.pending_transactions,
        'proof'         : proof,
        'previous_hash' : previous_hash or self.hash(self.chain[-1])
        }
        # Reset the current list of pending_transactions
        self.pending_transactions = []
        self.chain.append(block)
        return block
    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transactions
        self.pending_transactions.append({
            "sender"    : sender,
            "recipient" : recipient,
            "amount"    : amount
        })
        return self.last_block['index'] + 1
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(block_string).hexdigest()
    @property
    def last_block(self):
        return self.chain[-1]
    @staticmethod
    def proof_of_work(block):
        while not Blockchain.valid_proof(block):
            block["proof"] += 1
    @staticmethod
    def valid_proof(block):
        return Blockchain.hash(block) [:4] == "0000"
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')
blockchain = Blockchain()
@app.route('/mine', methods = ["GET"])
def mine():
    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1
    )
    block = blockchain.new_block(0)
    blockchain.proof_of_work(block)
    response = {
        "message"           : "New block mined",
        "index"             : block["index"],
        "transactions"      : block["transactions"],
        "proof"             : block["proof"],
        "previous_hash"     : block["previous_hash"]
    }
    return jsonify(response), 200
@app.route('/transactions/new', methods = ["POST"])
def new_transaction():
    values = request.get_json()
    if not values:
        return "Missing body", 400
    required = ['sender', "recipient", "amount"]
    if not all(k in values for k in required):
        return "Missing values", 400
    index = blockchain.new_transaction(values["sender"], values["recipient"], values["amount"])
    response = { "message": "Transaction will be added to block {index}" }
    return jsonify(response), 201
@app.route('/chain', methods = ["GET"])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
# if __name__ == "__main__":
#     blockchain = Blockchain()
#     blockchain.proof_of_work(blockchain.last_block)
#     print(blockchain.hash(blockchain.last_block))
