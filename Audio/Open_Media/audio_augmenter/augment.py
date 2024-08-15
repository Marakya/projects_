import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import soundfile as sf
from scipy.io import wavfile
from scipy.signal import butter, lfilter,resample
import scipy
from IPython.display import Audio, display
import torch



class AudioAugmentor:
    def __init__(self, waveform, sample_rate):
        """
            sample_rate: Sampling rate
            num_channels: Number of channels
            noise_level: white noise level
            pitch_factor: Indicates a change in pitch
            stretch_factor: Duration of the audio signal change
            num_masks: Number of lanes
            time_mask_param: Maximum mask length
        """

        self.sample_rate = sample_rate
        self.num_channels = 1 if len(waveform.shape) == 1 else waveform.shape[1]
        self.noise_level = 0.005
        self.pitch_factor = 1.5
        self.stretch_factor = 1.2
        self.num_masks = 8 
        self.time_mask_param = 5 

        if self.num_channels == 2:
            # Averaging of both channels to obtain a mono signal
            waveform = waveform.mean(axis=1)

        # Convert waveform to float32 and normalize
        waveform = waveform.astype(np.float32) / np.max(np.abs(waveform))
        # Convert to the Pwtorch tensor and add dimension
        self.waveform = torch.tensor(waveform).view(-1, 1)


    def add_white_noise(self):
        """
        Adding white noise to the audio.
        """

        noise = np.random.randn(*self.waveform.shape) * self.noise_level
        self.waveform += noise


    def random_gain(self, gain_range=(-10, 10)):
        """
        Random volume change.
        """

        gain = np.random.uniform(*gain_range)
        self.waveform *= (10 ** (gain / 20))

    def add_echo(self, delay=0.1, decay=0.2):
        """
        Adds an echo effect to the sound wave.
        """

        delay_samples = int(delay * self.sample_rate)
        echo_waveform = np.zeros_like(self.waveform)
        echo_waveform[delay_samples:] = self.waveform[:-delay_samples] * decay
        self.waveform += echo_waveform
  

    def apply_flanger(self, depth=1, rate=1.5):
        """
        Adds flanging - is an audio effect that combines 
        the original signal with a delayed version.
        """

        num_samples = len(self.waveform[0])
        flanger_waveform = np.zeros(num_samples)
        for i in range(num_samples):
            delay = int(depth * self.sample_rate * (1 + np.sin(2 * np.pi * rate * i / self.sample_rate)))
            if i - delay >= 0:
                flanger_waveform[i] = self.waveform[0][i - delay]
        # Normalization of the result to prevent distortion
        flanger_waveform = np.clip(flanger_waveform, -1, 1)
        self.waveform[0] += flanger_waveform
        self.waveform[0] = np.clip(self.waveform[0], -1, 1)  


    def change_pitch(self):
        """
        Changing the sampling rate.
        """

        new_sample_rate = int(self.sample_rate * self.pitch_factor)
        new_data = resample(self.waveform, int(len(self.waveform) * self.pitch_factor))
        self.waveform= new_data


    def time_stretch(self):
        """
        Changing the length of the audio signal
        """

        stretched_length = int(len(self.waveform) * self.stretch_factor)
        stretched_audio = resample(self.waveform, stretched_length)
        self.waveform = torch.from_numpy(stretched_audio)


    def vibrato(self, depth=0.005, frequency=3):
        """
        Adds a vibrato effect to the audio signal 
        by modulating the pitch with a sinusoidal waveform, 
        creating a periodic variation in pitch over time
        """

        num_samples = len(self.waveform)
        t = np.arange(num_samples) / self.sample_rate
        modulation = depth * np.sin(2 * np.pi * frequency * t)

        vibrato_signal = np.zeros_like(self.waveform)
        for i in range(num_samples):
            delay = int(modulation[i] * self.sample_rate)
            if i - delay >= 0:
                vibrato_signal[i] = self.waveform[i - delay]
            else:
                vibrato_signal[i] = self.waveform[i]  
        self.waveform = torch.from_numpy(vibrato_signal)
        return self.waveform

    def augment_audio(self):
        """
        Applying effects to audio
        """

        self.add_white_noise()
        self.random_gain()
        self.add_echo()
        self.apply_flanger()
        self.change_pitch()
        self.time_stretch()
        self.waveform = self.vibrato()
        print("Effects have been applied.")
        return self.waveform


    def augment_spectrogram(self, effects):
        """
        Adding augmentation to the spectrogram
        """

        self.waveform = self.waveform.transpose(0, 1)
        f, t, Sxx = scipy.signal.spectrogram(self.waveform, fs=self.sample_rate)  
        log_spectrogram = np.log(Sxx + 1e-10)  
        self.spec_mask = log_spectrogram.copy()

        if 'TimeMasking' in effects:
            """
            Time Masking in audio augmentation refers to a technique 
            used to enhance the robustness of audio models by randomly hiding 
            segments of the audio signal over time
            """

            for _ in range(self.num_masks):
                t_start = np.random.randint(0, self.spec_mask.shape[1] - self.time_mask_param + 1)
                self.spec_mask[:, t_start:t_start + self.time_mask_param] = 0

        elif 'FrequencyMasking' in effects:
            """
            Frequency Masking in audio augmentation is a technique 
            used to improve the robustness of audio models by randomly 
            occluding or masking specific frequency ranges within an 
            audio signal.
            """

            for _ in range(self.num_masks):
                mask_start = np.random.randint(0, self.spec_mask.shape[2] - self.time_mask_param)
                self.spec_mask[:,:, mask_start:mask_start + self.time_mask_param] = 0

        print("The augmentation of the spectrogram is complete.")
        return self.spec_mask


    def process_audio(self, method, effects=None):
        """
        Audio processing depending on the selected method.
        """

        if method == 'audio':
            self.waveform = self.augment_audio()
            display(Audio(self.waveform.T, rate=self.sample_rate))
            return self.waveform, self.sample_rate

        elif method == 'spectrogram' and effects is not None:
            self.spec_mask = self.augment_spectrogram(effects)
            display(Audio(self.spec_mask.T, rate=self.sample_rate))
            return self.spec_mask, self.sample_rate
        else:
            print(f"Unknown method: {method}")
