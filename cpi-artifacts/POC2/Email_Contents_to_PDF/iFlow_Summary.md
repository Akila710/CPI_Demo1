Email Contents to PDF iFlow Documentation
=====================================

### 1. High-level Architecture

The Email Contents to PDF iFlow is designed to retrieve email contents from a sender system, convert the email body into a PDF document, and send the PDF attachment to a receiver system. The iFlow uses SAP Cloud Platform Integration (CPI) to integrate the sender and receiver systems.

### 2. Purpose

The purpose of this iFlow is to demonstrate how to use CPI to integrate email systems and convert email contents into PDF documents.

### 3. Sender/Receiver Systems

*   **Sender System:** Gmail (IMAP)
*   **Receiver System:** Gmail (SMTP)

### 4. Adapter Types Used

*   **Sender Adapter:** Mail (IMAP)
*   **Receiver Adapter:** Mail (SMTP)

### 5. Step-by-Step Flow Explanation

1.  The iFlow starts with a **Start Event** that triggers the flow.
2.  The **Content Modifier** step is used to extract the email body from the incoming message.
3.  The **Groovy Script** step is used to convert the email body into a PDF document using the iText library.
4.  The **End Event** marks the end of the flow.

### 6. Mapping Logic Summary (XML/JSON/XSLT)

No mapping logic is used in this iFlow, as the email body is directly converted into a PDF document using the Groovy script.

### 7. Groovy Script Logic Explanation

The Groovy script is used to convert the email body into a PDF document. The script:

*   Reads the email body from the incoming message
*   Creates a PDF document using the iText library
*   Adds the email body to the PDF document
*   Returns the PDF document as a byte array

The script also creates two attachments with different names (Message_A.pdf and Message_B.pdf) and sets the email body to "Attached is the original email content in PDF format (two copies)."

### 8. Error Handling

Error handling is not explicitly implemented in this iFlow. However, CPI provides built-in error handling mechanisms, such as retry mechanisms and error messages, to handle errors that may occur during the execution of the iFlow.

### 9. Security/Authentication

The iFlow uses basic authentication to connect to the sender and receiver email systems. The username and password are stored in the adapter configurations.

### 10. High-Level Mermaid Diagram

```mermaid
graph TD
    A[Start Event] -->|Triggers Flow|> B[Content Modifier]
    B -->|Extracts Email Body|> C[Groovy Script]
    C -->|Converts Email Body to PDF|> D[End Event]
    D -->|Sends PDF Attachment|> E[Receiver System]
```

Note: This documentation is based on the provided iFlow code and may not be comprehensive or up-to-date. It is recommended to review the iFlow code and configuration to ensure accuracy and completeness.
