import click
import numpy as np
from .utils import read_audio, save_audio
from .augment import AudioAugmentor

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def main(input_file, output_file):
    """
    CLI is an application for augmentation of audio files.
    """

    click.echo(f"Reading an audio file: {input_file}")
    
    audio, sr = read_audio(input_file)
    
    click.echo("Audio augmentation...")
    augmentor = AudioAugmentor(audio, sr)

    """
    The choice of the augmentation method. 
    In this work, two types of augmentation are considered: 
    raw audio augmentation and audio signal spectrogram augmentation. 
    Audio spectrogram augmentation is widely used in speech recognition tasks.
    Below you can select an 'audio' or 'spectrogram' to perform the augmentation
    """

    method_to_use = 'audio'  # Or 'spectrogram'
    if method_to_use == 'audio':
      audio, sr = augmentor.process_audio(method=method_to_use)
      # Saving an augmented signal
      save_audio(output_file, audio, sr)
    else: 
      effects_spectr = ['FrequencyMasking']
      spectr, sr = augmentor.process_audio(method=method_to_use, effects = effects_spectr)
      # Saving an augmented signal
      save_audio(output_file, spectr, sr)
    
    click.echo(f"The audio has been successfully saved in: {output_file}!")
    

if __name__ == '__main__':
    main()

