"""Génération reproductible des vues à partir de l'assemblage (stdlib)."""
import argparse
import sys
from pathlib import Path
from collections import defaultdict
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mininet.architecture import COMPONENTS, CALLS, EVENT


def artifacts():
    ports = defaultdict(set)
    for c in CALLS:
        ports[c.consumer].add(c.required)
        ports[c.provider].add(c.provided)
    name,publisher,pp,subscriber,sp = EVENT
    ports[publisher].add(pp)
    ports[subscriber].add(sp)
    lines = ['System MiniNet = {']
    for comp in COMPONENTS:
        lines.append(f'  Component {comp} = {{')
        lines.extend(f'    Port {port};' for port in sorted(ports[comp]))
        lines.append('  };')
    for c in CALLS:
        lines += [f'  Connector {c.name} = {{ Role caller; Role callee; Property asynchronous : boolean = false; }};']
    lines += [f'  Connector {name} = {{ Role publisher; Role subscriber; Property asynchronous : boolean = false; }};', '  Attachments {']
    for c in CALLS:
        lines += [f'    {c.consumer}.{c.required} to {c.name}.caller;',f'    {c.provider}.{c.provided} to {c.name}.callee;']
    lines += [f'    {publisher}.{pp} to {name}.publisher;',f'    {subscriber}.{sp} to {name}.subscriber;', '  }','}']
    acme = '\n'.join(lines)+'\n'
    # Graphviz C&C : les connecteurs sont des nœuds (et non de simples flèches).
    dot = ['digraph MiniNet {','  graph [rankdir=TB, bgcolor="white", pad=0.15, nodesep=0.27, ranksep=0.35, splines=polyline];','  node [fontname="DejaVu Sans", fontsize=11];','  edge [fontname="DejaVu Sans", fontsize=8, color="#506578", arrowsize=0.55];']
    for comp in COMPONENTS:
        dot.append(f'  {comp} [shape=box, style="rounded,filled", fillcolor="#e6f0f5", color="#28546c"];')
    dot += ['  {rank=same; UserManager; FriendManager; PostManager; MessageService; NotificationService;}']
    for c in CALLS:
        dot += [f'  {c.name} [shape=ellipse, style=filled, fillcolor="#f0f2f4", color="#8294a2", label="{c.name}"];', f'  {c.consumer} -> {c.name};',f'  {c.name} -> {c.provider};']
    dot += [f'  {name} [shape=ellipse, style=filled, fillcolor="#ffedcc", color="#a66e18"];',f'  {publisher} -> {name} [color="#a66e18", style=dashed, constraint=false];',f'  {name} -> {subscriber} [color="#a66e18", style=dashed, constraint=false];', '}']
    trace = ['# Traçabilité : architecture → code','', 'Générée depuis `mininet/architecture.py`. Les ports requis sont les attributs injectés ; les ports fournis sont des ensembles nommés de méthodes exposées par le connecteur.','', '## Composants','', '| Composant ACME | Module et classe Python |','|---|---|']
    trace += [f'| `{comp}` | `mininet/components/{path.split(".")[0]}.py` / `{path.split(".")[1]}` |' for comp,path in COMPONENTS.items()]
    trace += ['', '## Connecteurs et ports','', '| Connecteur | Port requis / rôle caller | Port fourni / rôle callee | Opérations |','|---|---|---|---|']
    trace += [f'| `{c.name}` | `{c.consumer}.{c.required}` | `{c.provider}.{c.provided}` | '+', '.join(f'`{op}`' for op in c.operations)+' |' for c in CALLS]
    trace += ['', f'`{name}` : `{publisher}.{pp}` (publisher) → `{subscriber}.{sp}` (subscriber), événement `MessageSent` ; `PublisherPort`, `MessageBus` dans `mininet/connectors.py`. Les neuf autres connecteurs sont des instances de `ProcedureCall`. L’assemblage est réalisé dans `mininet/assembly.py`.','']
    return {'MiniNet.acme':acme,'composants.dot':'\n'.join(dot)+'\n','TRACABILITE.md':'\n'.join(trace)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true',help='vérifie sans modifier')
    args=p.parse_args()
    for name, content in artifacts().items():
        path=ROOT/'architecture'/name
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8')!=content:
                raise SystemExit(f'Vue obsolète : {path}')
        else:
            path.write_text(content,encoding='utf-8')
    print('Vues architecturales cohérentes.' if args.check else 'Vues générées.')

if __name__=='__main__':
    main()
