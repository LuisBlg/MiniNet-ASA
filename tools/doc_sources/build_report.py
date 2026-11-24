from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape
from PIL import Image
R=Path(__file__).resolve().parents[2]; D=R/'docs'
for n,f in [('DS','DejaVuSans.ttf'),('DSB','DejaVuSans-Bold.ttf'),('DM','DejaVuSansMono.ttf')]: pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('DS',normal='DS',bold='DSB',italic='DS',boldItalic='DSB')
W,H=A4; M=48; CW=W-2*M
navy=HexColor('#17394D'); teal=HexColor('#216D79'); ink=HexColor('#243746'); muted=HexColor('#536776'); pale=HexColor('#E7F1F4'); gray=HexColor('#F3F5F6'); gold=HexColor('#A66E18')
c=canvas.Canvas(str(D/'Rapport_architecture.pdf'),pagesize=A4); c.setTitle('MiniNet — Rapport d’architecture'); c.setAuthor('Binôme ALMA M2')
styles={
 'body':ParagraphStyle('body',fontName='DS',fontSize=10.2,leading=15,textColor=ink,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='DS',fontSize=8.4,leading=12,textColor=muted),
 'cell':ParagraphStyle('cell',fontName='DS',fontSize=8.4,leading=11.6,textColor=ink),
 'head':ParagraphStyle('head',fontName='DSB',fontSize=8.4,leading=11.6,textColor=white),
 'code':ParagraphStyle('code',fontName='DM',fontSize=8.5,leading=13,textColor=navy),
}
page=0;y=0

def start(num,title,sub):
 global page,y
 page=num; c.setFillColor(teal); c.rect(0,H-8,W,8,fill=1,stroke=0)
 c.setFont('DSB',9); c.setFillColor(teal); c.drawString(M,H-37,'MININET  /  ASA  ·  ALMA M2 2026–2027')
 c.setFillColor(navy); c.setFont('DSB',23); c.drawString(M,H-78,title)
 y=H-94; para(sub,'small',12); y-=4

def para(s,style='body',after=8):
 global y
 p=Paragraph(s,styles[style]); _,h=p.wrap(CW,700); p.drawOn(c,M,y-h); y-=h+after

def head(s):
 global y
 y-=7;c.setFont('DSB',12); c.setFillColor(teal); c.drawString(M,y-12,s); y-=21

def table(headers,rows,widths):
 global y
 data=[[Paragraph(escape(str(x)),styles['head']) for x in headers]]+[[Paragraph(escape(str(x)),styles['cell']) for x in row] for row in rows]
 t=Table(data,colWidths=[CW*w for w in widths]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('ROWBACKGROUNDS',(0,1),(-1,-1),[gray,white]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,-1),(-1,-1),0.5,HexColor('#B7C5CC'))])); _,h=t.wrap(CW,700);t.drawOn(c,M,y-h);y-=h+12

def code(lines):
 global y
 h=16+13*len(lines);c.setFillColor(gray);c.roundRect(M,y-h,CW,h,5,fill=1,stroke=0);c.setFont('DM',8.3);c.setFillColor(navy)
 for i,line in enumerate(lines):c.drawString(M+10,y-14-13*i,line)
 y-=h+12

def diagram(path):
 global y
 im=Image.open(path); ratio=im.height/im.width; h=CW*ratio;c.drawImage(str(path),M,y-h,CW,h,mask='auto');y-=h+8

def end():
 assert y>49,(page,y)
 c.setStrokeColor(HexColor('#CCD7DC'));c.line(M,42,W-M,42);c.setFont('DS',8);c.setFillColor(muted);c.drawString(M,26,'Rapport d’architecture  •  MiniNet');c.drawRightString(W-M,26,f'{page} / 9');c.showPage()

start(1,'MiniNet','Rapport d’architecture logicielle — Architecture à base de composants et connecteurs (C&C)')
para('<b>Master 2 Informatique – parcours ALMA</b><br/>Université de Nantes · année universitaire 2026–2027<br/>Binôme : ........................................ / ........................................',after=20)
head('Résumé')
para('MiniNet est un prototype de réseau social local, utilisable en console. Il couvre les cinq exigences du sujet : comptes, publications, fil des contacts, messages privés et gestion des amis. Le projet privilégie la séparation des responsabilités et la description explicite des interactions plutôt que la sophistication de l’interface.')
para('L’architecture retient sept composants et dix connecteurs : neuf appels de procédure synchrones et un bus publish/subscribe synchrone. Le modèle d’assemblage définit les ports et les opérations ; il est utilisé à l’exécution et sert à générer la spécification ACME et la matrice de traçabilité. Le stockage SQLite conserve les données métier entre deux exécutions.')
head('Organisation du rapport')
table(['Page','Contenu'],[(2,'Exigences et règles fonctionnelles'),(3,'Vue C&C et choix du style'),(4,'Composants et responsabilités'),(5,'Connecteurs, ports et contrats'),(6,'Description ACME et traçabilité'),(7,'Scénario de communication et comportement'),(8,'Données, sûreté et compromis'),(9,'Validation, exécution et limites')],[.15,.85])
para('Périmètre : prototype pédagogique mono-processus, sans serveur, sans réseau et sans dépendance Python tierce. Le bus d’événements constitue l’extension facultative retenue.','small')
end()
start(2,'Exigences et périmètre','Du cahier des charges aux comportements observables.')
table(['ID','Exigence du sujet','Comportement retenu'],[
 ('F1','Inscription et authentification','Pseudo unique, mot de passe dérivé, session console ; inscription puis connexion.'),('F2','Publier un message court','Texte ≤ 280 caractères ; lien HTTP(S) ; image locale ≤ 2 Mio, octets conservés.'),('F3','Consulter les publications des contacts','Fil des amis actuels et de soi-même, du plus récent au plus ancien (ordre des identifiants).'),('F4','Envoyer et recevoir des messages privés','Envoi à un compte existant ; historique filtré par émetteur ou destinataire.'),('F5','Ajouter et supprimer des amis','Amitié symétrique immédiate ; pas de demande à accepter. Liste et annuaire.'),('E1','Extension choisie : publish/subscribe','Événement MessageSent, notification ciblée, visible au prochain menu du destinataire.')],[.10,.32,.58])
head('Règles et décisions fonctionnelles')
para('L’amitié est réciproque et ne peut relier un utilisateur à lui-même. Supprimer une relation retire immédiatement les posts de l’ancien ami du fil ; cela ne supprime pas les messages privés déjà échangés. Les messages sont autorisés entre tous les comptes existants, sans condition d’amitié. Ces règles sont des décisions de conception, non des contraintes ajoutées par le sujet.')
para('Une image est représentée par son nom et son identifiant dans la console. L’utilisateur peut exporter les octets d’une publication qu’il est autorisé à consulter. Le lien est conservé sous forme de texte et n’est jamais ouvert automatiquement.')
head('Exigences non fonctionnelles')
para('<b>N1 – Modularité :</b> responsabilité unique, accès par ports et assemblage centralisé.<br/><b>N2 – Traçabilité :</b> noms identiques entre le code et l’ADL, vérification automatisée.<br/><b>N3 – Portabilité :</b> Python 3.10+, SQLite, lancement sans installation de paquets.<br/><b>N4 – Confidentialité logique :</b> identité issue de la session ; filtrage en lecture.')
end()
start(3,'Vue composants et connecteurs','Architecture locale : composants métier indépendants et interactions explicites.')
diagram(R/'architecture/composants.png')
para('Figure 1 — Rectangles bleus : composants. Ellipses grises : connecteurs d’appel (sens de la requête ; résultat retourné en sens inverse). Ellipse ocre et traits discontinus : diffusion d’événement. Les ports et les rôles détaillés figurent pages 5–6 et dans MiniNet.acme.','small')
head('Un monolithe modulaire, deux styles d’interaction')
para('Tous les composants s’exécutent dans un seul processus Python. ConsoleUI joue le rôle de client des services métier. Storage centralise la persistance : aucune autre classe ne manipule SQLite. La vue décrit les interactions à l’exécution, pas simplement une arborescence de fichiers.')
para('Les appels synchrones conviennent aux opérations qui nécessitent une réponse immédiate : authentification, affichage du fil, écriture en base. Le bus publish/subscribe est réservé à la notification d’un message : le service producteur ignore les abonnés. Les deux styles coexistent sans introduire de transport réseau.')
head('Frontière du système')
para('Le terminal et l’utilisateur sont extérieurs à la vue C&C. SQLite est une technologie interne de Storage ; le fichier de base est une ressource, pas un service distant. Le modèle et la racine de composition servent à construire le système et ne sont pas des composants métier actifs.')
end()
start(4,'Responsabilités des composants','Une classe concrète par composant ; des données partagées sans dépendance vers les services.')
table(['Composant / module','Responsabilité','Ports fournis / requis'],[
 ('ConsoleUI / console.py','Menus, session locale, erreurs et affichage.','Requis : users, friends, posts, messages, notifications.'),('UserManager / users.py','Inscription, contrôle du mot de passe, annuaire.','Fourni : api ; requis : store.'),('FriendManager / friends.py','Règles d’amitié : résolution, ajout, retrait, liste.','Fourni : api ; requis : store.'),('PostManager / posts.py','Validation des contenus, fil, lecture/export des images.','Fourni : api ; requis : store.'),('MessageService / messages.py','Validation et stockage du message ; publication de l’événement.','Fourni : api ; requis : store, events.'),('NotificationService / notifications.py','Abonnement, tampon par destinataire et consommation.','Fournis : api, on_message.'),('Storage / storage.py','Requêtes SQL, schéma, transactions, contrôle de visibilité en lecture.','Fournis : users_api, friends_api, posts_api, messages_api.')],[.28,.40,.32])
head('Dépendances et encapsulation')
para('Les composants reçoivent leurs ports requis par injection de constructeur. Ils n’importent pas les autres composants ; les types de données (Post, Message, MessageSent) et DomainError sont partagés dans domain.py. Les ports fournis sont des ensembles nommés de méthodes, matérialisés par les opérations autorisées sur chaque ProcedureCall ; ils ne sont pas des classes Python séparées.')
para('L’accès aux fichiers image est local au PostManager ; la lecture/écriture SQLite reste exclusivement dans Storage. Les erreurs métier sont propagées jusqu’à ConsoleUI, qui les affiche sans interrompre la session.')
end()
start(5,'Connecteurs et contrats','Les connecteurs sont des objets distincts de leurs participants.')
table(['Connecteur','Caller → callee','Opérations exposées'],[
 ('ui_users','ConsoleUI.users → UserManager.api','register, authenticate, list_users, name'),('ui_friends','ConsoleUI.friends → FriendManager.api','add, remove, list'),('ui_posts','ConsoleUI.posts → PostManager.api','publish_text, publish_link, publish_image, feed, export_image'),('ui_messages','ConsoleUI.messages → MessageService.api','send, history'),('ui_notifications','ConsoleUI.notifications → NotificationService.api','take'),('user_store','UserManager.store → Storage.users_api','create_user, credentials, list_users, user_name'),('friend_store','FriendManager.store → Storage.friends_api','user_id, add_friend, remove_friend, list_friends'),('post_store','PostManager.store → Storage.posts_api','create_post, feed, image'),('message_store','MessageService.store → Storage.messages_api','user_id, user_name, create_message, messages'),('message_bus','MessageService.events → NotificationService.on_message','publish(MessageSent) ; callback on_message')],[.22,.39,.39])
head('Sémantique des interactions')
para('ProcedureCall vérifie à l’assemblage que les opérations existent chez le fournisseur et relaie uniquement les opérations déclarées (rôle caller vers callee). Le bus accepte un événement MessageSent immuable et invoque les abonnés enregistrés ; le retour est synchrone. PublisherPort ne présente que publish. L’abonné expose on_message et n’a pas besoin d’une référence vers l’émetteur.')
para('Un appel de procédure propage son résultat ou son exception ; le bus ne stocke pas les événements, ne les rejoue pas et ne garantit pas leur livraison après redémarrage.','small')
end()
start(6,'ACME et traçabilité','Une configuration déclarative relie modèle, documentation et assemblage réel.')
para('ACME décrit la structure du système par des composants, ports, connecteurs, rôles et attaches. La spécification complète se trouve dans architecture/MiniNet.acme. Extrait ciblé sur le lien d’envoi de messages (les autres déclarations sont omises ici) :')
code(['Component ConsoleUI = { Port messages; };','Component MessageService = { Port api; };','Connector ui_messages = { Role caller; Role callee; };','Attachments {','  ConsoleUI.messages to ui_messages.caller;','  MessageService.api to ui_messages.callee;','}'])
head('Correspondance entre architecture et exécution')
table(['Élément','Implémentation'],[('Component MessageService','components/messages.py : classe MessageService'),('Port ConsoleUI.messages','Paramètre du constructeur et attribut messages'),('Port MessageService.api','Contrat d’opérations (send, history) dans CALLS'),('Connector ui_messages','Instance ProcedureCall créée dans assemble()'),('Attachment caller','Injection kwargs[call.required] dans ConsoleUI'),('Attachment callee','Référence au fournisseur dans ProcedureCall'),('message_bus','MessageBus + PublisherPort ; abonnement on_message')],[.43,.57])
head('Source de vérité et vérification')
para('architecture.py déclare les composants, les liaisons et les opérations. assembly.py instancie les composants dans l’ordre des dépendances et injecte les connecteurs. tools/architecture.py génère ACME, DOT et la matrice de traçabilité ; --check détecte toute divergence textuelle. Les tests inspectent l’assemblage, les contrats et les imports interdits.')
para('Limite : la génération utilise le sous-ensemble structurel d’ACME. Aucun parseur ACME externe ni vérificateur de propriétés formelles n’a été exécuté. Le contrôle local est un contrôle de cohérence, pas une preuve générale de conformité.','small')
end()
start(7,'Scénario : message privé','Le bus découple la production d’un message de la création de sa notification.')
# sequence diagram, compact table of calls, each transition names actual connector
head('Séquence nominale (Alice envoie à Bob)')
table(['Étape','Interaction','Résultat'],[('1','ConsoleUI → ui_messages → MessageService.send','L’identité Alice vient de la session ; Bob et le texte sont saisis.'),('2','MessageService → message_store → Storage','Résout Bob, valide le texte, récupère le nom d’Alice et insère le message ; commit.'),('3','MessageService.events → message_bus','Publie MessageSent(recipient, sender, message_id) sans corps du message.'),('4','message_bus → NotificationService.on_message','Le callback ajoute une notification au tampon de Bob.'),('5','MessageService → ConsoleUI','Retour de l’identifiant ; Alice voit la confirmation.'),('6','ConsoleUI → ui_notifications → NotificationService.take','Après connexion de Bob, le menu consomme ses notifications.'),('7','ConsoleUI → ui_messages → MessageService.history → Storage','Bob récupère son historique ; un tiers ne voit pas ce message.')],[.10,.43,.47])
head('Ordonnancement et traitement des erreurs')
para('La publication d’événement intervient après la transaction d’insertion. Si la validation ou l’insertion échoue, aucune notification n’est produite. Une erreur de callback inattendue après commit peut laisser un message enregistré sans notification ; aucune garantie transactionnelle globale n’est revendiquée. Le seul abonné actuel ajoute une chaîne dans un tampon mémoire.')
head('Bénéfice du style publish/subscribe')
para('Le MessageService ne connaît pas NotificationService et ne l’importe pas. Un nouvel abonné (par exemple un compteur de messages) pourrait être raccordé au même bus en étendant le modèle et l’assemblage sans modifier la logique de send. Les abonnés sont internes et de confiance ; aucun événement n’est envoyé à un client externe.')
end()
start(8,'Persistance et compromis','Simplicité d’exploitation sans négliger les invariants métier.')
table(['Table','Données et contraintes'],[('users','id, name UNIQUE, password : sel et empreinte dérivée.'),('friends','a, b : clés étrangères ; clé primaire (a,b), CHECK(a<b).'),('posts','author, kind, content, image BLOB, created ; image présente seulement pour kind=image.'),('messages','sender, recipient, body, created ; clés étrangères, sender différent de recipient.')],[.23,.77])
head('Intégrité et confidentialité')
para('Les clés étrangères SQLite sont activées à l’ouverture. Les modifications sont transactionnelles et les valeurs SQL sont passées comme paramètres. Les index couvrent auteurs, amis et participants aux messages. L’authentification utilise PBKDF2-HMAC-SHA256 (600 000 itérations), un sel aléatoire de 16 octets et une comparaison d’empreintes à temps constant. Aucun mot de passe n’est affiché dans l’annuaire.')
para('Le même prédicat SQL de visibilité est utilisé pour le fil et l’export d’image. L’historique des messages filtre par identité de l’émetteur ou du destinataire. Le choix de la console impose une session locale unique ; les identifiants ne sont pas saisis directement pour agir à la place d’un autre compte.')
head('Alternatives examinées')
table(['Alternative','Pourquoi non retenue'],[('Web / REST','Interface et serveur supplémentaires sans nécessité fonctionnelle.'),('Microservices / broker','Coût de déploiement, sérialisation, pannes réseau et coordination disproportionnés.'),('Fichiers JSON','Contraintes, transactions et jointures à réimplémenter.'),('Bus asynchrone durable','Threads ou broker, retries et garanties de livraison inutiles pour ce prototype.')],[.34,.66])
para('Le fichier SQLite n’est pas chiffré ; un accès local direct au fichier contourne les contrôles console. La reconnaissance d’image par signature n’est pas une validation complète du format.','small')
end()
start(9,'Validation et conclusion','Les tests relient exigences fonctionnelles, architecture et exécution.')
table(['Exigence','Vérification représentative'],[('F1','test_login_and_normalization, test_hashes_salted, test_register_and_duplicate'),('F2–F3','test_feed_filters_and_orders, test_links, test_image_bytes_export_and_access'),('F4–F5','test_private_messages_and_notification, test_friendship_is_symmetric'),('N1–N2','test_runtime_topology, test_no_component_to_component_imports, test_documentation_is_current'),('N3–N4','test_full_cli_and_restart, test_persistence, test_message_errors_no_events')],[.25,.75])
head('Reproduction des vérifications')
code(['python3 -m mininet --demo','python3 -m unittest discover -v','python3 tools/architecture.py --check'])
para('Le journal docs/RESULTATS_TESTS.txt conserve la sortie de l’exécution automatisée. Les tests incluent les erreurs de saisie, la persistance, la restriction du fil et des messages, les événements et la traversée réelle des menus. Les bases de test sont temporaires.')
head('Limites et évolution')
para('Pas de multi-utilisateur simultané dans une même console, pas de session distante, pas de chiffrement des contenus au repos ni de notification durable. Une interface web nécessiterait un modèle de sessions et de contrôle d’accès adapté ; un bus durable nécessiterait de traiter les échecs après commit (par exemple avec une outbox). La validation n’est pas une preuve d’absence de défauts.')
para('MiniNet illustre qu’un prototype réduit peut néanmoins expliciter les composants, les contrats de communication et les attaches, puis vérifier leur correspondance avec les objets effectivement assemblés.')
head('Références')
para('[1] Sujet du projet ASA, MiniNet, promotion ALMA M2 2025/2026 (PDF fourni, 2 pages).<br/>[2] Carnegie Mellon University, <i>Acme Language Overview</i>, https://www.cs.cmu.edu/~acme/docs/language_overview.html (consulté lors de la réalisation).','small')
end();c.save()
