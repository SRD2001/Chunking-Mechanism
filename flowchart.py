# from graphviz import Digraph
# from PIL import Image

# # Create a new directed graph
# flowchart = Digraph("Detailed File Chunking Process", node_attr={'shape': 'box'}, format="png")

# # Start
# flowchart.node("Start", "User initiates Upload/Download")

# # Decision: Upload or Download?
# flowchart.node("Decision", "Upload or Download?")
# flowchart.edge("Start", "Decision")

# # Upload Process
# flowchart.node("Chunking", "Chunk File\n(Split into parts)")
# flowchart.edge("Decision", "Chunking", label="Upload")

# # Metadata Creation for Upload
# flowchart.node("Metadata_Upload", "Create Metadata\n(File Name, Chunk Size, Chunk Count)")
# flowchart.edge("Chunking", "Metadata_Upload")

# # Parallel Upload
# flowchart.node("Parallel_Upload", "Parallel Upload of Chunks")
# flowchart.edge("Metadata_Upload", "Parallel_Upload")

# # Upload Progress Tracking
# flowchart.node("Upload_Progress", "Track Upload Progress")
# flowchart.edge("Parallel_Upload", "Upload_Progress")

# # Upload Error Handling
# flowchart.node("Upload_Retry", "Retry Failed Chunks")
# flowchart.edge("Parallel_Upload", "Upload_Retry", label="Error")
# flowchart.edge("Upload_Retry", "Parallel_Upload")

# # Upload Success/Failure Check
# flowchart.node("Upload_Success", "All Chunks Uploaded?")
# flowchart.edge("Parallel_Upload", "Upload_Success", label="No")
# flowchart.edge("Upload_Success", "Upload_Retry", label="No")
# flowchart.edge("Upload_Success", "Merge_Upload", label="Yes")

# # Merge Chunks After Upload
# flowchart.node("Merge_Upload", "Merge Uploaded Chunks")
# flowchart.edge("Upload_Success", "Merge_Upload", label="Yes")

# # Integrity Check After Upload
# flowchart.node("Upload_Integrity", "Verify Upload Integrity\n(Hash Verification)")
# flowchart.edge("Merge_Upload", "Upload_Integrity")

# # Completion of Upload
# flowchart.node("Upload_Complete", "Upload Complete\nNotify User")
# flowchart.edge("Upload_Integrity", "Upload_Complete")

# # Download Process
# flowchart.node("Download_Metadata", "Retrieve File Metadata\n(Total Chunks, Chunk Locations)")
# flowchart.edge("Decision", "Download_Metadata", label="Download")

# # Parallel Download
# flowchart.node("Parallel_Download", "Parallel Download of Chunks")
# flowchart.edge("Download_Metadata", "Parallel_Download")

# # Download Progress Tracking
# flowchart.node("Download_Progress", "Track Download Progress")
# flowchart.edge("Parallel_Download", "Download_Progress")

# # Download Error Handling
# flowchart.node("Download_Retry", "Retry Failed Chunks")
# flowchart.edge("Parallel_Download", "Download_Retry", label="Error")
# flowchart.edge("Download_Retry", "Parallel_Download")

# # Download Success/Failure Check
# flowchart.node("Download_Success", "All Chunks Downloaded?")
# flowchart.edge("Parallel_Download", "Download_Success", label="No")
# flowchart.edge("Download_Success", "Download_Retry", label="No")
# flowchart.edge("Download_Success", "Merge_Download", label="Yes")

# # Merge Chunks After Download
# flowchart.node("Merge_Download", "Merge Downloaded Chunks")
# flowchart.edge("Download_Success", "Merge_Download", label="Yes")

# # Integrity Check After Download
# flowchart.node("Download_Integrity", "Verify Download Integrity\n(Hash Verification)")
# flowchart.edge("Merge_Download", "Download_Integrity")

# # Completion of Download
# flowchart.node("Download_Complete", "Download Complete\nNotify User")
# flowchart.edge("Download_Integrity", "Download_Complete")

# # Render the graph to a file
# output_path = "C:/Users/sharad.pandey/Desktop/detailed_flowchart"
# flowchart.render(output_path, format="png")

# # Open the generated image in VS Code using PIL
# img = Image.open(output_path + ".png")
# img.show()

# print("Detailed flowchart generated and displayed.")









from graphviz import Digraph
from PIL import Image

# Create a new directed graph
flowchart = Digraph("Detailed File Chunking Process", node_attr={'shape': 'box'}, format="png")

# Start
flowchart.node("Start", "User initiates Upload/Download")

# Authentication & Authorization
flowchart.node("Auth", "Authenticate User")
flowchart.edge("Start", "Auth")

# Decision: Upload or Download?
flowchart.node("Decision", "Upload or Download?")
flowchart.edge("Auth", "Decision")

# Session Management
flowchart.node("Session_Expired", "Session Expired\nPrompt User to Login Again")
flowchart.edge("Auth", "Session_Expired", label="Session Timeout")

# Upload Process
flowchart.node("Chunking", "Chunk File\n(Split into parts)")
flowchart.edge("Decision", "Chunking", label="Upload")

# Metadata Creation for Upload
flowchart.node("Metadata_Upload", "Create Metadata\n(File Name, Chunk Size, Chunk Count)")
flowchart.edge("Chunking", "Metadata_Upload")

# Dynamic Chunk Size Adjustment
flowchart.node("Dynamic_Chunk_Size", "Adjust Chunk Size Dynamically")
flowchart.edge("Metadata_Upload", "Dynamic_Chunk_Size", label="Optimize for Network")

# Parallel Upload
flowchart.node("Parallel_Upload", "Parallel Upload of Chunks")
flowchart.edge("Dynamic_Chunk_Size", "Parallel_Upload")

# Encrypt File Chunks (Optional)
flowchart.node("Encrypt", "Encrypt File Chunks")
flowchart.edge("Dynamic_Chunk_Size", "Encrypt", label="If Encryption Enabled")

# Upload Progress Tracking
flowchart.node("Upload_Progress", "Track Upload Progress")
flowchart.edge("Encrypt", "Upload_Progress")

# Upload Error Handling
flowchart.node("Upload_Retry", "Retry Failed Chunks")
flowchart.edge("Parallel_Upload", "Upload_Retry", label="Error")
flowchart.edge("Upload_Retry", "Parallel_Upload")

# Upload Success/Failure Check
flowchart.node("Upload_Success", "All Chunks Uploaded?")
flowchart.edge("Upload_Progress", "Upload_Success", label="No")
flowchart.edge("Upload_Success", "Upload_Retry", label="No")
flowchart.edge("Upload_Success", "Merge_Upload", label="Yes")

# Merge Chunks After Upload
flowchart.node("Merge_Upload", "Merge Uploaded Chunks")
flowchart.edge("Upload_Success", "Merge_Upload", label="Yes")

# Integrity Check After Upload
flowchart.node("Upload_Integrity", "Verify Upload Integrity\n(Hash Verification)")
flowchart.edge("Merge_Upload", "Upload_Integrity")

# Versioning Update (if applicable)
flowchart.node("Versioning", "Update Versioning & Metadata")
flowchart.edge("Upload_Integrity", "Versioning")

# Completion of Upload
flowchart.node("Upload_Complete", "Upload Complete\nNotify User")
flowchart.edge("Versioning", "Upload_Complete")

# Download Process
flowchart.node("Download_Metadata", "Retrieve File Metadata\n(Total Chunks, Chunk Locations)")
flowchart.edge("Decision", "Download_Metadata", label="Download")

# Parallel Download
flowchart.node("Parallel_Download", "Parallel Download of Chunks")
flowchart.edge("Download_Metadata", "Parallel_Download")

# Download Progress Tracking
flowchart.node("Download_Progress", "Track Download Progress")
flowchart.edge("Parallel_Download", "Download_Progress")

# Download Error Handling
flowchart.node("Download_Retry", "Retry Failed Chunks")
flowchart.edge("Parallel_Download", "Download_Retry", label="Error")
flowchart.edge("Download_Retry", "Parallel_Download")

# Download Success/Failure Check
flowchart.node("Download_Success", "All Chunks Downloaded?")
flowchart.edge("Download_Progress", "Download_Success", label="No")
flowchart.edge("Download_Success", "Download_Retry", label="No")
flowchart.edge("Download_Success", "Merge_Download", label="Yes")

# Merge Chunks After Download
flowchart.node("Merge_Download", "Merge Downloaded Chunks")
flowchart.edge("Download_Success", "Merge_Download", label="Yes")

# Integrity Check After Download
flowchart.node("Download_Integrity", "Verify Download Integrity\n(Hash Verification)")
flowchart.edge("Merge_Download", "Download_Integrity")

# Completion of Download
flowchart.node("Download_Complete", "Download Complete\nNotify User")
flowchart.edge("Download_Integrity", "Download_Complete")

# Render the graph to a file
output_path = "C:/Users/sharad.pandey/Desktop/detailed_flowchart"
flowchart.render(output_path, format="png")

# Open the generated image in VS Code using PIL
img = Image.open(output_path + ".png")
img.show()

print("Detailed flowchart generated and displayed.")
