Email Contents to PDF iFlow Documentation
==============================================

### 1. High-level Architecture

The Email Contents to PDF iFlow is designed to retrieve email contents from a sender system, convert the email body into a PDF document, and send the PDF attachment to a receiver system.

### 2. Purpose

The primary purpose of this iFlow is to demonstrate the conversion of email contents into a PDF document using a Groovy script and send it as an attachment to the receiver.

### 3. Sender/Receiver Systems

*   **Sender System:** The sender system is an email server (e.g., Gmail) that sends emails to the CPI system.
*   **Receiver System:** The receiver system is also an email server (e.g., Gmail) that receives emails with PDF attachments from the CPI system.

### 4. Adapter Types Used

*   **Mail Adapter:** The Mail adapter is used for both sender and receiver systems to send and receive emails.
*   **Groovy Script Adapter:** The Groovy script adapter is used to convert the email body into a PDF document.

### 5. Step-by-Step Flow Explanation

1.  The iFlow starts with a **Start Event** that triggers the process.
2.  The **Content Modifier** step is used to extract the email body from the incoming message.
3.  The **Groovy Script** step is used to convert the email body into a PDF document.
4.  The **End Event** sends the PDF attachment to the receiver system.

### 6. Mapping Logic Summary (XML/JSON/XSLT)

No mapping logic is used in this iFlow, as the email body is directly converted into a PDF document using a Groovy script.

### 7. Groovy Script Logic Explanation

The Groovy script is used to convert the email body into a PDF document. The script:

*   Reads the email body from the incoming message.
*   Creates a PDF document using the iText library.
*   Adds the email body to the PDF document.
*   Returns the PDF document as a byte array.
*   Creates attachments with different names (same content).
*   Sets the attachments and body text of the outgoing message.

### 8. Error Handling

Error handling is not explicitly implemented in this iFlow. However, the CPI system provides built-in error handling mechanisms, such as logging and alerting, to handle any errors that may occur during the execution of the iFlow.

### 9. Security/Authentication

The iFlow uses basic authentication for the Mail adapter. The username and password are stored in the adapter configuration.

### 10. High-Level Mermaid Diagram

```mermaid
graph TD
    A[Email Sender] --> B[CPI]
    B --> C[Email Receiver]
    B -->|PDF Attachment|> C
```

This diagram shows the high-level architecture of the iFlow, including the email sender, CPI system, and email receiver. The CPI system converts the email body into a PDF document and sends it as an attachment to the email receiver.
