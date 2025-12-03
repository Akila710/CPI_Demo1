import com.sap.gateway.ip.core.customdev.util.Message
import java.util.HashMap
import java.io.ByteArrayOutputStream
import javax.activation.DataHandler
import javax.mail.util.ByteArrayDataSource
import com.itextpdf.text.Document
import com.itextpdf.text.Paragraph
import com.itextpdf.text.pdf.PdfWriter

def Message processData(Message message) {

    // ✅ Directly read email body from incoming message
    def bodyText = message.getBody(String)

    // ✅ Function to convert text to PDF (returns byte[])
    def createPdf = { String content ->
        ByteArrayOutputStream output = new ByteArrayOutputStream()
        Document document = new Document()
        PdfWriter.getInstance(document, output)
        document.open()
        document.add(new Paragraph(content))
        document.close()
        return output.toByteArray()
    }

    // ✅ Generate PDF content
    byte[] pdfBytes = createPdf(bodyText)

    // ✅ Create attachments with different names (same content)
    def attachments = new HashMap<String, DataHandler>()
    def dataSource = new ByteArrayDataSource(pdfBytes, "application/pdf")
    def dataHandler = new DataHandler(dataSource)

    attachments.put("Message_A.pdf", dataHandler)
    attachments.put("Message_B.pdf", dataHandler)

    // ✅ Attach and set body text
    message.setAttachments(attachments)
    message.setBody("Attached is the original email content in PDF format (two copies).")

    return message
}
