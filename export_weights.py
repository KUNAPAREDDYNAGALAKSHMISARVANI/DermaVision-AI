import os
import tensorflow as tf

print("Loading original Keras model...")
original = tf.keras.models.load_model("model/best_model.keras", compile=False)

print("Rebuilding architecture...")
base_model = tf.keras.applications.MobileNetV2(
    weights=None,
    include_top=False,
    input_shape=(224, 224, 3)
)
x = base_model.output
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.3)(x)
outputs = tf.keras.layers.Dense(9, activation="softmax")(x)

model = tf.keras.models.Model(inputs=base_model.input, outputs=outputs)
model.set_weights(original.get_weights())

weights_path = "model/model.weights.h5"
model.save_weights(weights_path)
print(f"Successfully saved clean weights to {weights_path}!")
