# LING 131 Group Project: Play Generation

## How to run

Ensure all packages in `requirements.txt` are installed. This can be done by running:
```
pip3 install -r requirements.txt
```

Running `python3 generator/main.py [SOURCE PLAY]` prints a generated play to standard output. The optional flag `--chartag` specifies which tag is used in the source html to specify a character, and `--stagetag` specifies the tag used for stage directions.

To save a generated play based on "A Doll's House" as "doll_play.txt" for example, run:
```
python3 generator/main.py source_plays/a_dolls_house.htm > doll_play.txt
```

To save a generated play based on "Hamlet" as "hamlet_play.txt", run:
```
python3 generator/main.py source_plays/hamlet.htm --chartag=charname --stagetag=scenedesc > hamlet_play.txt
```

## Division of Labor

Play parsing and structure: Deanna

Grammar: Lizzie

Vocabulary: Hayley

## Project Report

[Click here to view](https://docs.google.com/document/d/1LeaXm6ymA_7cPBXukxjhKDm9kpGTf4uZfwmnoyQsoeU/edit?usp=sharing)
