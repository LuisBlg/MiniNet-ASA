# Sources facultatives des documents

Les PDF et le PPTX sont déjà générés. Pour personnaliser les noms du binôme, modifier le fichier PPTX dans LibreOffice Impress ou PowerPoint ; pour le rapport, modifier la chaîne `Binôme` dans `build_report.py` puis régénérer le PDF. Les scripts de génération documentaire nécessitent des outils supplémentaires, contrairement au prototype : reportlab, Pillow et python-pptx, ainsi que les polices DejaVu Sans / DejaVu Sans Mono (chemins Linux dans build_report.py). LibreOffice permet de réexporter le PPTX en PDF.

Depuis la racine :

```bash
python3 tools/doc_sources/build_report.py
python3 tools/doc_sources/build_slides.py
libreoffice --headless --convert-to pdf --outdir docs docs/Soutenance.pptx
```
