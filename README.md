# Currículum — Ethan Moreno

Versiones públicas del currículum de Ethan Moreno en PDF, generadas desde una única fuente de datos.

**Perfil:** https://github.com/ethanmorenodev · **Portfolio:** https://ethanmorenodev.github.io/portfolio/

## Versiones

| Archivo | Perfil |
|---|---|
| `CV_Ethan_Moreno_General.pdf` | Sistemas, desarrollo web e IA aplicada. |
| `CV_Ethan_Moreno_Soporte_IT.pdf` | Soporte IT y sistemas. |
| `CV_Ethan_Moreno_Frontend.pdf` | Desarrollo web. |
| `CV_Ethan_Moreno_DotNet.pdf` | C# / .NET. |
| `CV_Ethan_Moreno_Hibrido.pdf` | Versión híbrida con retrato, una sola columna. |

El CV enlazado desde el portfolio es byte-idéntico a la versión **General**.

## Regenerar los PDF

Los archivos se generan desde `source/cv_data.json` con `source/build_cvs.py` (requiere `reportlab` y `PyMuPDF`):

```bash
python source/build_cvs.py
```

El script escribe los PDF en la carpeta `source/`. Cópialos a la raíz de este repositorio y a `portfolio/cv/` si actualizas el contenido.

## Notas

- Las cifras de pruebas de ProjectVTT se presentan como documentadas en una ficha técnica del 10/11/2026; no se reejecutaron.
- El código de ProjectVTT está publicado en https://github.com/ethanmorenodev/projectvtt (MIT); su documentación está en https://github.com/ethanmorenodev/projectvtt-docs.
- No se incluyen credenciales ni datos de candidaturas.

## Licencia

Los PDF son documentos personales de Ethan Moreno. El script de generación se publica bajo licencia [MIT](LICENSE).
