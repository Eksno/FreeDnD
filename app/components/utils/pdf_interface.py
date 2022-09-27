from pathlib import Path
import aspose.words as aw


# Load the PDF file
doc = aw.Document(
    str(
        Path(
            "C:\\Users\\Eksno\\Documents\\GitHub\\OpenDnD\\app\\components\\utils\\testing.pdf"
        )
    )
)

# Save the document as HTML
doc.save(
    str(
        Path(
            "C:\\Users\\Eksno\\Documents\\GitHub\\OpenDnD\\app\\components\\utils\\testing.html"
        )
    )
)
