import pandas as pd
import matplotlib.pyplot as plt

# Load Dataset
df = pd.read_csv("road_damage.csv")

# Show Dataset
print(df.head())

# -----------------------------
# Total Damage Count
# -----------------------------
damage_count = df['damage_type'].value_counts()

print("\nDamage Count:")
print(damage_count)

# -----------------------------
# Severity Analysis
# -----------------------------
severity_count = df['severity'].value_counts()

print("\nSeverity Count:")
print(severity_count)

# -----------------------------
# Plot Damage Types
# -----------------------------
plt.figure(figsize=(8,5))
damage_count.plot(kind='bar')

plt.title("Road Damage Types")
plt.xlabel("Damage Type")
plt.ylabel("Count")

plt.show()

# -----------------------------
# Plot Severity
# -----------------------------
plt.figure(figsize=(8,5))
severity_count.plot(kind='pie', autopct='%1.1f%%')

plt.title("Damage Severity Distribution")

plt.show()
