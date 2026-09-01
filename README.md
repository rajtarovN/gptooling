# GraphGen DSL

Domensko-specifičan jezik (DSL) za deklarativno definisanje šeme podataka i generisanje velikih, konfigurabilnih skupova test podataka za tri različita tipa baza podataka: Neo4j (graf baza), PostgreSQL (relaciona baza) i MongoDB (dokument baza).

# Ključne mogućnosti

Deklarativan opis šeme podataka: tipovi entiteta (node), veze između entiteta (edge), tipovi property-ja (int, float, string, enum, bool, datetime), kardinalnost, i strukturna ograničenja (acikličnost, zabrana samo-referenciranja).
Kontrola parametara generisanja: ukupna veličina skupa podataka, procentualna raspodela po tipovima entiteta, i način deljenja referenci između entiteta (Shared / NotShared).
Semantička validacija modela pre generisanja (npr. provera da li procenti sabiraju na 100%, da li su ograničenja kardinalnosti izvodljiva).
Generisanje podataka u streaming režimu (batch po batch), pogodno za skaliranje na velike količine podataka (100.000+) bez prekomerne potrošnje memorije.
Izvoz istog generisanog skupa podataka u tri različita formata upita (Cypher za Neo4j, SQL za PostgreSQL, JSON dokumenti za MongoDB), iz jedinstvenog, baza-agnostičkog internog modela.
Opcija direktnog izvršavanja generisanih upita nad pravom instancom ciljne baze, ili čuvanje upita u fajl za kasnije pokretanje.

# Struktura projekta

```
project:
  grammar:
    graphGenBase.tx       # textX gramatika jezika
  model:
    classes.py            # Python klase koje odgovaraju pravilima gramatike
  interpreter:
    validator.py          # semantička validacija modela
    generat_data.py       # generisanje konkretnih podataka (in-memory i streaming)
  export:
    neo4j_exporter.py     # izvoz u Cypher upite / izvršavanje nad Neo4j
    postgres_exporter.py  # izvoz u SQL upite / izvršavanje nad PostgreSQL
    mongo_exporter.py     # izvoz u JSON dokumente / izvršavanje nad MongoDB
  examples:
    example1.gg           # primer ulaznog fajla u definisanom jeziku
  output:                   # generisani fajlovi sa upitima (Cypher/SQL/JSON)
   cli.py                    # ulazna tačka, povezuje sve module u jedan proces
Instalacija
```

# Projekat zahteva Python 3.9+ i sledeće pakete:

bash
pip install textx exrex neo4j psycopg2-binary pymongo
# (preporuka koristiti virtuelno okruzenje)
# (takodje u exporterima i cli fajlu su komentari za iste biblioteke)

Za testiranje generisanih podataka nad pravim bazama, potrebna je pokrenuta instanca odgovarajuće baze:

Neo4j: lokalna instalacija ili Docker kontejner, podrazumevani port 7687
PostgreSQL: lokalna instalacija, podrazumevani port 5432
MongoDB: lokalna instalacija ili Docker kontejner, podrazumevani port 27017

# CLI fajl 17. linija, tu se nalaze podaci za baze i mozda je potrebno prilagoditi njih lokalnim bazama ili baze tim podacima. Lokalno slobodno menjati.

Ako ne planiraš direktno izvršavanje upita, ovaj korak nije neophodan. Generisani upiti se mogu sačuvati u fajl i pokrenuti kasnije, ili nad posebno pripremljenom instancom baze.
# timings = export_for_targets(model, model.spec.targets) prilikom poyiva funkcije u cli.py potrebno je dodati argument za upis u fajl. Polje je po defoltu false, pa ga treba staviti na true. Paziti i na polje za upis u bazu.

# Sintaksa jezika

Ulazni .gg fajl sastoji se iz dva glavna bloka:

schema: - opis strukture podataka
schema:
    node User:
        properties:
            name: string(pattern="user_{id}")
            active: bool

    node Namespace:
        properties:
            quota: int(range=1..100)

    edge OWNS:
        from User to Namespace
        cardinality: 1..3
        constraint: no_self_loop
generate: - opis parametara generisanja
generate:
    GENERATE 100
    FOR MongoDB
    WHERE 40% User, 60% Namespace
    USE OWNS: Shared
GENERATE: ukupna količina podataka koja se generiše.
FOR: ciljne baze podataka za koje se generišu upiti.
WHERE: procentualna raspodela ukupne količine podataka po tipovima entiteta (mora sabirati na 100%).
USE: način deljenja referenci po tipu veze: Shared (više entiteta može referencirati isti ciljni entitet) ili NotShared (svaki ciljni entitet se koristi najviše jednom).

Pokretanje generisanja
bash
python cli.py 

Svi generisani podaci potiču iz istog internog modela, što znači da je moguće generisati ekvivalentne skupove podataka za sve tri baze iz jednog .gg fajla, radi direktnog poređenja performansi različitih paradigmi skladištenja podataka.
