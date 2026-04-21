import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("../data/dataset.csv")

# FIX: handle missing values
df = df.fillna(0)

print("Dataset loaded successfully!")
print("\nColumns:\n", df.columns)

# -------------------------------
# SELECT FEATURES 
# -------------------------------
features = [
    "is_moas",
    "moas_duration",
    "edit_distance",
    "prepending",
    "local_hege_freq",
    "global_hege_freq"
]

X = df[features]

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X = scaler.fit_transform(X)

y = df["category"]

# -------------------------------
# TRAIN / TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# -------------------------------
# MODELS
# -------------------------------
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier(n_neighbors=3),
    "Random Forest": RandomForestClassifier(),
    "Decision Tree": DecisionTreeClassifier(),
}

results = {}

# -------------------------------
# TRAIN & EVALUATE
# -------------------------------
for name, model in models.items():
    print("\n========================")
    print(f"Model: {name}")
    print("========================")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    results[name] = acc

    print("Accuracy:", acc)
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # Save Confusion Matrix
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred)
    plt.title(f"{name} Confusion Matrix")
    plt.savefig(f"{name}_confusion_matrix.png")
    plt.clf()

# -------------------------------
# GRAPH 1: MODEL COMPARISON
# -------------------------------
model_names = list(results.keys())
accuracies = list(results.values())

plt.figure()
plt.bar(model_names, accuracies)
plt.xlabel("Models")
plt.ylabel("Accuracy")
plt.title("Model Accuracy Comparison")
plt.xticks(rotation=45)
plt.ylim(0, 1)
plt.savefig("model_comparison.png")
plt.clf()

print("Saved: model_comparison.png")

# -------------------------------
# GRAPH 2: CATEGORY DISTRIBUTION
# -------------------------------
df["category"].value_counts().plot(kind="bar")
plt.title("Category Distribution")
plt.xlabel("Category")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.savefig("category_distribution.png")
plt.clf()

print("Saved: category_distribution.png")

# -------------------------------
# GRAPH 3: FEATURE DISTRIBUTIONS
# -------------------------------
for feature in features:
    plt.figure()
    df[feature].hist(bins=20)
    plt.title(f"{feature} Distribution")
    plt.xlabel(feature)
    plt.ylabel("Frequency")
    plt.savefig(f"{feature}_distribution.png")
    plt.clf()

print("Saved: feature distribution graphs")

# -------------------------------
# GRAPH 4: FEATURE IMPORTANCE (RF)
# -------------------------------
rf = RandomForestClassifier()
rf.fit(X_train, y_train)

importances = rf.feature_importances_

plt.figure()
plt.bar(features, importances)
plt.xticks(rotation=45)
plt.title("Feature Importance (Random Forest)")
plt.savefig("feature_importance.png")
plt.clf()

print("Saved: feature_importance.png")