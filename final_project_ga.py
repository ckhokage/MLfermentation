# -*- coding: utf-8 -*-
"""Final project-GA.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ciBD3zqRT0zBLTk7bbRH1cSwagx2YO8d
"""

# Model type selection
MODEL_TYPE = 'Transformer'  # Choose from 'LSTM', 'CNN', 'Transformer', 'Regression'

# Genetic Algorithm for Hyperparameter Optimization
def create_population(size=10):
    population = []
    for _ in range(size):
        individual = {
            "num_layers": 1,
            "units": np.random.choice([32, 64, 128]),
            "dropout": np.random.uniform(0.1, 0.5),
            "learning_rate": np.random.uniform(0.0001, 0.01),
            "filters": np.random.choice([32, 64, 128]) if MODEL_TYPE == "CNN" else None,
            "kernel_size": np.random.choice([3, 5]) if MODEL_TYPE == "CNN" else None,
            "num_heads": np.random.choice([2, 4, 8]) if MODEL_TYPE == "Transformer" else None
        }
        population.append(individual)
    return population

def train_and_evaluate(individual):
    input_layer = Input(shape=(X_train.shape[1], X_train.shape[2]))
    x = input_layer

    if MODEL_TYPE == "LSTM":
        for _ in range(individual["num_layers"]):
            x = Bidirectional(LSTM(individual["units"], return_sequences=True))(x)
        x = Attention()([x, x])
        x = tf.keras.layers.GlobalAveragePooling1D()(x)

    elif MODEL_TYPE == "CNN":
        for _ in range(individual["num_layers"]):
          x = Conv1D(individual["filters"], (individual["kernel_size"],), activation='relu', padding='same')(x)
        x = Flatten()(x)

    elif MODEL_TYPE == "Transformer":
        for _ in range(individual["num_layers"]):
            x = MultiHeadAttention(num_heads=individual["num_heads"], key_dim=individual["units"])(x, x)
        x = Flatten()(x)

    elif MODEL_TYPE == "Regression":
        for _ in range(individual["num_layers"]):
            x = Dense(individual["units"], activation='relu')(x)
        x = Flatten()(input_layer)

    x = Dense(32, activation='relu')(x)
    x = Dropout(individual["dropout"])(x)
    outputs = [Dense(1, name=feature.replace(" ", "_"))(x) for feature in output_features]

    model = Model(inputs=input_layer, outputs=outputs)
    model.compile(optimizer=Adam(learning_rate=individual["learning_rate"]), loss='mse')

    model.fit(X_train, [y_train[:, i] for i in range(y_train.shape[1])], epochs=10, batch_size=16, verbose=0)
    loss = model.evaluate(X_test, [y_test[:, i] for i in range(y_test.shape[1])], verbose=0)
    return np.mean(loss)

def evolve_population(population, retain=0.5, mutation_rate=0.2):
    sorted_population = sorted(population, key=lambda ind: train_and_evaluate(ind))
    retain_length = int(len(sorted_population) * retain)
    next_generation = sorted_population[:retain_length]

    while len(next_generation) < len(population):
        parent1, parent2 = np.random.choice(sorted_population[:retain_length], 2)
        child = {
            "num_layers": np.random.choice([parent1["num_layers"], parent2["num_layers"]]),
            "units": np.random.choice([parent1["units"], parent2["units"]]),
            "dropout": np.random.choice([parent1["dropout"], parent2["dropout"]]),
            "learning_rate": np.random.choice([parent1["learning_rate"], parent2["learning_rate"]]),
            "filters": np.random.choice([parent1.get("filters"), parent2.get("filters")]) if MODEL_TYPE == "CNN" else None,
            "kernel_size": np.random.choice([parent1.get("kernel_size"), parent2.get("kernel_size")]) if MODEL_TYPE == "CNN" else None,
            "num_heads": np.random.choice([parent1.get("num_heads"), parent2.get("num_heads")]) if MODEL_TYPE == "Transformer" else None
        }
        if np.random.rand() < mutation_rate:
            if MODEL_TYPE == "CNN":
                child["filters"] = np.random.choice([32, 64, 128])
                child["kernel_size"] = np.random.choice([3, 5])
            if MODEL_TYPE == "Transformer":
                child["num_heads"] = np.random.choice([2, 4, 8])
            child["dropout"] = np.random.uniform(0.1, 0.5)
            child["learning_rate"] = np.random.uniform(0.0001, 0.01)
        next_generation.append(child)

    return next_generation

# Run Genetic Algorithm
population = create_population()
generations = 5

for generation in range(generations):
    print(f"Generation {generation + 1}")
    population = evolve_population(population)

# Select best model hyperparameters
best_hyperparams = sorted(population, key=lambda ind: train_and_evaluate(ind))[0]
print("Best Hyperparameters:", best_hyperparams)

MODEL_UNITS = best_hyperparams["units"]
NUM_FEATURE_LAYERS = best_hyperparams["num_layers"]
DROPOUT_RATE = best_hyperparams["dropout"]
LEARNING_RATE = best_hyperparams["learning_rate"]
FILTERS = best_hyperparams.get("filters")
KERNEL_SIZE = best_hyperparams.get("kernel_size")
NUM_HEADS = best_hyperparams.get("num_heads")

# Hyperparameters
NUM_DENSE_LAYERS = 2  # Number of Dense layers after feature extraction
MODEL_UNITS = 64
DENSE_UNITS = 32
OUTPUT_DENSE_UNITS = 32
EPOCHS = 100
BATCH_SIZE = 16
TEST_SIZE = 0.2
USE_LR_SCHEDULING = True

# Define input and output variables dynamically
columns = df.columns.tolist()
input_features = columns[:-4]
output_features = columns[-4:]

# Convert dataframe to numeric values
df = df.apply(pd.to_numeric, errors='coerce')

# Drop any rows with NaN values
df.dropna(inplace=True)

# Preprocessing
scaler_x = StandardScaler()
scaler_y = StandardScaler()
X = scaler_x.fit_transform(df[input_features])
y = scaler_y.fit_transform(df[output_features])

# Reshape X for LSTM and CNN (batch_size, time_steps, features)
X = X.reshape(X.shape[0], X.shape[1], 1)

# Pick 10 specific data points for demonstration before splitting (fixed indices within valid range)
demo_indices = np.array([5, 25, 50, 75, 100, 150, 200, 250, 300, 350])
demo_X = X[demo_indices]
demo_y = y[demo_indices]
X = np.delete(X, demo_indices, axis=0)
y = np.delete(y, demo_indices, axis=0)

# Splitting dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=42)

# Define input layer
input_layer = Input(shape=(X_train.shape[1], X_train.shape[2]))

# Model selection with added control for number of layers
if MODEL_TYPE == "LSTM":
    x = input_layer
    for _ in range(NUM_FEATURE_LAYERS):
        x = Bidirectional(LSTM(MODEL_UNITS, return_sequences=True))(x)
    x = Attention()([x, x])
    x = tf.keras.layers.GlobalAveragePooling1D()(x)  # Alternative: Flatten()

elif MODEL_TYPE == "CNN":
    x = input_layer
    for _ in range(NUM_FEATURE_LAYERS):
        x = Conv1D(FILTERS, (KERNEL_SIZE,), activation='relu', padding='same')(x)
    x = Flatten()(x)

elif MODEL_TYPE == "Transformer":
    x = input_layer
    for _ in range(NUM_FEATURE_LAYERS):
        x = MultiHeadAttention(num_heads=NUM_HEADS, key_dim=MODEL_UNITS)(x, x)
    x = Flatten()(x)

elif MODEL_TYPE == "Regression":
    x = input_layer
    for _ in range(NUM_FEATURE_LAYERS):
        x = Dense(MODEL_UNITS, activation='relu')(x)
    x = Flatten()(input_layer)

# Stacked Dense layers
for _ in range(NUM_DENSE_LAYERS):
    x = Dense(DENSE_UNITS, activation='relu')(x)
    x = Dropout(DROPOUT_RATE)(x)

# Define separate outputs with explicit names
outputs = []
for feature in output_features:
    safe_feature_name = feature.replace(" ", "_")
    out = Dense(OUTPUT_DENSE_UNITS, activation='relu', name=f"{safe_feature_name}_hidden")(x)
    out = Dropout(DROPOUT_RATE, name=f"{safe_feature_name}_dropout")(out)
    out = Dense(1, name=safe_feature_name)(out)
    outputs.append(out)

# Build model
model = Model(inputs=input_layer, outputs=outputs)
model.compile(optimizer=Adam(learning_rate=LEARNING_RATE), loss='mse')

# Display model summary to show the number of parameters
model.summary()

# Train model with less verbose output
if USE_LR_SCHEDULING:
    lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-5, verbose=1)
    callbacks = [lr_scheduler]
else:
    callbacks = []

# Train model with learning rate scheduler if enabled
history = model.fit(
    X_train, [y_train[:, i] for i in range(y_train.shape[1])],
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_split=0.2,
    verbose=2,
    callbacks=callbacks  # Include scheduler callback if enabled
)

# Plot loss curve
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title(f'Model Training Loss ({MODEL_TYPE})')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.savefig(f"loss_curve_{MODEL_TYPE}.png")
plt.show()

# Evaluate model using RMSE
predictions = model.predict(X_test)
rmse_scores = []
for i, feature in enumerate(output_features):
    safe_feature_name = feature.replace(" ", "_")
    mse = mean_squared_error(y_test[:, i], predictions[i].flatten())
    rmse = np.sqrt(mse)
    rmse_scores.append(rmse)
    print(f'RMSE for {safe_feature_name}: {rmse:.4f}')

# Predict on demonstration data
demo_predictions = model.predict(demo_X)

# Create and display results table
results_table = pd.DataFrame({
    'Data Point': demo_indices,
    'Experimental Value': demo_y[:, 0],
    'Predicted Value': np.array(demo_predictions[0]).flatten(),
    'Error': np.abs(demo_y[:, 0]-np.array(demo_predictions[0]).flatten())/np.array(demo_predictions[0]).flatten()})
print(results_table)
results_table.to_csv(f"10pts_table_{MODEL_TYPE}.csv", index=False)

# Ensemble Learning with Voting Regressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

base_models = [
    ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
    ('gb', GradientBoostingRegressor(n_estimators=50, learning_rate=0.1, random_state=42))
]

ensemble_models = []
ensemble_scores = []

# Train separate ensemble models for each output variable
train_preds = np.column_stack(model.predict(X_train))
test_preds = np.column_stack(model.predict(X_test))

for i, feature in enumerate(output_features):
    safe_feature_name = feature.replace(" ", "_")
    ensemble = VotingRegressor(estimators=base_models)
    ensemble.fit(train_preds[:, i].reshape(-1, 1), y_train[:, i])
    score = ensemble.score(test_preds[:, i].reshape(-1, 1), y_test[:, i])
    ensemble_models.append(ensemble)
    ensemble_scores.append(score)
    print(f'Ensemble Model Score for {safe_feature_name}: {score:.4f} (Higher is better, best = 1)')