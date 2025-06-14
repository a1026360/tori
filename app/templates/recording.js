// recording.js
export let frequencyPoints = [];
let audioContext, analyser, dataArray;
let maxFrequency = 8000;
let recordingTime = 10 * 1000;

export function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 4096;

            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);

            dataArray = new Uint8Array(analyser.frequencyBinCount);

            draw();

            setTimeout(() => {
                stream.getTracks().forEach(track => track.stop());
            }, recordingTime);
        })
        .catch(err => console.error("Microphone access denied:", err));
}

function draw() {
    requestAnimationFrame(draw);
    analyser.getByteFrequencyData(dataArray);

    let maxIndex = dataArray.indexOf(Math.max(...dataArray));
    let frequencyHz = maxIndex * (audioContext.sampleRate / analyser.fftSize);

    if (frequencyHz > maxFrequency) return;

    frequencyPoints.push(frequencyHz);
}
