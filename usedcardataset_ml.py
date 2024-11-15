# -*- coding: utf-8 -*-
"""UsedCarDataset_ML.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bDDZfBKQBOiX8tWCM-Mkf0ohChnXlDhN

## IT461 Practical Machine learning
### Used Car Prices Dataset

*Project Motivation:*

we want to develop a predictive model that determines consumer car preferences based on a comparison of key car attributes, such as price, mileage, model year, brand popularity, accident history, and fuel type. By building and training models to analyze differences between paired cars. Our project aims to identify the likelihood of one car being preferred over another, providing insights into the factors that influence car purchasing decisions.

*Prepared by:*

Jory Alharbi	443200984

Majd Aljuraysi	443200637

Deem Alshaye	443200583

Norah Mohammed Alwohaibi 	443200753

Razan Aldakhil	443201096


*dataset source:*
https://www.kaggle.com/datasets/taeefnajib/used-car-price-prediction-dataset
"""

from google.colab import drive
drive.mount('/content/drive')
directory_path = '/content/drive/MyDrive/'
file_name = "/content/used_cars.csv"

!pip install scikeras tensorflow numpy
!pip install scikeras tensorflow numpy
!pip install scikeras

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import itertools
from scikeras.wrappers import KerasClassifier
from sklearn.model_selection import GridSearchCV
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam, SGD
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import itertools
import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

df= pd.read_csv("/content/drive/My Drive/used_cars.csv")

df.head(5)

"""## 1- Data cleaning and Inspection

we will start by cleaning or dataset to prepare it for further work, starting by checking for missing values

### Missing values
"""

missing_values = df.isnull().sum()

# Display columns with missing values
print(missing_values[missing_values > 0])

"""since these features are signaficant for the user, and inflaunce whether the user would by the car or not, we cant just remove them from our dataset, we will fill these missing values with either the mode, mean or most common type or using clusters with the nearest values in the cluster"""

df['fuel_type'].unique()

"""fuel type has "–" and "not supported" and needs to be handeled, we will use numpy to solve this, np.nan represents a "Not a Number" value, which is useful for handling missing values."""

df['fuel_type'] = df['fuel_type'].replace(['–', 'not supported'], np.nan)

most_common_fuel_type = df['fuel_type'].mode()[0]
df['fuel_type'].fillna(most_common_fuel_type, inplace=True)

df['clean_title'].fillna('no', inplace=True)

df['accident'].unique()

# Fill missing values in the 'accident' column with 'None reported'
df['accident'] = df['accident'].fillna('None reported')

missing_values = df.isnull().sum()

# Display columns with missing values
print(missing_values[missing_values > 0])

# Descriptive Statistics
print(df.describe())

"""### duplicate rows"""

df_duplicates = df[df.duplicated()]

num_duplicates = df_duplicates.shape[0]
print(f"Number of duplicate rows: {num_duplicates}")

"""there are no duplicates rows in our dataset so it doesnt require further investigating

###removing unwanted characters

the milage and the price have "mi" and "$" in each data entry, we will remove them to work better with them
"""

# Data Cleaning: Remove 'mi.' from 'milage' and '$' from 'price', then convert to numeric
df['milage'] = df['milage'].str.replace(' mi.', '').str.replace(',', '').astype(float)
df['price'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)

"""## 2- Preprocessing

For the preprocessing section, we’ll focus on encoding categorical features and normalizing numerical ones to ensure the model performs optimally

### Encoding
"""

df['clean_title'].unique()

df['brand'].unique()

# Encode 'clean_title' column with 1 for 'Yes' and 0 for 'Missing'
df['clean_title_ecnoded'] = df['clean_title'].map({
    'Yes': 1,
    'Missing': 0
}).fillna(0).astype(int)

df['fuel_type_encoded'] = df['fuel_type'].astype('category').cat.codes

df['accident_encoded'] = df['accident'].map({
    'At least 1 accident or damage reported': 1,
    'None reported': 0
})

scaler = MinMaxScaler()

# Apply Min-Max Scaling to 'price' and 'milage'
df[['price_norm', 'milage_norm']] = scaler.fit_transform(df[['price', 'milage']])

"""###feature engineering

Feature engineering is a critical step in data preprocessing that involves transforming raw data into meaningful features to improve model performance. This process helps highlight important patterns, reduces noise, and allows machine learning models to better understand the underlying data. Here are some key feature engineering techniques applied to the dataset:

1- Binning/Grouping Numerical Features

Binning Mileage: Instead of using raw mileage,we will  group cars into mileage bins (e.g., 0-25,000 miles, 25,001-50,000 miles, etc.) to reduce the variability and make the model capture trends better.
"""

mileage_bins = [0, 25000, 50000, 75000, 100000, 150000, 200000]
df['mileage_bin'] = pd.cut(df['milage'], bins=mileage_bins, labels=['0-25k', '25k-50k', '50k-75k', '75k-100k', '100k-150k', '150k+'])

"""Binning Price: Group cars into price ranges (e.g., budget, mid-range, luxury) based on thresholds."""

price_bins = [0, 20000, 50000, 100000, 200000, df['price'].max()]
df['price_category'] = pd.cut(df['price'], bins=price_bins, labels=['Budget', 'Mid-range', 'Premium', 'Luxury', 'Super Luxury'])

# Encode 'price_category' column
df['price_category_encoded'] = df['price_category'].astype('category').cat.codes

# Encode 'mileage_bin' column
df['mileage_bin_encoded'] = df['mileage_bin'].astype('category').cat.codes

"""2- Creating new features

Brand Popularity
Creating a feature that represents the popularity of a car brand by counting how many cars of each brand are in the dataset. Popular brands might have higher resale values.
"""

df['brand_popularity'] = df['brand'].map(df['brand'].value_counts())

"""Create a feature that represents the age of a car by calculating the difference between the current year and the car's model year. Older cars tend to have different pricing and usage patterns compared to newer models, and the age feature helps capture this information."""

df['car_age'] = 2024 - df['model_year']

# Check for zeros in the car_age column
if (df['car_age'] == 0).any():
    # Optional: Drop rows with zero car_age or handle as needed
    df = df[df['car_age'] != 0]  # Drop rows with zero car_age

has_zeros = (df['car_age'] == 0).any()
print(f"Are there any zeros in 'car_age'? {has_zeros}")

"""3- Interaction Features

Mileage to Age Ratio: A feature that represents how much the car has been driven relative to its age. This can provide insight into whether the car is heavily or lightly used.
"""

df['mileage_to_age_ratio'] = df['milage'] / df['car_age']

"""Price-to-Age Ratio: This feature would capture how expensive the car is relative to its age, helping to differentiate between cheaper older cars and expensive older models."""

df['price_to_age_ratio'] = df['price'] / df['car_age']

# Define the categories with a specific order
ordered_categories = ['Budget', 'Mid-range', 'Premium', 'Luxury', 'Super Luxury']

# Create a categorical series with ordered categories and encode
df['encoded_price_category'] = pd.Categorical(df['price_category'], categories=ordered_categories, ordered=True).codes

# Display the DataFrame with the encoded column

label_encoder = LabelEncoder()
df['encoded_transmission'] = label_encoder.fit_transform(df['transmission'])

df['brand'].unique()

df['encoded_brand'] = label_encoder.fit_transform(df['brand'])

df.head(5)

"""## 3- EDA

Visualizing Data Distributions
"""

# Price Distribution
plt.figure(figsize=(10, 6))
sns.histplot(df['price'], bins=50, kde=True)
plt.title('Distribution of Car Prices')
plt.xlabel('Price ($)')
plt.ylabel('Frequency')
plt.show()

"""The output of the **car price distribution plot** shows the following:

- **Most car prices** are concentrated on the left side of the graph, close to \$0, with a high frequency of cars priced below \$100,000.
- The **peak** at the beginning indicates that a large number of cars have prices within a lower range (likely between \$10,000 and \$50,000).
- There are a few **outliers**—cars priced well over \$1 million, but these are very rare, as shown by the flat, extended tail on the right side of the plot.

This type of distribution is **right-skewed** (positively skewed), meaning there are a few extremely high prices that stretch the distribution toward higher values, but most cars are priced lower.

Data visualization

Distribution of Car Mileage
"""

plt.figure(figsize=(10, 6))
sns.histplot(df['milage'], bins=50, kde=True)
plt.title('Distribution of Car Mileage')
plt.xlabel('Mileage (mi)')
plt.ylabel('Frequency')
plt.show()

"""The graph shows the distribution of car mileage. It has a clear downward trend, indicating that cars with lower mileage are much more common than cars with higher mileage.

The graph starts with a tall peak on the left side, representing a large number of cars with relatively low mileage, likely newer or well-maintained vehicles.

As the mileage increases towards the right side of the graph, the number of cars with that mileage decreases rapidly. This reflects the reality that as cars are driven and accumulate more miles over time, there are fewer and fewer cars with higher mileage.

The shape of the graph resembles an exponential curve, which is a common way to model this kind of decreasing distribution. It shows that low-mileage cars are very common, while high-mileage cars become increasingly rare.

Mileage vs Price
"""

plt.figure(figsize=(10, 6))
sns.scatterplot(x=df['milage'], y=df['price'])
plt.title('Mileage vs Price')
plt.xlabel('Mileage (mi)')
plt.ylabel('Price ($)')
plt.show()

"""This scatter plot shows that cars with more miles tend to cost less:

Low mileage cars (under 50,000 miles) generally have higher prices.
Higher mileage cars (above 100,000 miles) mostly have lower prices.
There are a few expensive outliers (over $1 million), likely luxury or rare cars, that don't follow this trend.
 more mileage = lower price, but some special cars are priced high despite their mileage.

Model Year and Mileage Insights
"""

# Correlation analysis
price_model_year_corr = df[['model_year', 'price']].corr().iloc[0, 1]

plt.figure(figsize=(10, 6))
sns.scatterplot(x=df['model_year'], y=df['price'])
plt.title('Price vs Model Year')
plt.xlabel('Model Year')
plt.ylabel('Price ($)')
plt.show()

"""Positive Correlation: There is a general positive trend where newer cars (more recent model years) tend to have higher prices.

Outliers: The outliers in the graph suggest that for some model years, certain cars can be significantly more expensive than average, likely due to their luxury status, rarity, or other factors.
This graph shows how car prices are largely influenced by the model year, with newer cars generally costing more, but with several high-priced outliers skewing the overall distribution.

Accident History and Its Impact on Car Prices
"""

# Grouping by accident history and getting the average price
accident_price_mean = df.groupby('accident')['price'].mean()

plt.figure(figsize=(10, 6))
sns.barplot(x=accident_price_mean.index, y=accident_price_mean.values)
plt.title('Impact of Accident History on Car Prices')
plt.xlabel('Accident History')
plt.ylabel('Average Price ($)')
plt.show()

"""This graph clearly shows that accident history has a strong negative impact on car prices, with cars without accidents being valued significantly higher than those with reported damage.

Count of Cars by Brand
"""

plt.figure(figsize=(12, 6))
sns.countplot(data=df, x='brand', order=df['brand'].value_counts().index)
plt.title('Count of Cars by Brand')
plt.xlabel('Brand')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

"""This bar chart displays the count of cars for each brand in the dataset. The bars represent the number of listings available per brand, sorted in descending order. Brands like Ford, BMW, and Mercedes-Benz have the highest counts, indicating these are the most commonly listed cars. As we move to the right, brands like Rolls-Royce, Bugatti, and Maybach have much lower counts, showing that they are rarer in this dataset. This distribution gives a sense of each brand's market presence and availability in the data.

Boxplot of Prices by Brand
"""

plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='brand', y='price')
plt.title('Boxplot of Prices by Brand')
plt.xlabel('Brand')
plt.ylabel('Price ($)')
plt.xticks(rotation=45)
plt.show()

"""------------

The boxplot visualizes the distribution of car prices across different brands. Each box represents the interquartile range (IQR) of prices for a specific brand, with the median price marked by a horizontal line inside each box. The "whiskers" extend to the minimum and maximum values within 1.5 times the IQR, while points outside this range are considered outliers (shown as circles). Brands like Rolls-Royce, Bugatti, and Lamborghini have higher median prices and more outliers, indicating a wider range of luxury car prices. Meanwhile, brands like Ford and Hyundai have prices clustered near the lower end, with fewer outliers.
"""

import seaborn as sns
numeric_df = df.select_dtypes(include=[float, int])

plt.figure(figsize=(12, 8))
sns.heatmap(numeric_df.corr(), annot=True, cmap='Paired', fmt='.2f')
plt.title('Correlation Heatmap')
plt.show()

"""#4- Building The model

in this section, we will bulid three base models to compare with our NN model. we are doing this because by creating simple models like Logistic Regression and Support Vector Machines , we establish benchmarks for the performance that our NN model must at least match or exceed.

### Feature selection

before we bulid the models we should perform feature selection to select only the relevent features to use in the model, this process is impotant so we dont overfit the model, also since feature selection helps identify which features truly drive the predictions
"""

import itertools
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.preprocessing import StandardScaler

"""using the ***encoded and numeric*** features only since

1- we are finding the pair of cars by finding the difference between them.

2- the algorithems we are using perform mathmatical equations on the data so it should be numerical.
"""

numeric_columns = df.select_dtypes(include=['number']).columns

# Display the numeric columns' names
print(numeric_columns)

features = ['model_year', 'milage', 'price', 'clean_title_ecnoded',
       'fuel_type_encoded', 'accident_encoded', 'price_norm', 'milage_norm',
       'price_category_encoded', 'mileage_bin_encoded', 'brand_popularity',
       'car_age', 'mileage_to_age_ratio', 'price_to_age_ratio',
       'encoded_price_category', 'encoded_transmission', 'encoded_brand']

# Generate all possible car pairs
car_indices = list(df.index)
car_pairs = list(itertools.combinations(car_indices, 2))

# Prepare lists to store the differences in attributes and the labels
pair_data = []
pair_labels = []

for idx1, idx2 in car_pairs:
    car1 = df.loc[idx1, features].values
    car2 = df.loc[idx2, features].values
    # Calculate the difference between the attributes of two cars
    diff = car1 - car2

    # Append the difference in attributes to the pair_data list
    pair_data.append(diff)

    # Define the label based on the car price
    # Label 1 if car1 is preferred (lower price), 0 otherwise
    label = 1 if df.loc[idx1, 'price'] < df.loc[idx2, 'price'] else 0
    pair_labels.append(label)

# Convert the pair_data and labels into a DataFrame and Series
X = pd.DataFrame(pair_data, columns=features)
y = pd.Series(pair_labels)

# Perform Feature Selection using all features
model = RandomForestClassifier()
# RFE to select top features (e.g., top 5 features)
rfe = RFE(model, n_features_to_select=5)  # Adjust n_features_to_select as needed
X_rfe = rfe.fit_transform(X, y)

# Get selected feature names
selected_features = X.columns[rfe.support_]
print("Selected features:", selected_features.tolist())  # Print selected features as a list

# Convert X_rfe back to a DataFrame with the selected features for clarity
X_selected = pd.DataFrame(X_rfe, columns=selected_features)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)

# Normalize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

"""## A) Base models:

### Logistic regression

### SVM

### Ensambles

## B) Neural Networks

we will use grid search and Random search to Systematically tested combinations of hyperparameters, such as the learning rate, batch size, number of units for neural networks.

### Grid search

since our dataset is large and we want to find a pair of cars, using the whole data would produce a very lage number of pairs

we decided to use random subset of the data to use in the model for that reason.
"""

# Function to build the neural network model
def create_model(hidden_layers=1, neurons=32, learning_rate=0.001):
    model = Sequential()
    model.add(Dense(neurons, input_dim=X_train_scaled.shape[1], activation='relu'))
    for _ in range(hidden_layers - 1):
        model.add(Dense(neurons, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))  # Output layer
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Wrap the model using KerasClassifier
model = KerasClassifier(model=create_model, verbose=0)

# Define a smaller grid for faster exploration
param_grid = {
    'model__hidden_layers': [1, 2],
    'model__neurons': [16, 32],
    'batch_size': [16, 32],
    'epochs': [50],
    'model__learning_rate': [0.001]
}

# Grid search with the corrected feature names
grid = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, verbose=2)
grid_result = grid.fit(X_train_scaled, y_train)

# Print best parameters and accuracy
print("Best parameters found: ", grid_result.best_params_)
print("Best accuracy achieved: ", grid_result.best_score_)

"""based on grid search we found that


**Best parameters found:**  {'batch_size': 16, 'epochs': 50, 'model__hidden_layers': 2, 'model__learning_rate': 0.001, 'model__neurons': 32}


**Best accuracy achieved:**  0.9750124374606929

now we will use these hyperparameters to develop a neural network model to predict car preference.
"""

# Retrieve the best hyperparameters
best_params = grid_result.best_params_
hidden_layers = best_params['model__hidden_layers']
neurons = best_params['model__neurons']
learning_rate = best_params['model__learning_rate']
batch_size = best_params['batch_size']
epochs = best_params['epochs']

# Build the neural network model with the best hyperparameters
def build_best_model(hidden_layers=hidden_layers, neurons=neurons, learning_rate=learning_rate):
    model = Sequential()
    model.add(Dense(neurons, input_dim=X_train_scaled.shape[1], activation='relu'))

    for _ in range(hidden_layers - 1):
        model.add(Dense(neurons, activation='relu'))

    model.add(Dense(1, activation='sigmoid'))  # Output layer for binary classification

    # Compile model
    model.compile(optimizer=Adam(learning_rate=learning_rate), loss='binary_crossentropy', metrics=['accuracy'])

    return model

# Initialize the model with the best hyperparameters
best_model = build_best_model()

# Train the model
best_model.fit(X_train_scaled, y_train, batch_size=batch_size, epochs=epochs, verbose=1)

# Evaluate the model on the test set
loss, accuracy = best_model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"Test Loss: {loss:.4f}")
print(f"Test Accuracy: {accuracy:.4f}")

"""using grid search we got these results

Test Loss: 0.0403
Test Accuracy: 0.9850

meaning a loss of 0.0403 is indicating that our model is making accurate predictions and has learned effectively from the training data.
while a test accuracy of 0.9850, or 98.5%, is also excellent, suggesting that the model correctly classified 98.5% of the test samples.

### Random search
"""

# Set random seed for reproducibility
np.random.seed(0)

# Create two sets of shuffled indices for pairing observations
half_len = len(df) // 2  # Half the dataset length
indices = np.random.permutation(len(df))  # Random permutation of indices

# Split the indices into two halves for comparison
first_indices = indices[:half_len]  # First half
second_indices = indices[half_len:half_len * 2]  # Second half

# Create a paired dataset where each row is a comparison between two cars
df_pairs = pd.DataFrame({
    'price_diff': df['price_norm'].iloc[first_indices].values - df['price_norm'].iloc[second_indices].values,
    'mileage_diff': df['milage_norm'].iloc[first_indices].values - df['milage_norm'].iloc[second_indices].values,
    'model_year_diff': df['model_year'].iloc[first_indices].values - df['model_year'].iloc[second_indices].values,
    'brand_popularity_diff': df['brand_popularity'].iloc[first_indices].values - df['brand_popularity'].iloc[second_indices].values,
    'accident_encoded_1': df['clean_title_ecnoded'].iloc[first_indices].values,
    'accident_encoded_2': df['clean_title_ecnoded'].iloc[second_indices].values,
    'fuel_type_encoded_1': df['fuel_type_encoded'].iloc[first_indices].values,
    'fuel_type_encoded_2': df['fuel_type_encoded'].iloc[second_indices].values,
    'preferred_car': (df['price'].iloc[first_indices].values > df['price'].iloc[second_indices].values).astype(int)
})

# Split the data into features (X) and target variable (y)
X = df_pairs.drop('preferred_car', axis=1)  # Drop target column to get features
y = df_pairs['preferred_car']  # Target: 1 if first car is preferred, 0 otherwise

# Apply feature scaling to ensure that all features contribute equally to the model
scaler = StandardScaler()  # Initialize scaler
X = scaler.fit_transform(X)  # Scale features

# Define a function to build the neural network model
def build_model(neurons=32, optimizer='adam'):
    """Build a Sequential neural network model."""
    model = Sequential([  # Initialize a Sequential model
        Dense(neurons, activation='relu', input_shape=(X.shape[1],)),  # First hidden layer
        Dense(neurons, activation='relu'),  # Second hidden layer
        Dense(1, activation='sigmoid')  # Output layer for binary classification
    ])
    # Compile the model with specified optimizer, loss function, and evaluation metric
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Wrap the Keras model to use it with scikit-learn's RandomizedSearchCV
model = KerasClassifier(model=build_model, verbose=0)

# Define the hyperparameter search space for RandomizedSearchCV
param_dist = {
    'model__neurons': [32, 64, 128, 256],  # Number of neurons per layer to try
    'model__optimizer': ['adam', 'sgd'],  # Optimizers to experiment with
    'batch_size': [16, 32, 64],  # Batch sizes to test
    'epochs': [10, 20, 30, 50]  # Number of epochs for training
}

# Initialize RandomizedSearchCV to find the best hyperparameters
random_search = RandomizedSearchCV(
    estimator=model,  # Keras model wrapped in KerasClassifier
    param_distributions=param_dist,  # Hyperparameter space
    n_iter=5,  # Number of random combinations to try
    cv=5,  # 5-fold cross-validation
    verbose=1,  # Print progress
    random_state=42,  # Reproducibility
    n_jobs=-1  # Use all available CPU cores
)

# Perform the random search to find the best hyperparameters
random_search_result = random_search.fit(X, y)

# Display the best score and hyperparameters found
print(f"Best Score: {random_search_result.best_score_}")
print(f"Best Params: {random_search_result.best_params_}")

# Extract the best hyperparameters from the search results
best_params = random_search_result.best_params_

# Build the model with the best found hyperparameters
best_model = build_model(
    neurons=best_params['model__neurons'],  # Optimal number of neurons
    optimizer=best_params['model__optimizer']  # Optimal optimizer
)

# Split the data into training and testing sets for final evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Train the model with the best hyperparameters and capture the training history
history = best_model.fit(
    X_train, y_train,  # Training data
    validation_data=(X_test, y_test),  # Validation data
    epochs=best_params['epochs'],  # Optimal number of epochs
    batch_size=best_params['batch_size'],  # Optimal batch size
    verbose=1  # Display training progress
)

# Evaluate the model on the test set
loss, accuracy = best_model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Generate predictions on the test set
y_pred = (best_model.predict(X_test) > 0.5).astype("int32")

# Print the confusion matrix and classification report for model evaluation
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Plot the training history: accuracy and loss over epochs
plt.figure(figsize=(12, 5))

# Plot training and validation accuracy
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

# Plot training and validation loss
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# Adjust layout and display the plots
plt.tight_layout()
plt.show()

"""Using Random search, Our model performance was so much better!
the model demonstrates outstanding performance with high precision, recall, and F1-scores for both classes, as well as an impressive overall accuracy.

This suggests that Our model is effectively learning the distinguishing features between the two classes and generalizing well to the test data.

Accuracy: 0.99 (99% of the total predictions were correct)
This indicates that the model correctly classified 99% of all instances in the test set, which is an excellent result.

The precision values indicate that 99% of the predicted instances for both classes were correct, while the recall values show the model accurately identified all instances of class 0 and 98% of class 1 instances. The F1-scores being high for both classes reflect a balanced performance in precision and recall.

The overall results from the random search for hyperparameter optimization have proven to be superior to those obtained from the grid search. Several factors could explain this difference in performance, The grid search was conducted on a subset of the data, which represents only a small portion of the entire dataset. This limited representation may not have captured the full range of variability and patterns present in the complete dataset, leading to suboptimal hyperparameter selections and model performance.

Since the grid search was performed on a smaller subset, there is a greater risk of overfitting to that limited data, potentially skewing the results. In contrast, the random search may have had access to a more representative sample, leading to more robust generalization.
"""