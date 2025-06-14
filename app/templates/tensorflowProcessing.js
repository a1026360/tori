import { frequencyPoints } from "./recording.js";
import * as tf from "@tensorflow/tfjs";

export async function processFrequencyData() {
    const model = await tf.loadLayersModel("path-to-your-model/model.json");

    let tensorInput = tf.tensor2d(frequencyPoints.map(freq => [freq]), [frequencyPoints.length, 1]);

    let predictions = model.predict(tensorInput);
    let maxPredictionIndex = predictions.argMax(0).dataSync()[0];

    document.body.innerHTML += `<img src='images/${maxPredictionIndex}.jpg' alt='Recognized Image'>`;
}
