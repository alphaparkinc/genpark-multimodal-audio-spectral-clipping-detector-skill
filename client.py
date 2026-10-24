import math, struct, sys
sys.stdout.reconfigure(encoding='utf-8')

class MultimodalAudioSpectralClippingDetectorClient:
    """
    Pure Python digital signal processing (DSP) client for real-time voice frames.
    Computes RMS energy, zero-crossing rate (ZCR), crest factor, and clipping distortion.
    """
    def __init__(self, sample_rate=16000, bit_depth=16):
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.max_amplitude = (1 << (bit_depth - 1)) - 1 # 32767 for 16-bit
        self.clipping_threshold = self.max_amplitude * 0.995 # ~32603

    def parse_samples(self, audio_data):
        if isinstance(audio_data, (bytes, bytearray)):
            fmt = f"<{len(audio_data)//2}h"
            return list(struct.unpack(fmt, audio_data))
        elif isinstance(audio_data, list):
            return [float(x) for x in audio_data]
        else:
            raise ValueError("audio_data must be bytes or list of numeric amplitudes")

    def analyze_audio_frame(self, audio_data):
        samples = self.parse_samples(audio_data)
        n = len(samples)
        if n == 0:
            return {"status": "error", "message": "Empty audio frame"}

        sum_squares = 0.0
        zero_crossings = 0
        clipped_samples = 0
        peak_amp = 0.0

        for i in range(n):
            val = abs(samples[i])
            if val > peak_amp:
                peak_amp = val
            sum_squares += samples[i] * samples[i]
            if val >= self.clipping_threshold:
                clipped_samples += 1
            if i > 0 and ((samples[i] >= 0 and samples[i - 1] < 0) or (samples[i] < 0 and samples[i - 1] >= 0)):
                zero_crossings += 1

        rms = math.sqrt(sum_squares / n)
        normalized_rms = rms / self.max_amplitude
        dbfs = 20.0 * math.log10(max(normalized_rms, 1e-6))
        
        zcr = zero_crossings / float(n - 1) if n > 1 else 0.0
        crest_factor = (peak_amp / max(rms, 1e-5)) if rms > 0 else 1.0
        crest_factor_db = 20.0 * math.log10(max(crest_factor, 1.0))
        
        clipping_percentage = (clipped_samples / float(n)) * 100.0

        # Dynamic state classification
        if clipping_percentage > 0.8:
            state = "CLIPPING_DISTORTION"
            action = "ATTENUATE_INPUT_GAIN"
            gain_adj_db = -math.ceil(math.log10(max(1.01, peak_amp / self.clipping_threshold)) * 20.0) - 3.0
        elif dbfs < -55.0:
            state = "DIGITAL_SILENCE"
            action = "KEEP_GATE_CLOSED"
            gain_adj_db = 0.0
        elif dbfs < -38.0 and zcr > 0.35:
            state = "BACKGROUND_NOISE"
            action = "APPLY_SPECTRAL_SUBTRACTION"
            gain_adj_db = 0.0
        elif dbfs >= -38.0 and 0.02 <= zcr <= 0.40:
            state = "ACTIVE_VOICE_SPEECH"
            action = "TRANSMIT_TO_ASR"
            gain_adj_db = 0.0
        else:
            state = "UNCERTAIN_AMBIENT"
            action = "MONITOR"
            gain_adj_db = 0.0

        return {
            "status": "success",
            "sample_count": n,
            "duration_ms": round((n / float(self.sample_rate)) * 1000.0, 2),
            "rms_amplitude": round(rms, 2),
            "energy_dbfs": round(dbfs, 2),
            "zero_crossing_rate": round(zcr, 4),
            "peak_amplitude": round(peak_amp, 2),
            "crest_factor_db": round(crest_factor_db, 2),
            "clipped_sample_count": clipped_samples,
            "clipping_percentage": round(clipping_percentage, 3),
            "spectral_state": state,
            "recommended_dsp_action": action,
            "suggested_gain_adjustment_db": gain_adj_db
        }
