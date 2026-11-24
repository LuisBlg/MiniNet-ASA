"""ConsoleUI : interaction utilisateur et session locale, pas de logique SQL."""
import getpass
import sys
from ..domain import DomainError

GUEST = '''\n=== MiniNet | Accueil ===
1. Créer un compte
2. Se connecter
0. Quitter'''
MEMBER = '''1. Publier un texte
2. Publier un lien
3. Publier une image
4. Consulter le fil
5. Exporter une image du fil
6. Ajouter un ami
7. Supprimer un ami
8. Mes amis
9. Annuaire
10. Envoyer un message privé
11. Mes messages privés
0. Se déconnecter'''

def read_password(prompt):
    # Entrée masquée en terminal ; lecture simple pour scripts de tests.
    return getpass.getpass(prompt) if sys.stdin.isatty() else input(prompt)

class ConsoleUI:
    def __init__(self, users, friends, posts, messages, notifications, *, read=input, write=print, password=read_password):
        self.users = users
        self.friends = friends
        self.posts = posts
        self.messages = messages
        self.notifications = notifications
        self.read, self.write, self.password = read, write, password
        self._uid = None
        self._name = None

    def run(self):
        try:
            while True:
                try:
                    if self._uid is None:
                        self.write(GUEST)
                        choice = self.read('Choix : ').strip()
                        if choice == '0':
                            break
                        if choice == '1':
                            self.users.register(self.read('Pseudo : '),self.password('Mot de passe : '))
                            self.write('Compte créé. Connectez-vous.')
                        elif choice == '2':
                            uid = self.users.authenticate(self.read('Pseudo : '),self.password('Mot de passe : '))
                            self._name = self.users.name(uid)
                            self._uid = uid
                            self.write('Connexion réussie.')
                        else:
                            self.write('Choix inconnu.')
                    else:
                        self.write(f'\n=== MiniNet | {self._name} ===')
                        for notification in self.notifications.take(self._uid):
                            self.write('[Notification] '+notification)
                        self.write(MEMBER)
                        self._member(self.read('Choix : ').strip())
                except DomainError as exc:
                    self.write(f'Erreur : {exc}')
        except (EOFError, KeyboardInterrupt):
            self.write('\nSession interrompue.')
        finally:
            self._uid = self._name = None
        self.write('Au revoir !')

    def _member(self, choice):
        uid = self._uid
        if choice == '0':
            self._uid = self._name = None
            self.write('Déconnexion réussie.')
        elif choice in ('1','2','3'):
            methods = {'1':(self.posts.publish_text,'Texte : '),'2':(self.posts.publish_link,'URL : '),'3':(self.posts.publish_image,'Chemin image : ')}
            method, prompt = methods[choice]
            self.write(f'Publication #{method(uid,self.read(prompt))} créée.')
        elif choice == '4':
            rows = self.posts.feed(uid)
            self.write('--- Fil : vos publications et celles de vos amis ---')
            for post in rows:
                self.write(f'#{post.id} | {post.created} UTC | {post.author} | {post.kind} : {post.content}')
            if not rows:
                self.write('Aucune publication.')
        elif choice == '5':
            raw = self.read('Identifiant de publication : ').strip()
            if not raw.isascii() or not raw.isdecimal() or len(raw)>18 or int(raw)==0:
                raise DomainError('Identifiant numérique positif attendu.')
            self.posts.export_image(uid,int(raw),self.read('Nouveau chemin de sortie : '))
            self.write('Image exportée.')
        elif choice in ('6','7'):
            method = self.friends.add if choice=='6' else self.friends.remove
            method(uid,self.read('Pseudo : '))
            self.write('Ami ajouté.' if choice=='6' else 'Ami supprimé.')
        elif choice in ('8','9'):
            names = self.friends.list(uid) if choice=='8' else self.users.list_users(uid)
            self.write(', '.join(names) if names else 'Liste vide.')
        elif choice=='10':
            mid = self.messages.send(uid,self.read('Destinataire : '),self.read('Message : '))
            self.write(f'Message privé #{mid} envoyé.')
        elif choice=='11':
            rows = self.messages.history(uid)
            self.write('--- Messages envoyés et reçus ---')
            for msg in rows:
                self.write(f'#{msg.id} | {msg.created} UTC | {msg.sender} -> {msg.recipient} : {msg.body}')
            if not rows:
                self.write('Aucun message.')
        else:
            self.write('Choix inconnu.')
