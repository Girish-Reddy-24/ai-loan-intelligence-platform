import shap
def get_shap_explanation(model, df):

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(df)

    values = shap_values[0]
    feature_names = df.columns

    explanation = []

    for i in range(len(values)):
        explanation.append({
            "feature": feature_names[i],
            "impact": float(values[i])
        })

    explanation = sorted(explanation, key=lambda x: abs(x["impact"]), reverse=True)

    return explanation[:5]