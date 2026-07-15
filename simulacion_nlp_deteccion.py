"""
Simulación completa de Detección de Discurso Malicioso con NLP
===============================================================
Usa scikit-learn, TF-IDF, y clasificadores para detectar toxicidad.
Incluye: dataset sintético, entrenamiento, evaluación, gráficas y demo.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 1. DATASET SINTÉTICO (simula comentarios reales)
# ============================================================
print("=" * 60)
print("CYBERGUARD - Simulación NLP de Detección de Discurso Malicioso")
print("=" * 60)

toxic_phrases = [
    "eres un idiota inutil",
    "vete a la mierda",
    "te voy a matar",
    "odio a tu raza",
    "tu religion es una basura",
    "muerete enfermo",
    "no vales nada estupido",
    "los inmigrantes deberian morir",
    "te romperé la cara",
    "puto imbecil",
    "eres una verguenza",
    "que asco das",
    "todos ustedes son escoria",
    "te voy a encontrar y te voy a destruir",
    "zorra estupida",
    "mereces morir",
    "tu opinion no importa inutil",
    "eso es cosa de mariquitas",
    "vuelve a tu pais",
    "deberian exterminarlos a todos",
    "me das asco",
    "callate idiota",
    "pe pe pe perra",
    "que muera todo tu linaje",
    "no sirves para nada fracasado",
]

neutral_phrases = [
    "me gusta tu opinion",
    "gracias por tu ayuda",
    "buen trabajo en el proyecto",
    "esta informacion me fue util",
    "que bonito dia hace hoy",
    "me encanta la musica clasica",
    "el clima esta agradable",
    "felicidades por tu exito",
    "disfruta tu fin de semana",
    "la comida estuvo deliciosa",
    "aprecio tu punto de vista",
    "buena suerte con tu examen",
    "el libro que recomiendas es interesante",
    "me alegra verte feliz",
    "gracias por compartir tus conocimientos",
    "eres muy talentoso en lo que haces",
    "que buen chiste",
    "me encanta esta cancion",
    "la pelicula es fascinante",
    "te deseo lo mejor en tu viaje",
    "puedo contar contigo",
    "me encanta programar",
    "la tecnologia nos conecta",
    "un saludo cordial para todos",
    "que tengas un excelente dia",
]

np.random.seed(42)
toxic_labels = [1] * len(toxic_phrases)
neutral_labels = [0] * len(neutral_phrases)

texts = toxic_phrases + neutral_phrases
labels = toxic_labels + neutral_labels

df = pd.DataFrame({"texto": texts, "toxico": labels})
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nDataset sintético creado: {len(df)} muestras")
print(f"  - Tóxicos: {df['toxico'].sum()}")
print(f"  - Neutrales: {len(df) - df['toxico'].sum()}")
print(f"\nEjemplos de datos:")
for _, row in df.head(8).iterrows():
    print(f"  {'⚠️' if row['toxico'] else '✅'} {row['texto']}")

# ============================================================
# 2. TF-IDF VECTORIZATION
# ============================================================
print("\n" + "=" * 60)
print("2. EXTRACCIÓN DE CARACTERÍSTICAS (TF-IDF)")
print("=" * 60)

vectorizer = TfidfVectorizer(
    max_features=500,
    ngram_range=(1, 2),
    stop_words=["el", "la", "los", "las", "un", "una", "y", "e", "de", "del"],
    max_df=0.9,
    min_df=0.01,
)
X = vectorizer.fit_transform(df["texto"])
y = df["toxico"]

print(f"  Matriz TF-IDF: {X.shape[0]} documentos x {X.shape[1]} términos")
print(f"\n  Top 10 términos con mayor peso TF-IDF:")
feature_names = vectorizer.get_feature_names_out()
tfidf_sums = X.sum(axis=0).A1
top_indices = tfidf_sums.argsort()[-10:][::-1]
for idx in top_indices:
    print(f"    {feature_names[idx]:20s} -> {tfidf_sums[idx]:.2f}")

# ============================================================
# 3. ENTRENAMIENTO
# ============================================================
print("\n" + "=" * 60)
print("3. ENTRENAMIENTO DE MODELOS")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

print(f"  Train: {X_train.shape[0]} samples")
print(f"  Test:  {X_test.shape[0]} samples")

models = {
    "Regresión Logística": LogisticRegression(max_iter=1000, random_state=42),
    "SVM (Lineal)": SVC(kernel="linear", probability=True, random_state=42),
    "SVM (RBF)": SVC(kernel="rbf", probability=True, random_state=42),
}

results = []
trained_models = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    trained_models[name] = {"model": model, "y_pred": y_pred, "y_prob": y_prob}
    results.append(
        {"Modelo": name, "Accuracy": acc, "Precision": prec, "Recall": rec, "F1-Score": f1}
    )

    print(f"\n  {name}:")
    print(f"    Accuracy:  {acc:.3f}")
    print(f"    Precision: {prec:.3f}")
    print(f"    Recall:    {rec:.3f}")
    print(f"    F1-Score:  {f1:.3f}")
    print(f"\n    Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Neutral", "Tóxico"]))

results_df = pd.DataFrame(results)
print(f"\n  Resumen comparativo:")
print(results_df.to_string(index=False))

# ============================================================
# 4. VISUALIZACIONES
# ============================================================
print("\n" + "=" * 60)
print("4. GENERANDO VISUALIZACIONES...")
print("=" * 60)

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("CyberGuard - Análisis de Detección de Discurso Malicioso", fontsize=16, fontweight="bold")

# 4a. Bar chart: comparación de métricas
ax1 = axes[0, 0]
x = np.arange(len(results))
width = 0.2
metrics_data = {"Accuracy": [r["Accuracy"] for r in results],
                "Precision": [r["Precision"] for r in results],
                "Recall": [r["Recall"] for r in results],
                "F1-Score": [r["F1-Score"] for r in results]}
colors = ["#ff6b35", "#4ecdc4", "#45b7d1", "#96ceb4"]
for i, (metric, values) in enumerate(metrics_data.items()):
    bars = ax1.bar(x + i * width, values, width, label=metric, color=colors[i], edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                 f"{val:.2f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

ax1.set_xticks(x + width * 1.5)
ax1.set_xticklabels([r["Modelo"] for r in results], fontsize=9)
ax1.set_ylim(0, 1.15)
ax1.set_ylabel("Puntaje")
ax1.set_title("Comparación de Modelos", fontweight="bold")
ax1.legend(fontsize=8, loc="lower right")
ax1.set_facecolor("#f8f9fa")
ax1.grid(axis="y", alpha=0.3)

# 4b. Confusion Matrix - Logistic Regression
ax2 = axes[0, 1]
lr_result = trained_models["Regresión Logística"]
cm = confusion_matrix(y_test, lr_result["y_pred"])
ConfusionMatrixDisplay(cm, display_labels=["Neutral", "Tóxico"]).plot(ax=ax2, cmap="OrRd", values_format="d")
ax2.set_title("Matriz de Confusión\nRegresión Logística", fontweight="bold")

# 4c. ROC Curve - all models
ax3 = axes[0, 2]
roc_colors = ["#ff6b35", "#4ecdc4", "#45b7d1"]
for i, (name, result) in enumerate(trained_models.items()):
    viz = RocCurveDisplay.from_predictions(y_test, result["y_prob"], ax=ax3, name=name)
    viz.line_.set_color(roc_colors[i])
    viz.line_.set_linewidth(2)
ax3.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Aleatorio")
ax3.set_title("Curvas ROC", fontweight="bold")
ax3.legend(fontsize=9, loc="lower right")
ax3.set_facecolor("#f8f9fa")
ax3.grid(alpha=0.3)

# 4d. Distribución de clases
ax4 = axes[1, 0]
classes = ["Neutral", "Tóxico"]
counts = df["toxico"].value_counts().sort_index()
colors_pie = ["#4ecdc4", "#ff6b35"]
wedges, texts, autotexts = ax4.pie(
    counts, labels=classes, autopct="%1.1f%%", colors=colors_pie,
    startangle=90, explode=(0.03, 0.03), shadow=True,
    textprops={"fontweight": "bold"}
)
ax4.set_title("Distribución de Clases en Dataset", fontweight="bold")

# 4e. Palabras más importantes para clasificar toxicidad (coeficientes LR)
ax5 = axes[1, 1]
lr_model = trained_models["Regresión Logística"]["model"]
coef = lr_model.coef_.flatten()
top_n = 15
top_positive_idx = coef.argsort()[-top_n:][::-1]
top_negative_idx = coef.argsort()[:top_n]
top_words_pos = [(feature_names[i], coef[i]) for i in top_positive_idx]
top_words_neg = [(feature_names[i], coef[i]) for i in top_negative_idx]

all_words = top_words_pos + top_words_neg
words_labels = [w for w, _ in all_words]
words_values = [v for _, v in all_words]
colors_bar = ["#e71d36"] * top_n + ["#00e676"] * top_n

bars = ax5.barh(range(len(all_words)), words_values, color=colors_bar, edgecolor="white", linewidth=1)
ax5.set_yticks(range(len(all_words)))
ax5.set_yticklabels(words_labels, fontsize=9)
ax5.axvline(0, color="black", linewidth=0.5)
ax5.set_xlabel("Peso del coeficiente")
ax5.set_title(f"Top {top_n} palabras más influyentes\n(Regresión Logística)", fontweight="bold")
ax5.set_facecolor("#f8f9fa")
ax5.grid(axis="x", alpha=0.3)

# 4f. Distribución de longitudes de texto
ax6 = axes[1, 2]
df["longitud"] = df["texto"].apply(len)
toxic_lengths = df[df["toxico"] == 1]["longitud"]
neutral_lengths = df[df["toxico"] == 0]["longitud"]
ax6.hist(toxic_lengths, bins=12, alpha=0.7, label="Tóxico", color="#e71d36", edgecolor="white")
ax6.hist(neutral_lengths, bins=12, alpha=0.5, label="Neutral", color="#00e676", edgecolor="white")
ax6.set_xlabel("Longitud del texto (caracteres)")
ax6.set_ylabel("Frecuencia")
ax6.set_title("Distribución de longitud de textos", fontweight="bold")
ax6.legend()
ax6.set_facecolor("#f8f9fa")
ax6.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("cyberguard_analisis_modelos.png", dpi=150, bbox_inches="tight")
plt.show()
print("  Gráfico guardado: cyberguard_analisis_modelos.png")

# ============================================================
# 5. CLASIFICADOR EN ACCIÓN (Demo en tiempo real)
# ============================================================
print("\n" + "=" * 60)
print("5. DEMO: CLASIFICADOR EN TIEMPO REAL")
print("=" * 60)

best_model_name = results_df.sort_values("F1-Score", ascending=False).iloc[0]["Modelo"]
best_model = trained_models[best_model_name]["model"]
print(f"  Usando el mejor modelo: {best_model_name}\n")

test_phrases = [
    "Eres una persona increíble, gracias por tu ayuda",
    "Te voy a romper la cara idiota",
    "Me gusta mucho tu nuevo proyecto",
    "Vete a la mierda y no vuelvas nunca",
    "Que tengas un excelente día",
    "Los inmigrantes deberían ser eliminados",
    "Aprecio mucho tu trabajo en este equipo",
    "Eres un inútil que no sirve para nada",
    "La comida de hoy estuvo deliciosa",
    "Mereces morir por lo que hiciste",
]

print(f"{'Frase':<55} {'Predicción':<15} {'Confianza':<10}")
print("-" * 80)
for phrase in test_phrases:
    vec = vectorizer.transform([phrase])
    prob = best_model.predict_proba(vec)[0]
    pred = best_model.predict(vec)[0]
    confidence = max(prob)
    label = "⚠️ TÓXICO" if pred == 1 else "✅ SEGURO"
    print(f"{phrase:<55} {label:<15} {confidence:.2%}")

# ============================================================
# 6. RESUMEN FINAL
# ============================================================
print("\n" + "=" * 60)
print("RESUMEN Y CONCLUSIONES")
print("=" * 60)
print(f"""
✅ Dataset sintético con {len(df)} ejemplos ({df['toxico'].sum()} tóxicos, {len(df) - df['toxico'].sum()} neutrales)
✅ Vectorización TF-IDF con {X.shape[1]} términos
✅ Entrenamiento de {len(models)} modelos: {', '.join(models.keys())}
✅ Evaluación completa con métricas y visualizaciones
✅ Demo interactiva con {len(test_phrases)} frases de prueba

{'═' * 60}
CONCLUSIÓN: La detección de discurso malicioso con NLP
es factible usando técnicas clásicas de Machine Learning.
Combinando TF-IDF + Regresión Logística se obtienen
resultados sólidos para clasificación de toxicidad.
{'═' * 60}

📊 Gráfico guardado: cyberguard_analisis_modelos.png
💡 Siguiente paso: Probar con datasets reales como Jigsaw Toxic Comment
   o utilizar transformers (BERT) para mejor precisión.
""")
