# 🗺️ HERE Hackathon 2025 – POI295 Auto-Correction System

## 📌 Project Description

This project was developed for **GuadalaHacks 2025**, organized by HERE Technologies. The challenge focuses on **automating the correction of spatial errors** detected by the **POI295 validation**, which identifies potential inconsistencies in the location of Points of Interest (POIs) on “Multiply Digitised” roads.

The main goal is to eliminate the need for manual intervention through an intelligent system capable of classifying, correcting, and scaling the solution globally.

---

## 🎯 Objective

Automatically detect and resolve the following scenarios defined by POI295 validation:

1. ❌ **The POI no longer exists:** Remove it from the dataset.
2. ↔️ **POI is on the wrong side of the road:** Reassign it based on the direction of the `Reference Node`.
3. 🛣️ **Attribution error on the road segment:** Fix the `MULTIDIGIT` attribute.
4. ✅ **Correct location:** Mark as a “Legitimate exception”.

---

## 🧰 Technologies Used

- **Python** (GeoPandas, Pandas, Shapely, requests, math)
- **HERE REST APIs** (Satellite imagery acquisition)
- **Leaflet.js** (interactive web mapping)
- **YOLOv8n** (optional visual validation through object detection)
- **OpenStreetMap** (contextual street data)

---

## 🗂️ Project Structure
🗂️ HERE/HERE
|
├── here-visor: in this carpet we can find the files that make the vizualization in the map with the errors
🗂️ filtros: in this carpet we can find the funtion to filter the streets
🗂️ Deteccion_sospechosos: in this carpet we ca find the street and POIs filter and acomodados de manera correcta para su filtrado que hace la capreta anterior
