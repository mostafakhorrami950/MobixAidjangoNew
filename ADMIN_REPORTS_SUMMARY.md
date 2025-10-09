# Admin Panel Reports Summary

## Overview

This document summarizes the comprehensive reporting functionality that has been added to the Django admin panel without making changes to other parts of the project. All reports extract data directly from the database and provide accurate statistics.

## Reports Added

### 1. OpenRouter Request Cost Reports

Accessible through: **Admin Panel → Chatbot → OpenRouter Request Costs**

#### Reports Included:
1. **Top Users by OpenRouter Cost**
   - Shows users with the highest OpenRouter API costs
   - Displays total cost in USD, total tokens used, and request count

2. **Top AI Models by Usage**
   - Shows most frequently used AI models
   - Displays usage count, total tokens, and total cost in USD

3. **Top Free AI Models Usage**
   - Shows usage statistics for free AI models only
   - Displays usage count and total tokens

4. **Average Token Usage**
   - Shows average tokens per request across all users

5. **Top Chatbots by Session Count**
   - Shows most popular chatbots based on session creation
   - Displays session count and total messages

### 2. User Reports

Accessible through: **Admin Panel → Accounts → Users**

#### Reports Included:
1. **Top Users by OpenRouter Cost**
   - Shows users with the highest OpenRouter API costs
   - Displays total cost in USD, total tokens used, and request count

2. **Top Users by Free Model Usage**
   - Shows users with the highest usage of free AI models
   - Displays total tokens and request count

3. **Average Token Usage**
   - Shows average tokens per request across all users

### 3. AI Model Reports

Accessible through: **Admin Panel → AI Models → AI Models**

#### Reports Included:
1. **Top AI Models by Usage**
   - Shows most frequently used AI models
   - Displays usage count, total tokens, and total cost in USD

2. **Top Free AI Models Usage**
   - Shows usage statistics for free AI models only
   - Displays usage count and total tokens

### 4. Chatbot Reports

Accessible through: **Admin Panel → Chatbot → Chatbots**

#### Reports Included:
1. **Top Chatbots by Session Count**
   - Shows most popular chatbots based on session creation
   - Displays session count and total messages

## Data Accuracy

All reports extract data directly from the database using Django ORM queries, ensuring:
- Real-time data accuracy
- No manual calculations or estimations
- Consistent with actual usage records
- Efficient database queries with proper aggregation

## Technical Implementation

### Models Used for Reporting:
1. **OpenRouterRequestCost** - Primary source for cost and usage data
2. **ChatSession** - Source for chatbot usage statistics
3. **AIModel** - Source for model information and free model identification
4. **User** - Source for user information

### Key Features:
- Uses Django's aggregation functions (Sum, Count, Avg) for efficient calculations
- Implements proper filtering for free models vs. paid models
- Uses `apps.get_model()` to access models without direct imports
- Follows Django admin best practices for custom views
- Provides clean, readable reports with proper formatting

## Access Instructions

1. Log into the Django admin panel
2. Navigate to the relevant section (Chatbot, Accounts, or AI Models)
3. Click on the model name to view the changelist page
4. Reports will be displayed at the top of the page above the standard model list

## Report Refresh

Reports are generated dynamically each time the admin page is loaded, ensuring:
- Up-to-date information
- No caching issues
- Real-time visibility into system usage

## Data Privacy

All reports maintain user privacy by:
- Showing only aggregate statistics
- Not displaying individual message content
- Following existing data access patterns
- Maintaining existing authentication and authorization controls