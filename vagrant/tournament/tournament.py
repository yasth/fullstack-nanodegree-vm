#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""DELETE FROM match;""")
    cur.execute("""COMMIT""") #end tran

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""DELETE FROM player;""")
    cur.execute("""COMMIT""") #end tran

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""SELECT COUNT(player.id) FROM player;""") #fetch singleton computed value
    return cur.fetchone()[0]

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("""INSERT INTO player (name) VALUES (%s);""",(name,))
    cur.execute("""COMMIT""") #end tran

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("""SELECT id,name,wins,matches FROM PlayerStandings;""")
    return cur.fetchall() #should be in the right format so just send wholesale

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("""INSERT INTO match (winningPlayer,losingPlayer) VALUES (%s,%s);""",(winner,loser))
    cur.execute("""COMMIT""") #end tran
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    ret = [] #list to be returned
    rankings = playerStandings() #fetch sorted list of player standings (with OMV sorting)
    if(len(rankings)%2<>0):
       raise ValueError("Odd number of players") # Can't pair odd number of players'
    for key in range(0,len(rankings),2): #step by two as we consume two per go
       ret.append([rankings[key][0],rankings[key][1],rankings[key+1][0],rankings[key+1][1]])
    return ret
