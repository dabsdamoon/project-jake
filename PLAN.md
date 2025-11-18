# Plan for chatting pipeline

## Terminologies
- JAKE: 자캐 in Korean - abbreviation for "자기 캐릭터", a self-made persona 

## Purpose
- Combine components to create AI chatting agent with JAKE of own.

## Process
1. Create character via JAKECreator.
2. Save created JAKE in database. 
3. Load JAKE created
4. Insert JAKE's information in prompt, and use that prompt for JAKEChatter
5. After chat, run JAKEChecker, JAKEDynamicProfiler, and JAKESummarizer concurrently. If number of history (turn) is less than 3, run JAKESummarizer only. If number of history < 10, run JAKEChecker and JAKESummarizer only. If n < 10, run all 3. 
6. Embed chat history and save embedding in vector database. Also, if JAKEDynamicProfiler has been run, update JAKE database with "additional information"