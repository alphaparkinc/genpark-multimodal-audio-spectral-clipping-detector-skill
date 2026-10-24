from client import MultimodalAudioSpectralClippingDetectorClient
import math, sys
sys.stdout.reconfigure(encoding='utf-8')

def generate_synthetic_audio(freq=440.0, sample_rate=16000, duration_sec=0.03, amplitude=25000.0, clip=False):
    total_samples = int(sample_rate * duration_sec)
    samples = []
    for i in range(total_samples):
        t = i / float(sample_rate)
        val = amplitude * math.sin(2.0 * math.pi * freq * t)
        if clip:
            val = max(-32767.0, min(32767.0, val * 1.8))
        samples.append(int(val))
    return samples

def main():
    detector = MultimodalAudioSpectralClippingDetectorClient(sample_rate=16000)
    print("=== MULTIMODAL AUDIO SPECTRAL CLIPPING DETECTOR ===")
    
    # 1. Normal clean speech frame
    clean_frame = generate_synthetic_audio(freq=300.0, amplitude=16000.0, clip=False)
    res_clean = detector.analyze_audio_frame(clean_frame)
    print(f"1. Clean Speech Frame: {res_clean['spectral_state']} (dBFS: {res_clean['energy_dbfs']}, Clipping: {res_clean['clipping_percentage']}%)")
    print(f"   -> Action: {res_clean['recommended_dsp_action']}")
    
    # 2. Severely clipped audio frame
    clipped_frame = generate_synthetic_audio(freq=250.0, amplitude=32000.0, clip=True)
    res_clipped = detector.analyze_audio_frame(clipped_frame)
    print(f"2. Clipped Frame: {res_clipped['spectral_state']} (dBFS: {res_clipped['energy_dbfs']}, Clipping: {res_clipped['clipping_percentage']}%)")
    print(f"   -> Action: {res_clipped['recommended_dsp_action']} (Adj: {res_clipped['suggested_gain_adjustment_db']} dB)")

    # 3. Low energy silence frame
    silence_frame = [int(i % 15 - 7) for i in range(480)]
    res_silence = detector.analyze_audio_frame(silence_frame)
    print(f"3. Silence Frame: {res_silence['spectral_state']} (dBFS: {res_silence['energy_dbfs']}, ZCR: {res_silence['zero_crossing_rate']})")
    print(f"   -> Action: {res_silence['recommended_dsp_action']}")

if __name__ == "__main__":
    main()
