# Sources facultatives des documents

Les PDF et le PPTX sont déjà générés au nom de Hugo PIARD et Louis BOULANGER. Pour modifier les noms ultérieurement, mettre à jour les chaînes `Binôme` et les métadonnées des auteurs dans `build_report.py` et `build_slides.py`, puis régénérer les documents. Les scripts de génération documentaire nécessitent des outils supplémentaires, contrairement au prototype : reportlab, Pillow et python-pptx, ainsi que les polices DejaVu Sans / DejaVu Sans Mono (chemins Linux dans build_report.py). LibreOffice permet de réexporter le PPTX en PDF.

Depuis la racine :

```bash
python3 tools/doc_sources/build_report.py
python3 tools/doc_sources/build_slides.py
libreoffice --headless --convert-to pdf --outdir docs docs/Soutenance.pptx
```
