# Kirjakerho

## Sovelluksen toiminnot

* käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
* käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ilmoituksia kirjakerhoista
* käyttäjä pystyy luokitella kirjakerhon kirjan genret
* käyttäjä näkee muiden luomat ilmoitukset
* käyttäjä pystyy antamaan arvosteluja kirjakerhojen kirjoille
* käyttäjä pystyy etsimään ilmoituksia hakusanalla
* käyttäjä pystyy etsimään ilmoituksia genren perusteella (ei vielä toiminnassa)
* kullekin käyttäjälle on käyttäjäsivut, josta löytyy mm. käyttäjän omat kirjakerhot ja arvostelut

## Tekijänoikeudet

Sovelluksessa on valmiita profiilikuvia, jotka ovat tekijänoikeudettomia (public domain). Kuvat on haettu sivulta:
https://pdimagearchive.org/

## Sovelluksen asennus

Asenna `flask`-kirjasto:
```
$ pip install flask
```
Luo tietokannan taulut:
```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```
Käynnistä sovellus seuraavasti:

```
$ flask run
