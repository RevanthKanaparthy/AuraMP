# AURA Project Overview

## Abstract

AURA (AI-Powered Unified Repository Application) is a comprehensive full-stack web application designed to serve as an intelligent research knowledge base for educational institutions. The system combines advanced document management, AI-powered semantic search, and administrative controls to facilitate efficient access to academic resources including research papers, patents, project reports, and faculty publications.

## Introduction

AURA (AI-Powered Unified Repository Application) is a system designed to address the challenges of managing and accessing a growing body of academic and research information within an educational institution. This document outlines the project's objectives, motivation, and technical scope.

### Problem Statement

Educational institutions produce a vast amount of research materials, including papers, project reports, and patents. These resources are often stored in disparate locations and formats, making it difficult for students, faculty, and researchers to find relevant information efficiently. There is a need for a centralized system that not only stores these documents but also provides intelligent search capabilities to uncover insights and connections within the knowledge base.

### Objective

The primary objective of the AURA project is to develop a unified, AI-powered repository for academic and research documents. The system aims to provide a centralized platform for storing, managing, and querying research materials using natural language, thereby improving the accessibility and utility of the institution's intellectual assets.

### Motivation

The motivation behind AURA is to empower researchers, students, and faculty by providing them with a powerful tool for knowledge discovery. By leveraging AI and semantic search, the system aims to accelerate research, foster inter-departmental collaboration, and provide administrators with valuable insights into the institution's research output.

### Scope

The scope of the AURA project includes:
- A secure, multi-role user authentication system (Admin, Faculty, Student).
- A document management system supporting PDF, DOCX, and XLSX formats.
- An AI-powered query interface using Retrieval-Augmented Generation (RAG) for natural language questions.
- An administrative dashboard for user and document management.
- The system is designed for deployment within an institution's local network.

### Software and Hardware Requirements

#### Software Requirements:
- **Backend:** Python 3.7+, FastAPI, PostgreSQL, Ollama with Llama3.2:3b model.
- **Frontend:** Node.js, React, TypeScript.
- **Operating System:** A server environment (e.g., Linux, Windows Server) capable of running the above software.

#### Hardware Requirements:
- A server with sufficient CPU, RAM (to run the LLM), and disk space to host the application, database, and documents.
- Client machines with modern web browsers to access the application.

### Organisation Profile

This project was developed for the MVSR Research Intelligence Platform.
