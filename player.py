#!/usr/bin/env python

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# (c) Ricardo Cristovao Miranda, 2014, mail@ricardomiranda.com

# Program to the Snap! Card Game between two computer players. using 1 pack of
# cards (standard 52 card, 4 suit packs). The "Snap!" matching condition can be the face
# value of the card, the suit, or both.

import sys
import pika
import json

class player(object):
    deckL = list()

    def __init__(self, name):
        print 'Press Ctrl^C to end program'

        self.name = name

        self.connection = pika.AsyncoreConnection(pika.ConnectionParameters(host       ='localhost',
                                                                            credentials=pika.PlainCredentials('guest', 'guest')))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='cards',
                                      type    ='direct')

        self.result = self.channel.queue_declare(exclusive=True)
        self.queue_name = self.result.queue

        self.exchange_name = 'cards'
        self.bindingKeys   = ['players', 'pileCards', 'deckNbr']
        for bindingKey in self.bindingKeys:
            self.channel.queue_bind(exchange   =self.exchange_name,
                                    queue      =self.queue_name,
                                    routing_key=bindingKey)

    def loop(self):
        def callback(ch, method, header, body):
            if   body=="emptyDeck":
                message = {"player": self.name, "cardsRemaining": self.cardsRemaining()}
                self.channel.basic_publish(exchange   =self.exchange_name,
                                           routing_key='game',
                                           body       =json.dumps(message))

            elif method.routing_key=="pileCards":
                message = json.loads(body)

                if message['name']==self.name:
                    self.addCard(message)

            elif method.routing_key=="deckNbr":
                del self.deckL[:]
                print 'del player'
                print len(self.deckL)

        self.channel.basic_consume(callback,
                                   queue =self.queue_name,
                                   no_ack=True)

        pika.asyncore_loop()

    def printDeck(self):
        for card in self.deckL:
            print card

    def removeCard(self):
        item = self.deckL.pop(0)

    def addCard(self, message):
        card  = list()
        suit  = message['suit']
        value = message['value']
        card  = [suit, value]

        self.deckL.append(card)

    def cardsRemaining(self):
        return len(self.deckL)

if __name__ == '__main__':
    name = sys.argv[1]

    player = player(name)
    player.loop()

