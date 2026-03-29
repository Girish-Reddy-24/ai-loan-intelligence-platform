def get_shap_explanation(model, df):
    try:
        import shap

        explainer = shap.Explainer(model)
        shap_values = explainer(df)

        values = shap_values.values[0]
        features = df.columns

        result = []
        for i in range(len(features)):
            result.append({
                "feature": features[i],
                "impact": float(values[i])
            })

        # return top 5 important features
        result = sorted(result, key=lambda x: abs(x["impact"]), reverse=True)[:5]

        return result

    except Exception as e:
        print("SHAP not available:", e)
        return []