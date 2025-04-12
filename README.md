# LLM-EHR: Building an Electronic Health Record system with a linked Language Model

## Overview

LLM-EHR is a project that aims to build an Electronic Health Record (EHR) system that is linked with a language model. The project is designed to demonstrate how to integrate a language model with an EHR system to provide better patient care and improve clinical decision-making.

The main feature of the system is wherein the doctor uploads an audio conversation with the patient, and the system transcribes the audio to text. The transcribed text is then sent to a language model (Gemini) to generate a summary of the conversation. The summary is then stored in the EHR system.

This project can also be extended to include other features such as generating a summary of the patient's medical history, generating a list of medications, and generating a list of allergies.

The project is built using Python and Flask, and it uses the Gemini API for the language model. The EHR system is built using SQLite for simplicity, but it can be easily replaced with a more robust database system.

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/josh1221wa/llm_ehr
cd llm_ehr
```

### Step 2: Create a virtual environment

It is recommended to create a conda virtual environment, with Python 3.11, to avoid conflicts with other projects. This is because the project would be using libraries such as `transformers`, and `pytorch`, which may work better on a conda environment.

```bash
conda create -n llm_ehr python=3.11
conda activate llm_ehr
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Pytorch (choose the appropriate command for your system)

Refer to the [Pytorch installation page](https://pytorch.org/get-started/locally/) for the latest instructions.

### Step 5: Get the Gemini API key

You will need to sign up for the Gemini API and get your API key. Refer [Google Support](https://ai.google.dev/gemini-api/docs/api-key).

Once you have the API key, create a `tokens.env` file in the root directory of the project and add your API key:

```bash
GEMINI_API_KEY=your_api_key_here
```

### Step 6: Run the application

```bash
python app.py
```

## Conclusion

This project is a simple demonstration of how to integrate a language model with an EHR system. It can be extended to include more features and can be used as a starting point for building a more robust EHR system.

Happy coding❤️!
