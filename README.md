Serverless Secrets
===

This is a tiny website that you can use to exchange one-time secrets. For example, send an API key to a new customer, or send a new password to your new colleague. You can host this service for virtually nothing on AWS Lambda, the secrets are stored in DynamoDB. I built this for my current company easee, after years of working with a similar tool at Mendix.

Design goals
---

- Users can upload a one-time secret via a web interface and receive a URL, they can send this URL to the receiver, once the receiver opens the URL, the secret is displayed and purged from storage.
- The service should be trivially easy to self-host on AWS, because you don't want to use 3rd party services to store all your secrets, these services would be perfect honeypots. You should be able to see and understand all the code that you deploy.
- Secrets should expire after a user-determined time (max 7 days).
- It should be really tiny, a couple hundred lines of code at maximum, so the attack surface is reduced. I want to add Google SSO and Slack integration at some point, but I will do that in a fork.
- Scraping bots should not be able to download the secrets.
- There should be no cookies or externally hosted CSS, JS or fonts.
- It should be easy to use.
- There should be no dependencies except what comes included in the Lambda python.
- Secrets should not be plaintext visible to operators that inspect the AWS DynamoDB interface.
