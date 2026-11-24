"""Composant Storage : seul propriétaire de SQLite et du SQL."""
import sqlite3
from ..domain import DomainError, Post, Message

SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, password TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS friends (
 a INTEGER NOT NULL REFERENCES users(id), b INTEGER NOT NULL REFERENCES users(id),
 PRIMARY KEY(a,b), CHECK(a<b));
CREATE TABLE IF NOT EXISTS posts (
 id INTEGER PRIMARY KEY, author INTEGER NOT NULL REFERENCES users(id),
 kind TEXT NOT NULL CHECK(kind IN ('text','link','image')), content TEXT NOT NULL,
 image BLOB, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CHECK((kind='image' AND image IS NOT NULL) OR (kind<>'image' AND image IS NULL)));
CREATE TABLE IF NOT EXISTS messages (
 id INTEGER PRIMARY KEY, sender INTEGER NOT NULL REFERENCES users(id),
 recipient INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL,
 created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, CHECK(sender<>recipient));
CREATE INDEX IF NOT EXISTS posts_author ON posts(author,id);
CREATE INDEX IF NOT EXISTS friends_b ON friends(b,a);
CREATE INDEX IF NOT EXISTS messages_recipient ON messages(recipient,id);
CREATE INDEX IF NOT EXISTS messages_sender ON messages(sender,id);
'''

class Storage:
    def __init__(self, path):
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        try:
            self._db.execute('PRAGMA foreign_keys=ON')
            self._db.executescript(SCHEMA)
        except BaseException:
            self._db.close()
            raise

    def close(self):
        self._db.close()

    def create_user(self, name, password):
        try:
            with self._db:
                return self._db.execute('INSERT INTO users(name,password) VALUES (?,?)', (name,password)).lastrowid
        except sqlite3.IntegrityError as exc:
            raise DomainError('Ce pseudo existe déjà.') from exc

    def credentials(self, name):
        row = self._db.execute('SELECT id,password FROM users WHERE name=?', (name,)).fetchone()
        return (row['id'],row['password']) if row else None

    def user_id(self, name):
        row = self._db.execute('SELECT id FROM users WHERE name=?', (name,)).fetchone()
        if not row:
            raise DomainError('Utilisateur inconnu.')
        return row['id']

    def user_name(self, uid):
        row = self._db.execute('SELECT name FROM users WHERE id=?', (uid,)).fetchone()
        if not row:
            raise DomainError('Utilisateur inconnu.')
        return row['name']

    def list_users(self, uid):
        return [r[0] for r in self._db.execute('SELECT name FROM users WHERE id<>? ORDER BY name', (uid,))]

    def add_friend(self, uid, other):
        a,b = sorted((uid,other))
        try:
            with self._db:
                self._db.execute('INSERT INTO friends(a,b) VALUES (?,?)', (a,b))
        except sqlite3.IntegrityError as exc:
            raise DomainError('Cette amitié existe déjà.') from exc

    def remove_friend(self, uid, other):
        with self._db:
            if not self._db.execute('DELETE FROM friends WHERE a=? AND b=?', tuple(sorted((uid,other)))).rowcount:
                raise DomainError('Cette amitié n’existe pas.')

    def list_friends(self, uid):
        return [r[0] for r in self._db.execute('''SELECT u.name FROM friends f JOIN users u
            ON u.id=CASE WHEN f.a=? THEN f.b ELSE f.a END
            WHERE f.a=? OR f.b=? ORDER BY u.name''', (uid,uid,uid))]

    def create_post(self, uid, kind, content, image):
        with self._db:
            return self._db.execute('INSERT INTO posts(author,kind,content,image) VALUES (?,?,?,?)', (uid,kind,content,image)).lastrowid

    # Même prédicat pour le fil et l'export : aucune fuite par identifiant.
    _VISIBLE = '''(p.author=? OR EXISTS(SELECT 1 FROM friends f
        WHERE (f.a=? AND f.b=p.author) OR (f.b=? AND f.a=p.author)))'''

    def feed(self, uid):
        rows = self._db.execute('''SELECT p.id,u.name AS author,p.kind,p.content,p.created
            FROM posts p JOIN users u ON u.id=p.author WHERE '''+self._VISIBLE+' ORDER BY p.id DESC', (uid,uid,uid))
        return [Post(**dict(r)) for r in rows]

    def image(self, uid, post_id):
        row = self._db.execute('SELECT p.image FROM posts p WHERE p.id=? AND p.kind=\'image\' AND '+self._VISIBLE, (post_id,uid,uid,uid)).fetchone()
        if not row:
            raise DomainError('Image introuvable ou inaccessible.')
        return row[0]

    def create_message(self, sender, recipient, body):
        with self._db:
            return self._db.execute('INSERT INTO messages(sender,recipient,body) VALUES (?,?,?)', (sender,recipient,body)).lastrowid

    def messages(self, uid):
        rows = self._db.execute('''SELECT m.id,s.name AS sender,r.name AS recipient,m.body,m.created
            FROM messages m JOIN users s ON s.id=m.sender JOIN users r ON r.id=m.recipient
            WHERE m.sender=? OR m.recipient=? ORDER BY m.id DESC''', (uid,uid))
        return [Message(**dict(r)) for r in rows]
