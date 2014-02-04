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

import pile
import pika
import json


class table(object):
    player1 = list()
    player2 = list()

    def __init__(self):
        print 'Press Ctrl^C to end program'

        self.connection = pika.AsyncoreConnection(pika.ConnectionParameters(host       ='localhost',
                                                                            credentials=pika.PlainCredentials('guest', 'guest')))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='cards',
                                      type    ='direct')

        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.queue

        exchange_name = 'cards'
        bindingKeys   = ['game']
        for bindingKey in bindingKeys:
            self.channel.queue_bind(exchange   =exchange_name,
                                    queue      =self.queue_name,
                                    routing_key=bindingKey)

        self.startNewGame()

    def startNewGame(self):
        try:
            deckNbr = int(raw_input('How many decks for this game? '))
        except ValueError:
            print "Not a number"

        message = {"deckNbr": deckNbr}
        self.channel.basic_publish(exchange   ='cards',
                                   routing_key='deckNbr',
                                   body       =json.dumps(message))

        message = 'newRound'
        self.channel.basic_publish(exchange   ='cards',
                                   routing_key='deck',
                                   body       =message)

    def loop(self):
        def callback(ch, method, header, body):
            message = json.loads(body)
            player         = message['player']
            cardsRemaining = message['cardsRemaining']

            if   player=="player1":
                self.player1 = [player, cardsRemaining]
            elif player=="player2":
                self.player2 = [player, cardsRemaining]

            if len(self.player1) > 0 and len(self.player2) > 0:
                print 'Player 1 cards: '
                print self.player1[1]
                print 'Player 2 cards: '
                print self.player2[1]

                if   self.player1[1] > self.player2[1]:
                    print self.player1[0] +" wins!"
                elif self.player1[1] < self.player2[1]:
                    print self.player2[0] +" wins!"
                else:
                    print "Both win!"

                del self.player1[:]
                del self.player2[:]
                self.startNewGame()


        self.channel.basic_consume(callback,
                                   queue =self.queue_name,
                                   no_ack=True)

        pika.asyncore_loop()


if __name__ == '__main__':
    table = table()
    table.loop()



