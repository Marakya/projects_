import unittest
import numpy as np
import torch
from .augment import AudioAugmentor

class TestAudioProcessor(unittest.TestCase):
    
    def setUp(self):
        """
        Initialization of test data (for the case with 1 channel)
        """

        self.sample_rate = 16000
        self.waveform = np.random.rand(self.sample_rate * 2,1)  # 2 seconds audio
        self.processor = AudioAugmentor(self.waveform, self.sample_rate)

    def test_initialization(self):
        """
        Initialization check
        """

        self.assertEqual(self.processor.sample_rate, self.sample_rate)
        self.assertEqual(self.processor.waveform.shape, (self.waveform.shape[1],1))
        self.assertEqual(self.processor.num_channels, 1)

    def test_add_white_noise(self):
        """
        Check that white noise is added to the audio
        """

        original_waveform = self.processor.waveform.clone()
        self.processor.add_white_noise()
        noise_added = torch.any(self.processor.waveform != original_waveform)
        self.assertTrue(noise_added.item(), "White noise was not added.")


    def test_augment_spectrogram_time_masking(self):
        """
        Checking augmentation with time masking
        """

        effects = ['TimeMasking']
        original_spec_mask = self.processor.augment_spectrogram(effects)
        self.assertFalse(np.array_equal(original_spec_mask, self.processor.spec_mask))


    def test_augment_spectrogram_frequency_masking(self):
        """
        Checking augmentation with frequency masking
        """

        effects = ['FrequencyMasking']
        original_spec_mask = self.processor.augment_spectrogram(effects)
        self.assertFalse(np.array_equal(original_spec_mask, self.processor.spec_mask))


    def test_augment_spectrogram_both_masks(self):
        """
        Augmentation check with both masks
        """

        effects = ['TimeMasking', 'FrequencyMasking']
        original_spec_mask = self.processor.augment_spectrogram(effects)
        self.assertFalse(np.array_equal(original_spec_mask, self.processor.spec_mask))

    def test_process_audio_method(self):
        """
        Checking that:
        the result has the correct shape (two-dimensional tensor with one channel)
        the sampling rate has not changed
        The signal length has not decreased to 0
        """

        result_waveform, rate = self.processor.process_audio('audio')
        self.assertEqual(result_waveform.shape[1], 1)
        self.assertEqual(rate, self.sample_rate)
        self.assertGreater(result_waveform.shape[0], 0)

    def test_process_spectrogram_method(self):
        """
        Checking the correct processing of the audio spectrogram
        """

        effects = ['TimeMasking']
        result_spec_mask, rate = self.processor.process_audio('spectrogram', effects)
        self.assertEqual(result_spec_mask.shape[0], 1)  
        self.assertEqual(rate, self.sample_rate)


    def test_invalid_method(self):
        """
        Checking processing with a non-existent method
        """

        with self.assertRaises(Exception):
            self.processor.process_audio('invalid_method')


    def test_stereo_waveform_initialization(self):
        """
        Test for stereo audio
        """

        stereo_waveform = np.random.rand(self.sample_rate * 2, 2)  # 2 channels
        processor = AudioAugmentor(stereo_waveform, self.sample_rate)
        self.assertEqual(processor.num_channels, 2)
        self.assertEqual(processor.waveform.shape, (self.sample_rate * 2, 1))  # Must be converted to mono


if __name__ == '__main__':
    unittest.main()
