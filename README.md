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
```

## Suuri tietomäärä

Ajamalla tiedoston `seed.py` voi testata sovelluksen toimintaa suurella tietomäärällä. Testiaineisto sisältää:

* Tuhat käyttäjää
* Miljoona kirjakerhoa, jolla kullakin on 0-5 genreä ja yksi neljästä viimeisestä osallistumispäivämäärästä, joista osa on menneitä päivämääriä ja osa tulevia päivämääriä (olettaen, että testaus tehdään 13.12.2025 ja 30.12.2025 välillä)
* Kymmenen miljoona kirjan arvostelua, jotka sisältävät 1-5 tähteä ja joista joka toista on "muokattu", eli muokkausaika näkyy arvostelussa
* Kullekin kirjakerholle on arvottu käyttäjä ja kullekin arvostelulle on arvottu kirjakerho ja käyttäjä

Sovelluksessa on 4 pääkohdetta, joissa suuri tietomäärä vaikuttaa nopeuteen. Näitä ovat:

* Etusivu, joka näyttää kaikki kirjakerhot uusimmasta vanhimpaan
* Kirjakerhon sivu, joka näyttää kirjan arvostelut
* Käyttäjäsivu, joka näyttää käyttäjän luomat kirjakerhot ja kirjoittamat arvostelut
* Haku, joka näyttää hakutulokset, joita voi potentiaalisesti olla suuri määrä

Kullekin näistä on tehty sivutus, jossa sivut toimivat tehokkaasti. Etusivulla ja haussa kullakin sivulla näkyy korkeintaan kymmenen kirjakerhoa. Kirjakerhon sivulla näkyy viisi uusinta arvostelua, ja linkillä on mahdollista siirtyä katsomaan kaikkia kirjan saamia arvosteluja, jolloin arvosteluja on kymmenen sivua kohti. Käyttäjäsivulla näkyy myös viisi käyttäjän uusinta kirjakerhoa ja arvostelua, ja kirjakerhon arvostelujen tapaan voi siirtyä erilliselle sivulle, jossa kaikki kirjakerhot/arvostelut näkyvät kymmenen kappaletta kerrallaan.

Sivutuksen lisäksi tietokantaan on luotu neljä nopeuttavaa indeksiä. Tauluun `bookclubs` on luotu indeksi käyttäjille, tauluun `reviews` on luotu indeksi sekä käyttäjille että kirjakerhoille, ja tauluun `club_classes` on luotu indeksi kirjakerhoille.

### Aikatestaus

Testasin sivujen latausaikoja.

|                        | sivu 1 | sivu 3 | sivu n/2 | sivu n-1 | sivu n |
| ---------------------- | ------ | ------ | -------- | -------- | ------ |
| etusivu                | 0.09 s | 0.08 s | 0.3 s    | 0.52 s   | 0.53 s |
| kirjakerho             | 1.01 s | -      | -        | -        | -      |
| kirjakerhon arvostelut | 1.24 s | -      | -        | -        | -      |
| käyttäjä               | 0.86 s | -      | -        | -        | -      |
| käyttäjän arvostelut   | 0.79 s | 0.76 s | 1.23 s   | 1.55 s   | 1.55 s |
| käyttäjän kirjakerhot  | 0.09 s | 0.09 s | 0.12 s   | 0.15 s   | 0.17 s |
| haku *                 | 0.12 s | 0.12 s | 0.15 s   | 0.23 s   | 0.25 s |
| haku **                | 0.15 s | 0.17 s | 0.33 s   | 0.49 s   | 0.49 s |

\* kun hakusana tuotti 280 tulosta <br>
\*\* kun hakusana tuotti miljoona tulosta

Valtaosin ajat ovat kohtuullisia, etenkin suhteessa tietomäärään. Käyttäjän lähettämien arvostelujen etsiminen on kaikista hitainta, sillä arvosteluja on yhteensä kymmenen miljoonaa.
