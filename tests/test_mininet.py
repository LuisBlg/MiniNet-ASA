import ast
import os
import re
from contextlib import closing
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from mininet.assembly import assemble
from mininet.architecture import COMPONENTS, CALLS, EVENT
from mininet.connectors import ProcedureCall, MessageBus
from mininet.domain import DomainError, MessageSent

ROOT=Path(__file__).resolve().parents[1]
PASSWORD='MotDePasse!'

class FunctionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Une base de départ partagée uniquement comme fichier modèle ; copie par test.
        cls.temp=tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.template=Path(cls.temp.name)/'template.db'
        with assemble(cls.template) as app:
            cls.ids=[app.console.users.register(n,PASSWORD) for n in ('alice','bob','clara')]

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'test.db'
        self.path.write_bytes(self.template.read_bytes())
        self.ctx=assemble(self.path)
        self.app=self.ctx.__enter__()
        self.addCleanup(self.ctx.__exit__,None,None,None)
        self.ui=self.app.console
        self.a,self.b,self.c=self.ids

    def test_login_and_normalization(self):
        self.assertEqual(self.ui.users.authenticate(' ALICE ',PASSWORD),self.a)

    def test_wrong_password_and_unknown_account(self):
        for user,password in [('alice','incorrect'),('inconnu',PASSWORD),('x',PASSWORD)]:
            with self.subTest(user=user), self.assertRaisesRegex(DomainError,'Identifiants incorrects'):
                self.ui.users.authenticate(user,password)

    def test_register_and_duplicate(self):
        uid=self.ui.users.register('david',PASSWORD)
        self.assertEqual(self.ui.users.authenticate('david',PASSWORD),uid)
        with self.assertRaises(DomainError): self.ui.users.register('DAVID',PASSWORD)

    def test_invalid_credentials(self):
        for name,password in [('a',PASSWORD),('a b',PASSWORD),('david','short'),('david','a'*129)]:
            with self.subTest(name=name), self.assertRaises(DomainError): self.ui.users.register(name,password)

    def test_hashes_salted(self):
        import sqlite3
        with closing(sqlite3.connect(self.path)) as db:
            hashes=[r[0] for r in db.execute('SELECT password FROM users')]
        self.assertEqual(len(set(hashes)),3)
        self.assertTrue(all(PASSWORD not in h and len(h)==97 for h in hashes))

    def test_directory(self):
        self.assertEqual(self.ui.users.list_users(self.a),['bob','clara'])

    def test_friendship_is_symmetric(self):
        self.ui.friends.add(self.a,'bob')
        self.assertEqual(self.ui.friends.list(self.b),['alice'])
        with self.assertRaises(DomainError): self.ui.friends.add(self.b,'alice')
        self.ui.friends.remove(self.b,'alice')
        self.assertEqual(self.ui.friends.list(self.a),[])

    def test_friend_errors(self):
        for operation,name in [(self.ui.friends.add,'alice'),(self.ui.friends.add,'unknown'),(self.ui.friends.remove,'bob')]:
            with self.subTest(name=name), self.assertRaises(DomainError): operation(self.a,name)

    def test_feed_filters_and_orders(self):
        self.ui.friends.add(self.a,'bob')
        p1=self.ui.posts.publish_text(self.b,'Bonjour')
        self.ui.posts.publish_text(self.c,'Invisible')
        p3=self.ui.posts.publish_link(self.a,'https://example.org')
        self.assertEqual([p.id for p in self.ui.posts.feed(self.a)],[p3,p1])
        self.ui.friends.remove(self.a,'bob')
        self.assertEqual([p.id for p in self.ui.posts.feed(self.a)],[p3])

    def test_text_limits_and_sql_literals(self):
        for content in ('','a'*281,'\x1b[31m'):
            with self.subTest(content=content), self.assertRaises(DomainError): self.ui.posts.publish_text(self.a,content)
        value="'); DROP TABLE users; --"
        self.ui.posts.publish_text(self.a,value)
        self.assertEqual(self.ui.posts.feed(self.a)[0].content,value)
        self.assertEqual(self.ui.users.list_users(self.a),['bob','clara'])

    def test_links(self):
        for value in ('ftp://test.org','https://','https://a b','https://[','https://host:bad'):
            with self.subTest(value=value), self.assertRaises(DomainError): self.ui.posts.publish_link(self.a,value)
        self.ui.posts.publish_link(self.a,'https://example.org/path?q=1')
        self.assertEqual(self.ui.posts.feed(self.a)[0].kind,'link')

    def test_image_bytes_export_and_access(self):
        src=Path(self.tmp.name)/'image.png'
        data=(ROOT/'examples/mininet.png').read_bytes()
        src.write_bytes(data)
        pid=self.ui.posts.publish_image(self.b,src)
        src.unlink() # La publication ne dépend plus du fichier source.
        dst=Path(self.tmp.name)/'export.png'
        with self.assertRaises(DomainError): self.ui.posts.export_image(self.a,pid,dst)
        self.ui.friends.add(self.a,'bob')
        self.ui.posts.export_image(self.a,pid,dst)
        self.assertEqual(dst.read_bytes(),data)
        with self.assertRaises(DomainError): self.ui.posts.export_image(self.a,pid,dst)
        self.ui.friends.remove(self.a,'bob')
        with self.assertRaises(DomainError): self.ui.posts.export_image(self.a,pid,src)
        self.assertFalse(src.exists())

    def test_invalid_images(self):
        path=Path(self.tmp.name)/'bad.png'
        with self.assertRaises(DomainError): self.ui.posts.publish_image(self.a,path)
        path.write_bytes(b'not an image')
        with self.assertRaises(DomainError): self.ui.posts.publish_image(self.a,path)
        path.write_bytes(b'\x89PNG\r\n\x1a\n'+b'x'*(2*1024*1024))
        with self.assertRaises(DomainError): self.ui.posts.publish_image(self.a,path)
        self.assertEqual(self.ui.posts.feed(self.a),[])

    def test_private_messages_and_notification(self):
        mid=self.ui.messages.send(self.a,'bob','Secret')
        self.assertEqual(self.ui.messages.history(self.a)[0].id,mid)
        self.assertEqual(self.ui.messages.history(self.b)[0].body,'Secret')
        self.assertEqual(self.ui.messages.history(self.c),[])
        self.assertEqual(self.ui.notifications.take(self.a),[])
        self.assertEqual(self.ui.notifications.take(self.c),[])
        self.assertEqual(self.ui.notifications.take(self.b),[f'Nouveau message de alice (#{mid}).'])
        self.assertEqual(self.ui.notifications.take(self.b),[])

    def test_message_errors_no_events(self):
        for recipient,body in [('alice','ok'),('unknown','ok'),('bob',''),('bob','a'*501)]:
            with self.subTest(recipient=recipient), self.assertRaises(DomainError): self.ui.messages.send(self.a,recipient,body)
        self.assertEqual(self.ui.messages.history(self.a),[])
        self.assertEqual(self.ui.notifications.take(self.b),[])

    def test_persistence(self):
        self.ui.friends.add(self.a,'bob')
        self.ui.posts.publish_text(self.b,'Persistant')
        self.ui.messages.send(self.b,'alice','Persistant aussi')
        with assemble(self.path) as reopened:
            ui=reopened.console
            self.assertEqual(ui.users.authenticate('alice',PASSWORD),self.a)
            self.assertEqual(ui.friends.list(self.a),['bob'])
            self.assertEqual(ui.posts.feed(self.a)[0].content,'Persistant')
            self.assertEqual(ui.messages.history(self.a)[0].body,'Persistant aussi')
            self.assertEqual(ui.notifications.take(self.a),[])

class ArchitectureTests(unittest.TestCase):
    def test_runtime_topology(self):
        with assemble(':memory:') as app:
            self.assertEqual(set(app.components),set(COMPONENTS))
            self.assertEqual(set(app.connectors),{c.name for c in CALLS}|{EVENT[0]})
            for c in CALLS:
                wire=app.connectors[c.name]
                self.assertIs(getattr(app.components[c.consumer],c.required),wire)
                self.assertIs(wire._provider,app.components[c.provider])
                self.assertEqual(wire._operations,set(c.operations))
                for op in c.operations:
                    self.assertTrue(callable(getattr(wire,op)))
                with self.assertRaises(AttributeError): getattr(wire,'close')
            name,pub,pp,sub,sp=EVENT
            self.assertIs(getattr(app.components[pub],pp).bus,app.connectors[name])
            self.assertEqual(app.connectors[name]._subscribers,[getattr(app.components[sub],sp)])

    def test_no_component_to_component_imports(self):
        for path in (ROOT/'mininet/components').glob('*.py'):
            tree=ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    self.assertTrue(node.level==0 or (node.level==2 and node.module=='domain'),str(path))
                    self.assertNotIn('components',node.module or '')
                    self.assertFalse((node.module or '').startswith('mininet.'))
                if isinstance(node,ast.Import):
                    self.assertFalse(any(n.name.startswith('mininet') for n in node.names))
                    if path.name!='storage.py': self.assertFalse(any(n.name=='sqlite3' for n in node.names))

    def test_documentation_is_current(self):
        subprocess.run([sys.executable,'tools/architecture.py','--check'],cwd=ROOT,check=True,capture_output=True)

    def test_acme_attachments_match_declared_ports_and_roles(self):
        source=(ROOT/'architecture/MiniNet.acme').read_text(encoding='utf-8')
        components={name:set(re.findall(r'Port (\w+);',body))
                    for name,body in re.findall(r'Component (\w+) = \{([^}]+)\};',source)}
        connectors={name:set(re.findall(r'Role (\w+);',body))
                    for name,body in re.findall(r'Connector (\w+) = \{([^}]+)\};',source)}
        attachments=re.findall(r'(\w+)\.(\w+) to (\w+)\.(\w+);',source)
        self.assertEqual(set(components),set(COMPONENTS))
        self.assertEqual(set(connectors),{c.name for c in CALLS}|{EVENT[0]})
        left=[(comp,port) for comp,port,_,_ in attachments]
        right=[(conn,role) for _,_,conn,role in attachments]
        self.assertCountEqual(left,[(c,p) for c,ports in components.items() for p in ports])
        self.assertCountEqual(right,[(c,r) for c,roles in connectors.items() for r in roles])
        expected=[a for c in CALLS for a in [(c.consumer,c.required,c.name,'caller'),(c.provider,c.provided,c.name,'callee')]]
        name,pub,pp,sub,sp=EVENT
        expected += [(pub,pp,name,'publisher'),(sub,sp,name,'subscriber')]
        self.assertCountEqual(attachments,expected)

    def test_connector_rejects_bad_contract(self):
        with self.assertRaises(TypeError): ProcedureCall('x',object(),('foo',))

    def test_event_multicast(self):
        bus=MessageBus(); a=[]; b=[]
        bus.subscribe(a.append); bus.subscribe(a.append); bus.subscribe(b.append)
        e=MessageSent(1,'alice',42); bus.publish(e)
        self.assertEqual(a,[e]); self.assertEqual(b,[e])
        with self.assertRaises(TypeError): bus.publish('bad')

class ConsoleTests(unittest.TestCase):
    def run_cli(self,*args,commands):
        return subprocess.run([sys.executable,'-m','mininet',*args],cwd=ROOT,input='\n'.join(commands)+'\n',capture_output=True,text=True,encoding='utf-8',timeout=30,env={**os.environ,'PYTHONUTF8':'1'})

    def test_full_cli_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=str(Path(tmp)/'social.db'); dst=str(Path(tmp)/'export.png')
            result=self.run_cli('--db',db,commands=['bad','1','alice',PASSWORD,'1','bob',PASSWORD,'1','clara',PASSWORD,'2','alice','incorrect','2','alice',PASSWORD,'9','6','bob','8','1','Hello Alice','2','https://example.org','3','examples/mininet.png','4','10','bob','SECRET-ALICE','0','2','bob',PASSWORD,'4','5','3',dst,'11','7','alice','4','0','2','clara',PASSWORD,'4','11','0','0'])
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stderr,'')
            self.assertIn('Identifiants incorrects',result.stdout)
            self.assertEqual(result.stdout.count('Compte créé'),3)
            self.assertIn('Image exportée',result.stdout)
            self.assertEqual(Path(dst).read_bytes(),(ROOT/'examples/mininet.png').read_bytes())
            self.assertIn('[Notification] Nouveau message de alice',result.stdout)
            clara=result.stdout.split('=== MiniNet | clara ===',1)[1]
            self.assertNotIn('SECRET-ALICE',clara)
            self.assertNotIn('Hello Alice',clara)
            result2=self.run_cli('--db',db,commands=['2','bob',PASSWORD,'11','4','0','0'])
            self.assertEqual(result2.returncode,0,result2.stderr)
            self.assertIn('SECRET-ALICE',result2.stdout)
            self.assertNotIn('Hello Alice',result2.stdout)

    def test_demo_does_not_create_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Exécuter dans un répertoire indépendant, avec une base sentinelle.
            directory=Path(tmp)
            sentinel=directory/'mininet.db'
            sentinel.write_bytes(b'ne pas modifier')
            result=subprocess.run([sys.executable,'-m','mininet','--demo'],cwd=directory,
                input='2\nalice\nDemo2026!\n4\n11\n0\n0\n',capture_output=True,
                text=True,encoding='utf-8',timeout=30,
                env={**os.environ,'PYTHONPATH':str(ROOT),'PYTHONUTF8':'1'})
            self.assertEqual(sentinel.read_bytes(),b'ne pas modifier')
            self.assertEqual(list(directory.iterdir()),[sentinel])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Bonjour Alice !',result.stdout)
        self.assertNotIn('Publication hors du cercle',result.stdout)
        self.assertIn('[Notification]',result.stdout)

    def test_eof_and_bad_database(self):
        self.assertEqual(self.run_cli('--demo',commands=[]).returncode,0)
        with tempfile.TemporaryDirectory() as tmp:
            result=self.run_cli('--db',tmp,commands=['0'])
            self.assertEqual(result.returncode,1)
            self.assertIn('Erreur SQLite',result.stderr)

if __name__=='__main__': unittest.main()
