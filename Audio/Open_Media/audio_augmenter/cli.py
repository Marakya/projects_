import click
import numpy as np
from .utils import read_audio, save_audio
from .augment import AudioAugmentor

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--method', type=click.Choice(['audio', 'spectrogram'], case_sensitive=False), default='audio', help='Choose the augmentation method: audio or spectrogram.')
@click.option('--effects', type=click.Choice(['FrequencyMasking', 'TimeStretching'], case_sensitive=False), default=None, help='Choose one effect to apply when using spectrogram method.')
def main(input_file, output_file, method,effects):
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

    
    if method == 'audio':
      audio, sr = augmentor.process_audio(method=method)
      # Saving an augmented signal
      save_audio(output_file, audio, sr)
    elif method == 'spectrogram': 
      if effects:
            spectr, sr = augmentor.process_audio(method=method, effects=[effects])
            # Saving an augmented signal
            save_audio(output_file, spectr, sr)
      else:
            click.echo("No effect provided for spectrogram method. Please specify an effect.")

    click.echo(f"The audio has been successfully saved in: {output_file}!")
    

if __name__ == '__main__':
    main()

