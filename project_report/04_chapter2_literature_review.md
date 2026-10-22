# CHAPTER 2 — LITERATURE REVIEW

---

## 2.1   Introduction to the Review

This chapter presents a comprehensive review of existing research and systems related to smart agriculture, crop recommendation using machine learning, plant disease detection using deep learning, smart irrigation systems, and agricultural market intelligence platforms. The review identifies the strengths and limitations of existing approaches and establishes the research gap that this project addresses.

---

## 2.2   AI-Based Crop Recommendation Systems

Crop recommendation using machine learning has received considerable research attention in recent years. Researchers have proposed various models based on soil parameters, weather data, and historical yield records.

**Doshi et al. (2018)** proposed a crop recommendation system using Naive Bayes, Support Vector Machine (SVM), and Random Forest classifiers trained on NPK values, temperature, humidity, pH, and rainfall. Their study found that Random Forest achieved the highest accuracy of 99.3% compared to other models on the Crop Recommendation Dataset from Kaggle.

**Pudumalar et al. (2017)** developed an ensemble crop recommendation system combining multiple classifiers. They concluded that ensemble methods outperform single classifiers, particularly when trained on multi-parameter soil datasets.

**Gandhi et al. (2016)** focused specifically on Gujarat-region crops and proposed a rule-based recommendation system considering soil type, water availability, and seasonal factors. Their work highlighted the importance of region-specific parameter weighting, which influenced the design of the rule-based fallback engine in this project.

The present system improves upon these works by incorporating **15 input parameters** including organic carbon, soil texture (sand/silt/clay percentages), irrigation type, water source, and water salinity — parameters rarely considered in prior work.

---

## 2.3   Plant Disease Detection Using Deep Learning

Deep learning-based plant disease detection has emerged as a powerful alternative to traditional laboratory-based diagnosis methods.

**Mohanty et al. (2016)** published a landmark study using the PlantVillage dataset (54,306 images, 38 disease classes) and trained deep CNN models including AlexNet and GoogLeNet. They achieved up to 99.35% accuracy in controlled conditions, demonstrating the feasibility of image-based disease diagnosis.

**Ramcharan et al. (2017)** applied a MobileNet-based transfer learning approach for cassava disease detection using field photographs. They demonstrated that lightweight MobileNet architectures could achieve near-AlexNet accuracy with significantly fewer parameters, making them suitable for mobile deployment.

**Ferentinos (2018)** explored multiple CNN architectures for plant disease detection and concluded that AlexNet, GoogLeNet, and VGG-16 all performed well, but transfer learning from pre-trained ImageNet models consistently outperformed models trained from scratch.

The present system uses **MobileNetV2** — an improved version of MobileNet that uses inverted residuals and linear bottlenecks — for efficient, accurate leaf disease detection with an input size of 224×224 pixels and MobileNetV2-specific preprocessing (pixel values normalized to [-1, 1]).

---

## 2.4   Smart Irrigation Systems

Precision irrigation management using sensor data and AI has been an active research area aimed at reducing water waste while maintaining crop yield.

**Goap et al. (2018)** proposed an IoT-based smart irrigation system using soil moisture sensors, weather data, and a Random Forest model to predict irrigation needs. Their system achieved 94% prediction accuracy and reduced water consumption by 40% compared to traditional flood irrigation.

**Munir et al. (2021)** developed a rule-based smart irrigation decision support system for small-scale farmers, arguing that pure rule-based deterministic engines are more transparent, auditable, and reliable for agricultural advisory than black-box ML models — an argument that directly supports the design choice made in this project.

**Goldstein et al. (2018)** studied various crop evapotranspiration (ET) models and concluded that combining soil moisture data with crop growth stage coefficients (Kc factors) and weather parameters produces the most accurate irrigation scheduling outcomes.

The irrigation module in this project implements a **deterministic multi-rule engine** (Rules A–E) based on these principles, incorporating crop-specific moisture thresholds, growth stage factors, soil type factors, irrigation method efficiency coefficients, and rainfall probability assessment.

---

## 2.5   Agricultural Market Intelligence Systems

Access to real-time market price information is critical for empowering farmers to make informed selling decisions.

**Bhimrao et al. (2019)** analyzed the impact of digital market information on farmer income and found that farmers with access to real-time mandi prices received an average of 12–15% higher prices compared to those who relied on intermediaries.

**Shalendra et al. (2020)** proposed an agricultural price prediction model using LSTM (Long Short-Term Memory) networks trained on historical mandi price data. They achieved reasonable short-term prediction accuracy (MAPE < 8%) for major commodities including wheat, cotton, and tomato.

The present system integrates the **Agmarknet API (data.gov.in)** for live Gujarat mandi prices and provides a 7-day price trend visualization with an AI-based sell/wait recommendation engine based on trend direction, price relative to MSP, and market comparison — a practical, interpretable approach over pure predictive models.

---

## 2.6   Weather-Based Farming Advisory Systems

**Sharma et al. (2017)** developed a crop weather advisory system for Indian farmers that used OpenWeatherMap API data to generate text-based advisories for irrigation, pest risk, and harvest planning. Their evaluation with 120 farmers in Rajasthan showed a 23% reduction in unnecessary irrigation events.

**Kale et al. (2019)** proposed a bilingual (Hindi-English) agricultural advisory chatbot for smallholder farmers, demonstrating the importance of native language support in technology adoption by rural communities.

The weather advisory module in this project builds on these findings, delivering **bilingual (English + Gujarati)** advisories covering irrigation scheduling, pest risk assessment, and farm operation tips, along with a 7-day forecast display.

---

## 2.7   Research Gap and Contribution of This Project

The review reveals the following gaps in existing systems:

1. Most systems address only one agricultural problem domain; **no single integrated system** covers crop recommendation, disease detection, irrigation, market prices, and weather advisory together.
2. Existing systems often require **expensive hardware** (IoT sensors, dedicated servers, databases) or depend on mobile apps with limited accessibility.
3. Very few systems provide **regional localization** — bilingual content, Gujarat-specific crops, mandi data, and agronomic parameters suited to Gujarat's agro-climatic conditions.
4. Most ML-based systems lack transparent, **auditable decision rules** — farmers and extension workers cannot understand *why* a recommendation was made.

This project addresses all four gaps by delivering an integrated, lightweight, database-free, bilingual, region-specific smart agricultural platform with transparent decision logic.

---

## 2.8   Summary

This chapter reviewed major related works in crop recommendation, disease detection, smart irrigation, market price intelligence, and weather-based advisories. The review established the research gap and motivated the design decisions made in this project, including the choice of Random Forest for crop recommendation, MobileNetV2 for disease detection, a deterministic rule engine for irrigation, and the Agmarknet API for market prices.

---
