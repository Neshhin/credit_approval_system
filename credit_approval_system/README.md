# Credit Approval System

A Django-based REST API system for managing credit approvals and loans based on customer creditworthiness.

## Features

- Customer registration with automatic credit limit calculation
- Credit score calculation based on loan history
- Loan eligibility checking with dynamic interest rate adjustment
- Loan creation and management
- Comprehensive loan and customer viewing endpoints
- Background task processing with Celery
- Dockerized deployment with PostgreSQL

## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL 15
- **Task Queue**: Celery + Redis
- **Container**: Docker & Docker Compose
- **Language**: Python 3.11

## Project Structure

