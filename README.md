<div id="top"></div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Logo" width="80" height="80">

  <h3 align="center">Inference API - LLM & TTS Service</h3>

  <p align="center">FastAPI-based inference service for Large Language Models (LLM) and Text-to-Speech (TTS) with Bearer token authentication, dependency injection, and background event processing.</p>
</div>

 <br />  

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">🧭 About The Project</a>
      <ul>
        <li><a href="#built-with">🏗️ Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">📋 Getting Started</a>
      <ul>
        <li><a href="#prerequisites">🗺️ Prerequisites</a></li>
        <li><a href="#installation">⚙️ Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">💾 Usage</a></li>
    <li><a href="#api-endpoints">🔌 API Endpoints</a></li>
    <li><a href="#architecture">🏛️ Architecture</a></li>
    <li><a href="#contributing">🔗 Contributing</a></li>
    <li><a href="#license">📰 License</a></li>
    <li><a href="#contact">📫 Contact</a></li>
    <li><a href="#acknowledgments">⛱️ Acknowledgments</a></li>
  </ol>
</details>

<br>



<!-- ABOUT THE PROJECT -->
## 🧭 About The Project

This project provides a production-ready inference API service for running Large Language Models (LLM) and Text-to-Speech (TTS) models. It features:

- **Multiple LLM Models**: Support for Qwen, Dolphin GGUF variants, and custom models
- **TTS Models**: Facebook MMS TTS for French and English
- **Background Processing**: Asynchronous event queue for processing Riot game incoming events
- **Dependency Injection**: Clean architecture with service layer pattern
- **Object Storage**: DigitalOcean Spaces integration for audio file storage
- **Database Integration**: PostgreSQL for event tracking and job management
- **Real-time Updates**: Server-Sent Events (SSE) for event status streaming

### 🏗️ Built With

* [![Python Badge](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
* [![FastAPI Badge](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
* [![PyTorch Badge](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=PyTorch&logoColor=white)](https://pytorch.org/)
* [![Transformers Badge](https://img.shields.io/badge/_Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/transformers/)
* [![PostgreSQL Badge](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
* [![DigitalOcean Badge](https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=DigitalOcean&logoColor=white)](https://www.digitalocean.com/)
* [![Uvicorn Badge](https://img.shields.io/badge/Uvicorn-5E4F47?style=for-the-badge&logo=uvicorn&logoColor=white)](https://www.uvicorn.org/)

<p align="right"><a href="#top">⬆️</a></p>




<!-- GETTING STARTED -->
## 📋 Getting Started

To get a local copy up and running follow these simple example steps.

### 🗺️ Prerequisites

* [mise](https://mise.jdx.dev/)
* PostgreSQL database
* DigitalOcean Spaces account (or any S3-compatible storage)
* CUDA-capable GPU (recommended for model inference)

### ⚙️ Installation

1. **Clone the repository**
```sh
   git clone https://github.com/Ouilliam-21/inference
   cd inference
```
2. **Install dependencies using mise**
```sh
mise trust
mise install
```
3. **Active python env**
```sh 
   mise exec -- python -m venv venv
   mise exec -- source venv/bin/activate
   mise exec -- pip install -r requirements.txt
``` 
4. **Create environment file**
   
   Create a `.env` file at the root of the project:
   AUTH_TOKEN=your_secret_bearer_token_here
   
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   
   SPACES_ACCESS_KEY=your_access_key
   SPACES_SECRET_KEY=your_secret_key
   SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
   SPACES_BUCKET=your-bucket-name
   SPACES_REGION=nyc3
   
   Copy the example config file:
   ```sh 
   cp server/config.example.yaml server/config.yaml
   ``` 
    
    Edit `server/config.yaml` to customize prompts and event templates.

5. **Set up the database**
   
   Ensure PostgreSQL is running and create the database
   
<p align="right"><a href="#top">⬆️</a></p>


<!-- USAGE EXAMPLES -->
## 💾 Usage

### Development Mode

Start the development server with hot reload:

```sh
mise run dev
```

Or with a custom config file:

```sh
mise run dev:custom
```

Once the server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc


### Example API Calls

In the **mise.toml** file, you'll find a list of curl cmd to test the API


<!-- API ENDPOINTS -->
## 🔌 API Endpoints

All endpoints require Bearer token authentication in the `Authorization` header.

<p align="right"><a href="#top">⬆️</a></p>


<!-- ARCHITECTURE -->
## 🏛️ Architecture

The project follows a clean architecture pattern with dependency injection:
```sh
inference/
├── ai/                   # AI models (LLM & TTS)
│   ├── models/           # Model implementations
│   └── prompts/          # Prompt management
├── database/             # Database models and access
├── dependencies/         # Dependency injection container
├── externals/            # External services (Object Storage)
├── middlewares/          # HTTP middlewares (Auth, CORS)
├── routes/               # API route handlers
├── schemas/              # Pydantic schemas
├── services/             # Business logic layer
└── server/               # Server configuration
```


Key Features:
- **Service Layer**: Business logic separated from HTTP layer
- **Dependency Injection**: FastAPI's `Depends()` for clean dependencies
- **Background Workers**: Asynchronous event processing
- **Model Registry**: Centralized model management
- **State Management**: Singleton pattern for shared resources

<p align="right"><a href="#top">⬆️</a></p>


<!-- CONTRIBUTING -->
## 🔗 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right"><a href="#top">⬆️</a></p>




<!-- LICENSE -->
## 📰 License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right"><a href="#top">⬆️</a></p>




<!-- CONTACT -->
## 📫 Contact

Reach me at : gauron.dorian.pro@gmail.com

Project Link: [https://github.com/yourusername/oui-lliam](https://github.com/yourusername/oui-lliam)

<p align="right"><a href="#top">⬆️</a></p>




<!-- ACKNOWLEDGMENTS -->
## ⛱️ Acknowledgments

This space is a list to resources i found helpful and would like to give credit to.

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
* [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
* [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
* [DigitalOcean Spaces](https://www.digitalocean.com/products/spaces)
* [mise - Runtime Version Manager](https://mise.jdx.dev/)

<p align="right"><a href="#top">⬆️</a></p>

<a href="https://github.com/othneildrew/Best-README-Template">Template inspired by othneildrew</a>