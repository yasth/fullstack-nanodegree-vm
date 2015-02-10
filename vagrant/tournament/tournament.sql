
create database if not exists tournament; --make new db
\c tournament 
create table if not exists "player" (
"id" serial primary key,
"name" varchar (40) NOT NULL
);
create table if not exists "match" ( --match references losing and winning
"id" serial primary key,
"losingplayer" int REFERENCES player(id),
"winningplayer" int REFERENCES player(id)
	);
drop view if exists PlayerStandings;
create view PlayerStandings --view sorted by wins and OMV wins
AS
SELECT player.id, player.name, count(wins.id) as wins, count(losses.id) as losses, count(wins.id) + count(losses.id) as matches
from player left join
match AS wins ON player.id = wins.winningPlayer LEFT JOIN
match as losses ON player.id = losses.losingPlayer LEFT JOIN
(SELECT p.id, count(otherWins.id)
FROM player AS p inner join match AS m ON p.id = m.winningplayer 
inner join match AS otherWins ON otherWins.winningPlayer = m.losingPlayer GROUP BY p.id) 
AS OMV ON OMV.id= player.id
GROUP BY player.id, player.name
ORDER BY count(wins.id) DESC, count(OMV.id) DESC;
