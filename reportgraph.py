#!/usr/bin/env python
#Run using ledger --no-pager --no-color -F '%C|%(t*100)|%A\n' -f <LEDGERFILE> register | ./reportgraph.py | circo -Tsvg > out.svg

import fileinput
import re
import sys

class Entry:
    ident = ""
    amount = 0
    account = ""
    def __init__(self, amount, account, ident = "NONE"):
        self.amount = int(amount)
        self.account = account
        self.ident = ident
    def dump(self):
        print >> sys.stderr, '%s: %s @ %s' % (self.ident, self.amount, self.account)

class Transaction:
    amount = 0
    source = ""
    sink = ""

    def __init__(self, amount, source, sink):
        self.amount = amount
        self.source = source
        self.sink = sink

    def dump(self):
        print >> sys.stderr, '%s %s -> %s' % (self.amount, self.source, self.sink)

class Edge:
    amount = 0
    tx = 0
    sink = 0
    
    def __init__(self, sink):
        self.amount = 0
        self.tx = 0
        self.sink = sink

    def dump(self, source):
        print '%d -> %d [ label="%d in %d Transactions" ];' % (source, self.sink, self.amount, self.tx)


class Node:
    name = ""
    amount_in = 0
    tx_in = 0
    outbound = {}
    node_id = 0

    def __init__(self, name, node_id):
        self.name = name
        self.amount_in = 0
        self.tx_in = 0
        self.node_id = node_id
        self.outbound = {}

    def txout(self):
        return len(self.outbound)

    def amountout(self):
        sum = 0
        for tx in self.outbound.keys():
            sum += self.outbound[tx].amount
        return sum

    def dump(self):
        print '%s [label="%s @ %d\\nIn: %d Transactions @ %d\\nOut: %d Transactions @ %d)"];' % (self.node_id, self.name, self.amount_in - self.amountout(), self.tx_in, self.amount_in, self.txout(), self.amountout())
        for edge in self.outbound.keys():
            self.outbound[edge].dump(self.node_id)

def txfromentries(entries):
    tx = []
    negatives = []
    positives = []
    for entry in entries:
        if entry.amount < 0:
            negatives.append(entry)
        else:
            positives.append(entry)
    
    if len(negatives) == 1:
        for pos in positives:
            tx.append(Transaction(pos.amount, negatives[0].account, pos.account))
        return tx

    if len(positives) == 1:
        for neg in negatives:
            tx.append(Transaction(neg.amount, neg.account, positives[0].account))
        return tx

    print >> sys.stderr, 'Entry could not be reliably resolved into transactions:'
    for entr in entries:
        entr.dump()
    return []
        
def balance(entries):
    balance = 0
    for entry in entries:
        balance += entry.amount
    return balance

def balances(entries):
    return balance(entries) == 0

entries = {}
transactions = []
nodes = {}
expr = re.compile("^(?P<tag>.*)\|(?P<amount>.*)\|(?P<account>.*)$")

# read entries
for line in fileinput.input():
    match = re.match(expr, line)
    #print '%s @ %s -> %s' % (match.group("tag"), match.group("amount"), match.group("account"))
    if match.group("tag") == "":
        continue

    if entries.get(match.group("tag"), None) is None:
        entries[match.group("tag")] = []
    entries[match.group("tag")].append(Entry(match.group("amount"), match.group("account"), match.group("tag")))

#try to match transactions
for transaction in entries.keys():
    if not balances(entries[transaction]):
        print 'Transaction %s does not balance: %s' % (transaction, balance(entries[transaction]))
        for entry in entries[transaction]:
            entry.dump()
        sys.exit(1)
    transactions.extend(txfromentries(entries[transaction]))

#aggregate per source/sink couple
node_ids = 0
for tx in transactions:
    if nodes.get(tx.source, None) is None:
        nodes[tx.source] = Node(tx.source, node_ids)
        node_ids += 1
    if nodes.get(tx.sink, None) is None:
        nodes[tx.sink] = Node(tx.sink, node_ids)
        node_ids += 1
    if nodes[tx.source].outbound.get(tx.sink, None) is None:
        nodes[tx.source].outbound[tx.sink] = Edge(nodes[tx.sink].node_id)
    
    nodes[tx.source].outbound[tx.sink].amount += tx.amount
    nodes[tx.source].outbound[tx.sink].tx += 1
    nodes[tx.sink].amount_in += tx.amount
    nodes[tx.sink].tx_in += 1

#dump
print 'digraph Money {'
for node in nodes.keys():
    nodes[node].dump()
print '}'
