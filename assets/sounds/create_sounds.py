import pygame
import numpy as np
import os
import wave
import struct

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Function to save a numpy array as a WAV file
def save_wav(filename, data, sample_rate=44100):
    # Ensure data is in the range [-1, 1]
    data = np.clip(data, -1, 1)
    
    # Convert to 16-bit PCM
    data = (data * 32767).astype(np.int16)
    
    # Open WAV file for writing
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 2 bytes = 16 bits
        wav_file.setframerate(sample_rate)
        
        # Write data
        for sample in data:
            wav_file.writeframes(struct.pack('<hh', sample[0], sample[1]))
    
    print(f"Saved {filename}")

# Create a smoother grow sound (soft bell-like sound)
def create_grow_sound():
    sample_rate = 44100
    duration = 0.5
    buffer = np.zeros((int(sample_rate * duration), 2), dtype=np.float32)
    
    # Generate a pleasant bell-like tone
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Main tone (higher frequency)
    freq1 = 440  # A4
    tone1 = 0.7 * np.sin(2 * np.pi * freq1 * t)
    
    # Harmonic overtones
    freq2 = freq1 * 1.5  # Perfect fifth
    tone2 = 0.3 * np.sin(2 * np.pi * freq2 * t)
    
    freq3 = freq1 * 2  # Octave
    tone3 = 0.2 * np.sin(2 * np.pi * freq3 * t)
    
    # Combine tones
    tone = tone1 + tone2 + tone3
    
    # Apply smooth envelope (ADSR: Attack, Decay, Sustain, Release)
    attack = int(0.05 * sample_rate)
    decay = int(0.1 * sample_rate)
    release = int(0.35 * sample_rate)
    
    envelope = np.ones(len(tone))
    # Attack phase
    envelope[:attack] = np.linspace(0, 1, attack)
    # Decay phase
    envelope[attack:attack+decay] = np.linspace(1, 0.7, decay)
    # Release phase
    envelope[-release:] = np.linspace(0.7, 0, release)
    
    tone = tone * envelope * 0.5
    
    # Convert to stereo
    buffer[:, 0] = tone
    buffer[:, 1] = tone
    
    return buffer

# Create a smoother shrink sound (soft descending tone)
def create_shrink_sound():
    sample_rate = 44100
    duration = 0.5
    buffer = np.zeros((int(sample_rate * duration), 2), dtype=np.float32)
    
    # Generate a gentle descending tone
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create a frequency sweep from high to low
    freq_start = 440
    freq_end = 220
    freq = np.linspace(freq_start, freq_end, len(t))
    
    # Main tone with frequency sweep
    tone = 0.6 * np.sin(2 * np.pi * freq * t)
    
    # Add a subtle second tone for richness
    tone2 = 0.2 * np.sin(2 * np.pi * freq * 1.5 * t)
    
    # Combine tones
    tone = tone + tone2
    
    # Apply smooth envelope
    attack = int(0.05 * sample_rate)
    release = int(0.3 * sample_rate)
    
    envelope = np.ones(len(tone))
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    
    tone = tone * envelope * 0.5
    
    # Convert to stereo
    buffer[:, 0] = tone
    buffer[:, 1] = tone
    
    return buffer

# Create a pleasant win sound (musical chime sequence)
def create_win_sound():
    sample_rate = 44100
    duration = 2.0
    buffer = np.zeros((int(sample_rate * duration), 2), dtype=np.float32)
    
    # Define a pleasant major chord progression
    notes = [
        {"freq": 523.25, "start": 0.0, "duration": 0.5},     # C5
        {"freq": 659.25, "start": 0.2, "duration": 0.5},     # E5
        {"freq": 783.99, "start": 0.4, "duration": 0.5},     # G5
        {"freq": 1046.50, "start": 0.7, "duration": 1.0}     # C6 (longer final note)
    ]
    
    # Generate each note
    for note in notes:
        freq = note["freq"]
        start_time = note["start"]
        note_duration = note["duration"]
        
        start_sample = int(start_time * sample_rate)
        end_sample = min(int((start_time + note_duration) * sample_rate), len(buffer))
        
        # Create time array for this note
        t = np.linspace(0, note_duration, end_sample - start_sample, False)
        
        # Create a bell-like tone with harmonics
        tone = 0.7 * np.sin(2 * np.pi * freq * t)
        tone += 0.3 * np.sin(2 * np.pi * freq * 2 * t)  # First overtone
        tone += 0.1 * np.sin(2 * np.pi * freq * 3 * t)  # Second overtone
        
        # Apply envelope
        attack = int(0.05 * note_duration * sample_rate)
        release = int(0.5 * note_duration * sample_rate)
        
        envelope = np.ones_like(tone)
        if len(tone) > 0:
            if attack > 0 and attack < len(tone):
                envelope[:attack] = np.linspace(0, 1, attack)
            if release > 0 and release < len(tone):
                envelope[-release:] = np.linspace(1, 0, release)
        
        tone = tone * envelope * 0.4
        
        # Add to buffer
        if start_sample < len(buffer) and end_sample <= len(buffer):
            buffer[start_sample:end_sample, 0] += tone
            buffer[start_sample:end_sample, 1] += tone
    
    return buffer

# Create a gentle background music (soft ambient loop)
def create_background_music():
    sample_rate = 44100
    duration = 8.0  # 8 seconds loop
    buffer = np.zeros((int(sample_rate * duration), 2), dtype=np.float32)
    
    # Generate a base ambient tone
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Use pleasant chord frequencies (C major)
    freqs = [
        65.41,   # C2
        82.41,   # E2
        98.00,   # G2
        130.81,  # C3
        164.81,  # E3
        196.00   # G3
    ]
    
    # Add each frequency with different amplitudes and phases
    for i, freq in enumerate(freqs):
        # Add some gentle vibrato
        vibrato_rate = 0.2 + (i * 0.05)  # Different for each tone
        vibrato_depth = 0.005
        vibrato = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        
        # Create a smooth waveform (mix of sine and triangle)
        phase = i * 0.5  # Different phase for each tone
        amp = 0.1 - (i * 0.01)  # Decreasing amplitude for higher frequencies
        
        # Sine component
        tone = amp * np.sin(2 * np.pi * freq * vibrato * t + phase)
        
        # Add to buffer with panning
        pan = 0.5 + (i - len(freqs)/2) * 0.1  # Pan across stereo field
        buffer[:, 0] += tone * (1 - pan * 0.5)
        buffer[:, 1] += tone * (1 - (1-pan) * 0.5)
    
    # Apply a very slow amplitude modulation for movement
    mod_freq = 0.05
    mod = 0.8 + 0.2 * np.sin(2 * np.pi * mod_freq * t)
    buffer[:, 0] *= mod
    buffer[:, 1] *= mod
    
    # Apply fade in and fade out for looping
    fade_samples = int(0.5 * sample_rate)
    if fade_samples > 0:
        buffer[:fade_samples, 0] *= np.linspace(0, 1, fade_samples)
        buffer[:fade_samples, 1] *= np.linspace(0, 1, fade_samples)
        buffer[-fade_samples:, 0] *= np.linspace(1, 0, fade_samples)
        buffer[-fade_samples:, 1] *= np.linspace(1, 0, fade_samples)
    
    # Ensure we don't clip
    buffer = np.clip(buffer, -0.9, 0.9)
    
    return buffer

# Create and save sounds
def main():
    print("Creating sound effects...")
    
    # Create sounds directory if it doesn't exist
    sounds_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(sounds_dir, exist_ok=True)
    
    # Create and save grow sound
    print("Creating grow sound...")
    grow_sound = create_grow_sound()
    save_wav(os.path.join(sounds_dir, "grow.wav"), grow_sound)
    
    # Create and save shrink sound
    print("Creating shrink sound...")
    shrink_sound = create_shrink_sound()
    save_wav(os.path.join(sounds_dir, "shrink.wav"), shrink_sound)
    
    # Create and save win sound
    print("Creating win sound...")
    win_sound = create_win_sound()
    save_wav(os.path.join(sounds_dir, "win.wav"), win_sound)
    
    # Create and save background music
    print("Creating background music...")
    bg_music = create_background_music()
    save_wav(os.path.join(sounds_dir, "background.wav"), bg_music)
    
    print("All sound effects created successfully!")
    print("Restart the game to use the new sounds.")

if __name__ == "__main__":
    main()
