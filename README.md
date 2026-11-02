# Midterms 2026
1. Sube estos archivos a un repo nuevo (rama main).
2. Settings → Pages → Deploy from branch → main / root.
3. Settings → Secrets and variables → Actions → New secret `AP_API_KEY` (tu clave de AP Elections API).
4. Prueba en Actions → "Actualizar resultados AP" → Run workflow, y revisa que `results.json` se llene.

NOTA: en carreras con independiente a la izquierda (NE, ID, SD) la columna "D" debe llevar los votos de ese independiente; el script no lo hace solo.
