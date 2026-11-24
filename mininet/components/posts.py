"""PostManager : validation et accès aux publications."""
from pathlib import Path
from ..domain import DomainError, text, link

MAX_IMAGE = 2 * 1024 * 1024

class PostManager:
    def __init__(self, store):
        self.store = store

    def publish_text(self, uid, value):
        return self.store.create_post(uid,'text',text(value,'Publication',280),None)

    def publish_link(self, uid, value):
        return self.store.create_post(uid,'link',link(value),None)

    def publish_image(self, uid, filename):
        path = Path(filename).expanduser()
        try:
            if not path.is_file():
                raise DomainError('Fichier image introuvable.')
            with path.open('rb') as f:
                data = f.read(MAX_IMAGE+1)
        except (OSError, ValueError, RuntimeError) as exc:
            raise DomainError('Impossible de lire le fichier image.') from exc
        if len(data)>MAX_IMAGE:
            raise DomainError('Image trop volumineuse (2 Mio maximum).')
        # Reconnaissance légère du format, pas un décodeur ni un antivirus.
        if not (data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8\xff') or data.startswith((b'GIF87a',b'GIF89a')) or (data[:4]==b'RIFF' and data[8:12]==b'WEBP')):
            raise DomainError('Image PNG, JPEG, GIF ou WebP attendue.')
        return self.store.create_post(uid,'image',text(path.name,'Nom du fichier',255),data)

    def feed(self, uid):
        return self.store.feed(uid)

    def export_image(self, uid, post_id, destination):
        data = self.store.image(uid, post_id)
        created = False
        try:
            path = Path(destination).expanduser()
            with path.open('xb') as f:
                created = True
                f.write(data)
        except (OSError, ValueError, RuntimeError) as exc:
            if created:
                try:
                    path.unlink()
                except OSError:
                    pass  # Le système de fichiers peut empêcher le nettoyage.
            raise DomainError('Export impossible (chemin invalide, fichier existant ou erreur d’écriture).') from exc
