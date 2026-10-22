# SMART AGRICULTURAL SYSTEM FOR GUJARAT FARMERS
## B.Tech Project Report — Silver Oak University, Ahmedabad

---

## STUDENT INFORMATION

| Field | Details |
|---|---|
| Student Name | JADAV VISHVAJEET |
| Enrollment Number | *(Fill your enrollment number)* |
| Branch | Computer Engineering (CE) |
| Department | Department of Computer Engineering |
| College | College of Technology, Silver Oak University |
| Academic Year | 2026–2027 |
| Submission Month | April 2026 |
| Internal Guide | *(Fill guide name)* |

---

---

# TABLE OF CONTENTS

| Section | Title | Page |
|---|---|---|
| — | Declaration | i |
| — | Acknowledgement | ii |
| — | Abstract | iii |
| — | List of Figures | iv |
| — | List of Tables | v |
| — | List of Abbreviations | vi |
| — | Table of Contents | vii |
| **Chapter 1** | **Introduction** | **1** |
| 1.1 | Background and Motivation | 2 |
| 1.2 | Problem Statement | 3 |
| 1.3 | Objectives of the Project | 4 |
| 1.4 | Scope of the Project | 5 |
| 1.5 | Technology Stack | 6 |
| 1.6 | Organization of the Report | 7 |
| **Chapter 2** | **Literature Review** | **8** |
| 2.1 | Introduction to the Review | 9 |
| 2.2 | AI-Based Crop Recommendation Systems | 9 |
| 2.3 | Plant Disease Detection Using Deep Learning | 10 |
| 2.4 | Smart Irrigation Systems | 11 |
| 2.5 | Agricultural Market Intelligence Systems | 12 |
| 2.6 | Weather-Based Farming Advisory Systems | 13 |
| 2.7 | Research Gap and Contribution of This Project | 14 |
| 2.8 | Summary | 14 |
| **Chapter 3** | **System Analysis** | **15** |
| 3.1 | Study of the Current System | 16 |
| 3.2 | Problems and Weaknesses of the Current System | 17 |
| 3.3 | Requirements of the New System | 18 |
| 3.4 | System Feasibility Analysis | 20 |
| 3.5 | Activity / Process in the Proposed System | 21 |
| 3.6 | Features of the Proposed System | 22 |
| 3.7 | Main Modules / Components | 23 |
| 3.8 | Selection of Technology and Justification | 24 |
| 3.9 | Summary | 24 |
| **Chapter 4** | **System Design** | **25** |
| 4.1 | System Architecture | 26 |
| 4.2 | Module Design | 28 |
| 4.3 | Data Structure Design | 34 |
| 4.4 | Input / Output and Interface Design | 35 |
| 4.5 | Security Design | 36 |
| 4.6 | Summary | 37 |
| **Chapter 5** | **Implementation** | **38** |
| 5.1 | Implementation Platform / Environment | 39 |
| 5.2 | Project Directory Structure | 40 |
| 5.3 | Module Implementation Details | 42 |
| 5.4 | Finding / Results / Outcomes | 50 |
| 5.5 | Result Analysis | 51 |
| 5.6 | Summary | 52 |
| **Chapter 6** | **Testing** | **53** |
| 6.1 | Testing Plan / Strategy | 54 |
| 6.2 | Test Results and Analysis | 55 |
| 6.3 | Summary of Test Results | 60 |
| 6.4 | Testing Notes | 60 |
| **Chapter 7** | **Conclusion and Discussion** | **61** |
| 8.1 | Overall Analysis of Project Viability | 62 |
| 8.2 | Dates of Continuous Evaluation | 63 |
| 8.3 | Problems Encountered and Solutions | 63 |
| 8.4 | Summary of Project Work | 64 |
| 8.5 | Limitations and Future Enhancements | 65 |
| 8.6 | Conclusion | 66 |
| — | **References / Bibliography** | **67** |

---

---

# LIST OF FIGURES

| Figure | Caption | Page |
|---|---|---|
| Fig 1.1 | Technology Stack Overview — Smart Agricultural System | 6 |
| Fig 3.1 | Workflow Diagram — Smart Agricultural System | 21 |
| Fig 4.1 | Layered System Architecture Diagram | 26 |
| Fig 4.2 | Crop Recommendation Module — Processing Flow | 28 |
| Fig 4.3 | Disease Detection Module — Processing Flow | 29 |
| Fig 4.4 | Smart Irrigation — 5-Rule Decision Flowchart | 30 |
| Fig 4.5 | Weather Advisory — Module Flow Diagram | 32 |
| Fig 4.6 | Market Price Module — Processing Flow | 33 |
| Fig 5.1 | Project Directory Structure | 40 |
| Fig 5.2 | Dashboard Screenshot — Live Weather Display | 43 |
| Fig 5.3 | Crop Recommendation Page Screenshot | 44 |
| Fig 5.4 | Disease Detection — Result Page Screenshot | 45 |
| Fig 5.5 | Smart Irrigation — Result with Status Badge Screenshot | 46 |
| Fig 5.6 | Weather Advisory — 7-Day Forecast Screenshot | 47 |
| Fig 5.7 | Market Prices — Trend Chart Screenshot | 48 |

---

---

# LIST OF TABLES

| Table | Caption | Page |
|---|---|---|
| Table 1.1 | Technology Stack — Components and Versions | 6 |
| Table 3.1 | Problems of Current Agricultural Information System | 17 |
| Table 3.2 | Functional Requirements of the Proposed System | 18 |
| Table 3.3 | Non-Functional Requirements | 19 |
| Table 3.4 | Main Modules and Python Files | 23 |
| Table 3.5 | Technology Selection and Justification | 24 |
| Table 4.1 | Irrigation Decision Rules (A–E) Summary | 30 |
| Table 4.2 | Irrigation Method Efficiency Coefficients | 31 |
| Table 4.3 | Growth Stage Multipliers | 31 |
| Table 5.1 | Implementation Environment | 39 |
| Table 5.2 | Module Output — Demo vs Live Mode Comparison | 51 |
| Table 6.1 | Test Cases — Crop Recommendation Module | 55 |
| Table 6.2 | Test Cases — Disease Detection Module | 56 |
| Table 6.3 | Test Cases — Smart Irrigation Module | 57 |
| Table 6.4 | Test Cases — Weather Advisory Module | 58 |
| Table 6.5 | Test Cases — Market Price Module | 59 |
| Table 6.6 | Test Cases — Application Level | 59 |
| Table 6.7 | Summary of Test Results | 60 |
| Table 8.1 | Problems Encountered and Solutions Applied | 63 |
| Table 8.2 | Limitations and Proposed Future Enhancements | 65 |

---

---

# LIST OF ABBREVIATIONS

| Abbreviation | Full Form |
|---|---|
| AI | Artificial Intelligence |
| ML | Machine Learning |
| CNN | Convolutional Neural Network |
| RF | Random Forest |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| HTTP | Hypertext Transfer Protocol |
| JSON | JavaScript Object Notation |
| HTML | Hypertext Markup Language |
| CSS | Cascading Style Sheets |
| JS | JavaScript |
| OWM | OpenWeatherMap |
| SMTP | Simple Mail Transfer Protocol |
| NPK | Nitrogen, Phosphorus, Potassium |
| MSP | Minimum Support Price |
| NDVI | Normalized Difference Vegetation Index |
| IoT | Internet of Things |
| UI | User Interface |
| WSGI | Web Server Gateway Interface |
| MobileNetV2 | Mobile Network Version 2 (Lightweight CNN architecture by Google) |
| PKL | Pickle file (serialized Python object) |
| H5 | HDF5 file format (Keras model storage) |
| SVM | Support Vector Machine |
| LSTM | Long Short-Term Memory (Recurrent Neural Network) |
| PWA | Progressive Web Application |
| ETc | Crop Evapotranspiration |
| KVK | Krishi Vigyan Kendra (Farm Science Centre) |

---

---

*(The full chapter content follows in individual chapter files. See files 03 through 10 in this project_report folder.)*

---

> **NOTE FOR PRINTING:**
> This combined file provides the Table of Contents, List of Figures, List of Tables, and List of Abbreviations.
> For the complete report, combine the content from all files in this folder in order:
> 1. `01_cover_page.md`
> 2. `02_certificates_declaration_abstract.md`
> 3. `00_COMPLETE_REPORT.md` (this file — front matter)
> 4. `03_chapter1_introduction.md`
> 5. `04_chapter2_literature_review.md`
> 6. `05_chapter3_system_analysis.md`
> 7. `06_chapter4_system_design.md`
> 8. `07_chapter5_implementation.md`
> 9. `08_chapter6_testing.md`
> 10. `09_chapter7_conclusion.md`
> 11. `10_references.md`
