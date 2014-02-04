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

import pika
import re
import json
import random

class pileCards(object):
    deckL = list()

    def __init__(self):
        print 'Press Ctrl^C to end program'

        self.connection = pika.AsyncoreConnection(pika.ConnectionParameters(host       ='localhost',
                                                                            credentials=pika.PlainCredentials('guest', 'guest')))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='cards',
                                      type    ='direct')

        self.result = self.channel.queue_declare(exclusive=True)
        self.queue_name = self.result.queue

        self.exchange_name = 'cards'
        self.bindingKeys   = ['cards', 'deckNbr']
        for bindingKey in self.bindingKeys:
            self.channel.queue_bind(exchange   =self.exchange_name,
                                    queue      =self.queue_name,
                                    routing_key=bindingKey)

    def loop(self):
        def callback(ch, method, header, body):
            if   method.routing_key=="cards":
                message = json.loads(body)
                self.playRound(message)

            elif method.routing_key=="deckNbr":
                del self.deckL[:]

        self.channel.basic_consume(callback,
                                   queue =self.queue_name,
                                   no_ack=True)

        pika.asyncore_loop()



    def printDeck(self):
        for card in self.deckL:
            print card

    def removePile(self):
        pile = list(self.deckL)
        del self.deckL[:]
        return pile

    def addCard(self, card):
        self.deckL.append(card)

    def playRound(self, message):
        card1 = list()
        card2 = list()

        card  = message['card1']
        suit  = card['suit']
        value = card['value']
        card1 = [suit, value]
        self.addCard(card1)

        card = message['card2']
        suit = card['suit']
        value = card['value']
        card2 = [suit, value]
        self.addCard(card2)

        if (card1[0] == card2[0] or card1[1] == card2[1]) and len(card1) > 0 and len(card2) > 0:
            randomNbr = random.randint(1, 2)
            cards = pile.removePile()

            for card in cards:
                if randomNbr == 1:
                    message = {"name": "player1", "suit":card[0], "value": card[1]}
                    self.channel.basic_publish(exchange   =self.exchange_name,
                                               routing_key='pileCards',
                                               body       =json.dumps(message))
                else:
                    message = {"name": "player2", "suit":card[0], "value": card[1]}
                    self.channel.basic_publish(exchange   =self.exchange_name,
                                               routing_key='pileCards',
                                               body       =json.dumps(message))

            del cards[:]
            del card1[:]
            del card2[:]

        message = 'newRound'
        self.channel.basic_publish(exchange   ='cards',
                                   routing_key='deck',
                                   body       =message)

if __name__ == '__main__':
    pile = pileCards()
    pile.loop()


