# ENADE Performance Prediction

This project investigates whether variables from ENADE microdata can be used to
predict student and course performance using classical machine learning models.

The data used in this study is derived from the same ENADE microdata employed in
the Ontology_ENADE project, which focuses on semantic modeling of educational data.
In this work, these data are explored from a predictive analysis perspective.

📄 Read this README in Portuguese: README.pt-br.md

## Objective
Evaluate the predictive capacity of institutional, course-level and student-level
variables from ENADE microdata.

## Research Questions
- Is it possible to predict student performance categories (low/medium/high)?
- Which variables are most relevant to ENADE performance?
- Can the results support academic reinforcement strategies?

## Dataset
ENADE microdata provided by INEP, using the same data source adopted in the
Ontology_ENADE project.  
Raw data is not included in this repository.

## Methodology
- Data preprocessing and feature selection
- Supervised learning (classification and regression)
- Baseline models: Logistic Regression, Decision Tree and Random Forest
- Evaluation metrics: Accuracy, F1-score and Confusion Matrix

## Project Status
Initial setup and exploratory analysis.

## Related Work
Previous work has explored the use of ontologies to semantically organize ENADE
microdata and support educational analysis. One example is the Ontology_ENADE
project, which focuses on structuring ENADE data using semantic web technologies.

This project differs by focusing on predictive analysis using machine learning
models, rather than semantic modeling or recommendation systems.

Reference:  
https://github.com/Ivanylson/Ontology_ENADE
