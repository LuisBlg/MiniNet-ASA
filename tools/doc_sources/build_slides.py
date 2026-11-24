from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
R=Path(__file__).resolve().parents[2]; D=R/'docs'
prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
NAVY='17394D'; TEAL='216D79'; INK='243746'; MUTED='536776'; PALE='E7F1F4'; GRAY='F3F5F6'; GOLD='A66E18'; WHITE='FFFFFF'
def rgb(s):return RGBColor.from_string(s)
def text(s,x,y,w,h,size=24,color=INK,bold=False,font='DejaVu Sans',align=None):
 box=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=tf.margin_right=Inches(.02);tf.margin_top=tf.margin_bottom=Inches(.02)
 for i,line in enumerate(s.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=line; p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_after=Pt(4)
  if align:p.alignment=align
 return box

def rect(x,y,w,h,color,stroke=None):
 sh=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=rgb(color);sh.line.fill.background() if not stroke else None
 if stroke:sh.line.color.rgb=rgb(stroke)
 return sh

def base(n,title,sub):
 global slide
 slide=prs.slides.add_slide(prs.slide_layouts[6]); slide.background.fill.solid();slide.background.fill.fore_color.rgb=rgb(WHITE)
 rect(0,0,13.333,.13,TEAL);text('MININET  /  ASA  ·  ALMA M2',.55,.28,12,.3,11,TEAL,True);text(title,.55,.79,12.2,.66,30,NAVY,True);text(sub,.57,1.46,12.1,.5,15,MUTED);rect(.55,7.03,12.2,.018,'CDD8DD');text('Architecture à base de composants et connecteurs',.55,7.1,11,.27,10,MUTED);text(f'{n:02d}',12.1,7.1,.62,.3,10,MUTED,True,align=PP_ALIGN.RIGHT)

def panel(x,y,w,h,heading,body):
 rect(x,y,w,h,GRAY);rect(x,y,.07,h,TEAL);text(heading,x+.2,y+.14,w-.4,.48,19,NAVY,True);text(body,x+.2,y+.75,w-.4,h-.87,17,INK)

def notes(s):
 slide.notes_slide.notes_text_frame.text=s

base(1,'MiniNet','Mini réseau social en console — prototype et architecture C&C')
text('Une architecture explicite,\nune implémentation minimale.',.7,2.0,12,1.7,40,NAVY,True)
text('Python  ·  SQLite  ·  ACME',.75,4.1,11,.7,25,TEAL,True)
text('Binôme : ........................................ / ........................................\nMaster 2 Informatique – ALMA · Université de Nantes',.75,5.4,12,.9,17,MUTED)
notes('45 s. Le sujet évalue la clarté architecturale plutôt que la richesse de l’interface. Présenter l’objectif et les choix de sobriété.')
base(2,'Le périmètre fonctionnel','Les cinq exigences sont couvertes ; aucune interface graphique nécessaire.')
panel(.6,2.05,3.98,1.72,'Comptes','Inscription et authentification locale.')
panel(4.68,2.05,3.98,1.72,'Publications','Texte, lien et image réellement stockée.')
panel(8.76,2.05,3.98,1.72,'Fil d’actualité','Soi-même et ses amis actuels.')
panel(.6,4.02,5.98,1.7,'Amitiés','Relation réciproque immédiate ; ajout et retrait.')
panel(6.74,4.02,6,1.7,'Messages privés','Historique filtré et notification ciblée.')
text('Extension retenue : bus publish/subscribe synchrone.',.65,6.24,12,.5,21,TEAL,True)
notes('1 min. Rappeler les décisions : images exportables, amis symétriques, messages possibles à tout compte existant. Notifications en mémoire.')
base(3,'La vue C&C','7 composants · 9 connecteurs d’appel · 1 connecteur événementiel')
slide.shapes.add_picture(str(R/'architecture/composants.png'),Inches(.65),Inches(1.95),width=Inches(12.0),height=Inches(5.0))
notes('1 min 30. Rectangles = composants ; ellipses = connecteurs. Expliquer le sens de la requête, le retour synchrone et le bus. Storage encapsule SQLite. La console est un composant, le terminal est extérieur.')
base(4,'Des ports et des rôles explicites','Exemple de la liaison ui_messages, extrait ACME')
rect(.65,2.05,12,2.55,GRAY)
text('Component ConsoleUI = { Port messages; };\nComponent MessageService = { Port api; };\nConnector ui_messages = { Role caller; Role callee; };\nAttachments {\n  ConsoleUI.messages to ui_messages.caller;\n  MessageService.api to ui_messages.callee;\n}',.9,2.24,11.5,2.21,17,NAVY,False,'DejaVu Sans Mono')
panel(.65,4.92,5.85,1.45,'Port requis','ConsoleUI.messages : opérations send, history.')
panel(6.75,4.92,5.9,1.45,'Port fourni','MessageService.api : contrat exposé par le connecteur.')
notes('1 min. Le composant expose des opérations ; le port indique le point d’interaction ; le rôle correspond à une extrémité du connecteur. Deux attaches explicites. Montrer le fichier complet si besoin.')
base(5,'Du modèle au code','Le modèle déclaratif est utilisé à l’exécution et pour générer les vues.')
panel(.65,2.1,4.0,2.0,'architecture.py','Déclare composants, ports, liaisons et opérations.')
panel(4.8,2.1,3.9,2.0,'assembly.py','Instancie les classes et injecte les connecteurs.')
panel(8.85,2.1,3.8,2.0,'connectors.py','ProcedureCall et MessageBus matérialisent les échanges.')
rect(.65,4.45,12,1.45,PALE);text('Même modèle → MiniNet.acme, diagramme DOT et matrice de traçabilité',.95,4.7,11.4,1.0,23,TEAL,True)
text('Tests : fournisseurs, ports injectés, opérations, abonnement et imports.',.67,6.2,12,.5,18,MUTED)
notes('1 min. Ouvrir assembly.py. Le connecteur relaie seulement les opérations prévues, les composants ne s’importent pas entre eux. Les tests ne sont pas une preuve formelle.')
base(6,'Un événement, deux responsabilités','MessageService ne connaît pas NotificationService.')
for i,(a,b) in enumerate([('1 · MessageService','Valide et persiste le message.'),('2 · message_bus','Diffuse MessageSent après commit.'),('3 · NotificationService','Tamponne pour le destinataire.'),('4 · ConsoleUI','Consomme au prochain menu.')]):
 y=2.04+i*1.04;rect(.65,y,12,.89,PALE if i%2==0 else GRAY);text(a,.86,y+.15,4.1,.62,18,TEAL,True);text(b,5.02,y+.15,7.4,.65,18,INK)
text('Synchrone, local et sans rétention d’événements ; pas de corps de message sur le bus.',.67,6.34,12,.5,16,MUTED)
notes('1 min. Le bus est synchrone mais découplé. La notification est éphémère ; les messages sont persistants. En cas d’échec inattendu du callback après commit, le message reste enregistré.')
base(7,'Démonstration','Trois comptes, deux amis, un tiers : vérifier les frontières de visibilité.')
rect(.65,2.0,12,.75,NAVY);text('python3 -m mininet --demo',.9,2.16,11.4,.4,22,WHITE,True,'DejaVu Sans Mono')
for i,(a,b) in enumerate([('Alice','Fil de Bob, image et envoi d’un message privé.'),('Bob','Notification, historique, export ; suppression d’Alice.'),('Clara','Aucun message des autres, aucune publication de leurs comptes.')]):
 y=3.0+i*1.03; text(a,.78,y,2.0,.6,23,TEAL,True);text(b,3.1,y,9.4,.7,20,INK)
text('Comptes : alice / bob / clara  ·  Mot de passe : Demo2026!',.7,6.34,12,.5,16,MUTED)
notes('4 à 5 min. Suivre docs/DEMONSTRATION.md. Montrer l’export et la suppression. Mode démo isolé et non persistant.')
base(8,'Validation et bilan','La qualité architecturale est vérifiée, pas seulement décrite.')
panel(.65,2.0,5.9,2.2,'Tests automatisés','Fonctionnalités, cas d’erreur, persistance, confidentialité logique et câblage.')
panel(6.75,2.0,5.9,2.2,'Limites assumées','Mono-processus, base locale non chiffrée, notifications éphémères, pas de parseur ACME externe.')
rect(.65,4.48,12,1.45,GRAY);text('python3 -m unittest discover -v\npython3 tools/architecture.py --check',.9,4.73,11.4,1.02,19,NAVY,False,'DejaVu Sans Mono')
text('Bilan : simplicité d’exploitation, interactions explicites et traçabilité vérifiable.',.65,6.28,12,.55,19,TEAL,True)
notes('2 min. Montrer le journal ou lancer les tests. Conclure sur la cohérence et les limites. Pour une future version web, adapter l’identité et le modèle de confiance.')
prs.save(D/'Soutenance.pptx')
