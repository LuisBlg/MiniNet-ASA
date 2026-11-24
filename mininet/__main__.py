import argparse
import sqlite3
import sys
from pathlib import Path
from .assembly import assemble

DEMO_PASSWORD = 'Demo2026!'

def seed(app):
    ui = app.console
    alice = ui.users.register('alice',DEMO_PASSWORD)
    bob = ui.users.register('bob',DEMO_PASSWORD)
    clara = ui.users.register('clara',DEMO_PASSWORD)
    ui.friends.add(alice,'bob')
    ui.posts.publish_text(bob,'Bonjour Alice !')
    ui.posts.publish_link(bob,'https://www.univ-nantes.fr/')
    ui.posts.publish_text(clara,'Publication hors du cercle d’amis.')
    ui.messages.send(bob,'alice','Salut, on révise ASA ?')

def main(argv=None):
    parser = argparse.ArgumentParser(description='MiniNet : réseau social local en console')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--db',type=Path,default=Path('mininet.db'),help='fichier SQLite (défaut : mininet.db)')
    group.add_argument('--demo',action='store_true',help='jeu de données de démonstration en mémoire, sans toucher à la base')
    args = parser.parse_args(argv)
    try:
        with assemble(':memory:' if args.demo else args.db) as app:
            if args.demo:
                seed(app)
                print('Mode démo : alice / bob / clara, mot de passe commun : '+DEMO_PASSWORD)
                print('Les données de cette session ne seront pas conservées.')
            app.console.run()
    except sqlite3.Error:
        print('Erreur SQLite : base inaccessible ou opération impossible.',file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
