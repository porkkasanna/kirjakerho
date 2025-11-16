# Kirjakerho

## Sovelluksen toiminnot

* käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
* käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ilmoituksia kirjakerhoista
* käyttäjä näkee muiden luomat ilmoitukset
* käyttäjä pystyy etsimään ilmoituksia hakusanalla

## Sovelluksen asennus

Asenna `flask`-kirjasto:
```
$ pip install flask
```
Luo tietokannan taulut:
```
$ sqlite3 database.db < schema.sql
```
Käynnistä sovellus seuraavasti:

```
$ flask run
