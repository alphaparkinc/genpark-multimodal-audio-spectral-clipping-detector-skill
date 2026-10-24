import sys, json
from client import MultimodalAudioSpectralClippingDetectorClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    client = MultimodalAudioSpectralClippingDetectorClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-multimodal-audio-spectral-clipping-detector-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    samples = req.get("samples", [0] * 320)
    res = client.analyze_audio_frame(samples)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
