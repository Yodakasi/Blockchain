import hashlib
from collections import namedtuple
from time import time
import json

class block:
    def __init__(self, previusHash, transactions, difficulty):
        self.date = time()
        self.previusHash = previusHash
        self.transactions = transactions
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = ''
        #self.hash = self.mineHash()

    def calculateHash(self):
        transactionsString = ""
        if type(self.transactions) is not int:
            for i in self.transactions:
                transactionsString += i.fromAdress
                transactionsString += ","
                transactionsString += i.toAdress
                transactionsString += ","
                transactionsString += str(i.amount)
                transactionsString += ","
            transactionsString = transactionsString[0 : -1]
        else:
            transactionsString = str(self.transactions)
        strToHash = (self.previusHash + str(self.date) + transactionsString + str(self.nonce)).encode('utf-8')
        return hashlib.sha256(strToHash).hexdigest()

    def mineHash(self):
        hashed = ''
        while hashed[0 : self.difficulty] != "{}".format('0' * self.difficulty):
            self.nonce += 1
            hashed = self.calculateHash()
        return hashed

    def addBlock(self, date, previusHash, transactions, nonce, difficulty, hash):
        self.date = date
        self.previusHash = previusHash
        self.transactions = []
        transactionScheme = namedtuple('transaction', 'fromAdress toAdress amount')
        for x in transactions:
            transaction = transactionScheme(fromAdress=x[0], toAdress=x[1], amount=int(x[2]))
            self.transactions.append(transaction)
        self.nonce = nonce
        self.difficulty = difficulty
        self.hash = hash


class blockChain:
    def __init__(self, difficulty):
        self.chain = []
        self.transactionsQueue = []
        self.difficulty = difficulty
        self.mineReward = 1
        self.firstBlock()
        #for client purposes mining first block
        self.chain[-1].hash = self.chain[-1].mineHash()


    def firstBlock(self):
        self.chain.append(block('0', 0, self.difficulty))

    def mineBlock(self, adress):
        if len(self.transactionsQueue) < 1:
            return 0
        self.newTransaction('minedReward', adress, self.mineReward)
        self.chain.append(block(self.chain[-1].hash, self.transactionsQueue, self.difficulty))

    def newBlockSchema(self, adress):
        newTrans = True
        for x in self.transactionsQueue:
            if 'minedReward' in x[0]:
                newTrans = False
        if newTrans:
            self.newTransaction('minedReward', adress, self.mineReward)
        return block(self.chain[-1].hash, self.transactionsQueue, self.difficulty)

    def validateChain(self):
        for i in range(len(self.chain)):
            if self.chain[i].calculateHash() != self.chain[i].hash:
                return False
        return True

    def newTransaction(self, froms, to, howMuch):
        transactionScheme = namedtuple('transaction', 'fromAdress toAdress amount')
        transaction = transactionScheme(fromAdress=froms, toAdress=to, amount=int(howMuch))
        self.transactionsQueue.append(transaction)

    def getAdressBalance(self, adress):
        balance = 100
        for i in range(1, len(self.chain)):
            for j in range(0, len(self.chain[i].transactions)):
                if self.chain[i].transactions[j].fromAdress == adress:
                    balance -= self.chain[i].transactions[j].amount
                if self.chain[i].transactions[j].toAdress == adress:
                    balance += self.chain[i].transactions[j].amount
        return balance

    def addBlockFromClient(self, content):
        content = json.loads(content)
        for x in self.chain:
            if x.hash == content['hash']:
                return False
        self.chain.append(block(None, None, None))
        self.chain[-1].addBlock(content['date'], content['previusHash'], content['transactions'], content['nonce'], content['difficulty'], content['hash'])
        self.transactionsQueue = []

    def chainReset(self):
        for i in range(len(self.chain)):
            if self.chain[i].calculateHash() != self.chain[i].hash:
                self.chain = self.chain[0:i]
                return True
        return False

def main():
    print("Initialization:")
    m = blockChain(2)
    m.newTransaction('llll', 'Bob', 150)
    m.newTransaction('llll', 'Bob', 50)
    m.mineBlock('Jon')
    print(m.chain[-1].transactions.fromAdress)
    m.newTransaction('Bob', 'llll', 100)
    m.mineBlock('Jon')
    m.mineBlock('Harry')
    m.mineBlock('Jon')
    print(len(m.transactionsQueue))
    print(m.getAdressBalance('Jon'))


if __name__ == "__main__":
    main()
