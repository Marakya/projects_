# AudioAugmentor CLI Tool

A command-line interface tool for augmenting audio signals with various effects.

## Project Structure

![image](https://github.com/user-attachments/assets/32ce48f9-0bc0-4b74-8581-907eb92c72ce)


## Installation

Follow these steps to install and set up the CLI tool:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Marakya/projects_/tree/main/Audio/Open_Media 
   ```

2. **Navigate to the project directory:**
     ```
     cd yourproject
     ```

3. **Create a virtual environment:**
      ```
      python -m venv venv
      ```
4. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```
5. **Install the dependencies:**
      ```
      pip install -r requirements.txt
      ```
6. **Install the package:**
      ```
      pip install .
      ```

## Usage 

To use the CLI tool, follow these steps:

1. **Run the CLI tool:**
   ```
   python -m audio_augmenter.cli path/to/input/file path/to/output/file --method audio
   ```
   
In this work, two types of augmentation are considered: raw audio augmentation and audio signal spectrogram augmentation. Audio spectrogram augmentation is widely used in speech recognition tasks.


Replace *path/to/input/file* with the path to your input audio file, *path/to/output/file* with the desired output path, and choose a processing method ('audio' or 'spectrogram').


2. **Command Options:**
     
   **--method or -m:** Method to use for processing. Options: audio, spectrogram.
   
   **--effects or -e:** Effects to apply when using the spectrogram method. Options: TimeMasking, FrequencyMasking.


3. **Examples:**

- Process an audio file with default settings:
  ```
  python -m audio_augmenter.cli audio.wav augmented_audio.wav --method audio
  ```

- Apply a spectrogram augmentation with time masking:
  ```
  python -m audio_augmenter.cli audio.wav augmented_spectrogram.wav --method spectrogram --effects TimeMasking
  ```
  
## Running Tests


To ensure that everything is working correctly, you can run the tests with the following command:

- If you want to run tests from a specific file, you can specify the file directly:
  ```
  python -m unittest tests.test_augment
  ```
  
- You can run unittest directly from the command line. To discover and run tests, use:
  ```
  python -m unittest discover -s tests
  ```
  


   



