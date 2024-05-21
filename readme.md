## About Streamlit LLM Chatbot

Streamlit LLM Chatbot brings the power of AI-driven chat interfaces to developers and users, running directly on your machine. This project leverages Streamlit along with the Azure OpenAI service, offering an intuitive interface to interact with AI, while providing options to enhance chats with local project context such as file structures, recent changes, and more.

### Core Features
- **Chat Session Management**: Create, rename, and delete chat sessions with ease.
- **Project Context Integration**: Append file structure, list recent changes, or include all file contents within the chat context to aid in AI-driven project understanding.
- **Smart Session Naming**: Utilize AI to generate meaningful names for chat sessions based on the context.
- **Privacy-Preserving**: All chat sessions are stored locally, ensuring that your data remains private and secure.
- **Easy To Customize**: Thanks to the simplicity of the Streamlit 

### Getting Started

To get started with Streamlit LLM Chatbot, clone this repository to your local machine:

```bash
git clone https://github.com/rafaelsanchezsouza/streamlit-chatbot-interface.git
cd streamlit-chatbot-interface
```

Ensure you have the required dependencies by running:

```bash
pip install -r requirements.txt
```

To run the application, navigate to the project root directory and execute:

```bash
streamlit run app.py
```

### Development and Contributions

Streamlit LLM Chatbot is an open-source project and contributions are welcome. See `CONTRIBUTING.md` for more details on how to contribute, report issues, or submit pull requests.

### Roadmap

- **[In Progress]** Enhance context integration.
- **[Planned]** Solution refactoring for more modularity.
- **[Planned]** Extend backend support to include additional AI services.
- **[Planned]** Document editing.

## Acknowledgments

- This project utilizes the [Azure OpenAI service](https://azure.microsoft.com/en-us/services/cognitive-services/openai-service/) for AI-driven interactions.
- Built completely thanks to [Streamlit Chatbot Interface](https://github.com/daveebbelaar/streamlit-chatbot-interface).

## Citation

If you find this project useful, please consider citing it in your work:

```bibtex
@software{streamlit-chatbot-interface,
  title = {{Streamlit LLM Chatbot: Local AI-driven Chat Interface with Enhanced Project Context}},
  author = {Streamlit, Rafael Sanchez Souza and ChatGPT},
  url = {https://github.com/rafaelsanchezsouza/streamlit-chatbot-interface},
  year = {2024}
}
```

---
Please adjust placeholders (`https://github.com/rafaelsanchezsouza/streamlit-chatbot-interface`, `https://discord.gg/your-invite-link`, `Rafael Sanchez Souza`, etc.) with your actual project details before making this README public.
