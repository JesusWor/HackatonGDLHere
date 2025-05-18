# 🗺️ HERE Hackathon 2025 – POI295 Auto-Correction System

## 📌 Descripción del Proyecto

Este proyecto fue desarrollado para el **GuadalaHacks 2025**, organizado por HERE Technologies. El reto consiste en **automatizar la corrección de errores espaciales** detectados por la validación **POI295**, que identifica posibles inconsistencias en la ubicación de Puntos de Interés (POIs) dentro de carreteras “Multiply Digitised”.

Nuestro objetivo es eliminar la necesidad de intervención humana mediante un sistema inteligente capaz de clasificar, corregir y escalar esta solución a nivel global.

---

## 🎯 Objetivo

Detectar y resolver automáticamente los siguientes escenarios definidos por la validación POI295:

1. ❌ **El POI ya no existe:** Eliminar del dataset.
2. ↔️ **POI en lado incorrecto del camino:** Reasignar con base en la dirección del `Reference Node`.
3. 🛣️ **Error de atribución en la vía:** Corregir atributo `MULTIDIGIT`.
4. ✅ **Ubicación correcta:** Marcar como “Legítima excepción”.

---

## 🧰 Tecnologías Utilizadas

- **Python** (GeoPandas, Pandas, Shapely, rquests, math)
- **HERE REST APIs** (Imágenes satelitales)
- **Leaflets.js** (biblioteca de mapas interactivos)
- **tolov8n** (Validación opcional con imágenes)
- **OpenStreetma** (Calles, contexto urbano)

---
