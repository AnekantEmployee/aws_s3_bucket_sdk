import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from services.s3_service import S3Manager
from services.utils import format_file_size, format_file_info
from PIL import Image
import io

load_dotenv()

# Configuration
AWS_ACCESS_KEY = os.getenv("ACCESS_KEY")  # Fixed typo: was "ACEESS_KEY"
AWS_SECRET_KEY = os.getenv("SECRET_ACCESS_KEY")  # Fixed typo: was "SECRET_ACESS_KEY"
AWS_REGION = "ap-south-1"  # Or your preferred region
BUCKET_NAME = "my-photos-manager02"  # Replace with your bucket name


# Initialize session state
def initialize_session_state():
    if "s3_manager" not in st.session_state:
        st.session_state.s3_manager = S3Manager()
        try:
            if st.session_state.s3_manager.initialize_client(
                AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
            ):
                st.session_state.aws_connected = True
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            st.session_state.aws_connected = False


def is_image_file(filename):
    """Check if file is an image based on extension"""
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def display_image_preview(file_content, max_width=200):
    """Display image preview from file content"""
    
    try:
        image = Image.open(io.BytesIO(file_content))
        # Resize image to fit within max_width while maintaining aspect ratio
        image.thumbnail((max_width, max_width))
        return image
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None


def render_image_grid(objects):
    """Render images in a 3-column grid with details below"""
    if not objects:
        st.info("No files found in this bucket")
        return

    # Filter image files
    image_objects = [obj for obj in objects if is_image_file(obj["Key"])]
    non_image_objects = [obj for obj in objects if not is_image_file(obj["Key"])]

    if image_objects:
        st.subheader("📸 Image Preview Grid")

        # Display images in grid format (3 columns)
        cols_per_row = 3
        for i in range(0, len(image_objects), cols_per_row):
            cols = st.columns(cols_per_row)

            for j, col in enumerate(cols):
                if i + j < len(image_objects):
                    obj = image_objects[i + j]

                    with col:
                        try:
                            # Download image for preview
                            file_content = st.session_state.s3_manager.download_file(
                                BUCKET_NAME, obj["Key"]
                            )

                            if file_content:
                                image = display_image_preview(file_content)
                                if image:
                                    st.image(
                                        image,
                                        caption=obj["Key"],
                                        use_container_width=True,
                                    )

                                    # Image details
                                    st.caption(f"📏 {format_file_size(obj['Size'])}")
                                    st.caption(
                                        f"📅 {obj['LastModified'].strftime('%Y-%m-%d %H:%M')}"
                                    )

                                    # Download button for each image
                                    if st.button(
                                        f"⬇️ Download", key=f"download_{obj['Key']}"
                                    ):
                                        st.download_button(
                                            label="💾 Save Image",
                                            data=file_content,
                                            file_name=obj["Key"],
                                            mime="image/*",
                                            key=f"save_{obj['Key']}",
                                        )
                            else:
                                st.error(f"Failed to load: {obj['Key']}")

                        except Exception as e:
                            st.error(f"Error loading {obj['Key']}: {str(e)}")

        st.markdown("---")

    # Display all files in tabular format
    st.subheader("📋 All Files Details")

    all_objects = image_objects + non_image_objects
    if all_objects:
        df_data = []
        for obj in all_objects:
            file_type = "🖼️ Image" if is_image_file(obj["Key"]) else "📄 File"
            df_data.append(
                {
                    "Type": file_type,
                    "File Name": obj["Key"],
                    "Size": format_file_size(obj["Size"]),
                    "Last Modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
                    "Storage Class": obj["StorageClass"],
                }
            )

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", len(all_objects))
        with col2:
            st.metric("Images", len(image_objects))
        with col3:
            st.metric("Other Files", len(non_image_objects))
    else:
        st.info("No files found in this bucket")


# View files tab with grid preview
def render_view_files_tab():
    st.subheader(f"Files in bucket: {BUCKET_NAME}")

    if st.button("🔄 Refresh"):
        st.rerun()  # Fixed: changed from st.experimental_rerun()

    try:
        objects = st.session_state.s3_manager.list_objects(BUCKET_NAME)
        render_image_grid(objects)
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")


# Upload files tab
def render_upload_tab():
    st.subheader("Upload Files")

    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        help="Select one or more files to upload to S3",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            col1, col2 = st.columns([3, 1])

            with col1:
                file_type = "🖼️" if is_image_file(uploaded_file.name) else "📄"
                st.write(
                    f"{file_type} {uploaded_file.name} ({format_file_size(uploaded_file.size)})"
                )

            with col2:
                if st.button(f"Upload", key=f"upload_{uploaded_file.name}"):
                    with st.spinner(f"Uploading {uploaded_file.name}..."):
                        uploaded_file.seek(0)
                        try:
                            if st.session_state.s3_manager.upload_file(
                                BUCKET_NAME, uploaded_file, uploaded_file.name
                            ):
                                st.success(
                                    f"✅ {uploaded_file.name} uploaded successfully!"
                                )
                                st.rerun()  # Fixed: changed from st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Upload error: {str(e)}")


# Download files tab
def render_download_tab():
    st.subheader("Download Files")

    try:
        objects = st.session_state.s3_manager.list_objects(BUCKET_NAME)

        if objects:
            file_names = [obj["Key"] for obj in objects]
            selected_file = st.selectbox("Select file to download", file_names)

            if selected_file:
                try:
                    file_info = st.session_state.s3_manager.get_file_info(
                        BUCKET_NAME, selected_file
                    )
                    if file_info:
                        formatted_info = format_file_info(file_info)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("File Size", formatted_info["ContentLength"])
                        with col2:
                            st.metric("Content Type", formatted_info["ContentType"])
                        with col3:
                            st.metric("Storage Class", formatted_info["StorageClass"])

                    # Show preview for images
                    if is_image_file(selected_file):
                        if st.button("👁️ Preview Image"):
                            try:
                                file_content = (
                                    st.session_state.s3_manager.download_file(
                                        BUCKET_NAME, selected_file
                                    )
                                )
                                if file_content:
                                    image = display_image_preview(file_content, 400)
                                    if image:
                                        st.image(image, caption=selected_file)
                            except Exception as e:
                                st.error(f"Preview error: {str(e)}")

                    if st.button("📥 Download File"):
                        with st.spinner("Downloading..."):
                            file_content = st.session_state.s3_manager.download_file(
                                BUCKET_NAME, selected_file
                            )

                            if file_content:
                                mime_type = (
                                    "image/*"
                                    if is_image_file(selected_file)
                                    else "application/octet-stream"
                                )
                                st.download_button(
                                    label="💾 Save File",
                                    data=file_content,
                                    file_name=selected_file,
                                    mime=mime_type,
                                )
                                st.success("✅ File ready for download!")
                except Exception as e:
                    st.error(f"Download error: {str(e)}")
        else:
            st.info("No files available for download")
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")


# Delete files tab
def render_delete_tab():
    st.subheader("Delete Files")
    st.warning("⚠️ Deletion is permanent and cannot be undone!")

    try:
        objects = st.session_state.s3_manager.list_objects(BUCKET_NAME)

        if objects:
            file_names = [obj["Key"] for obj in objects]
            selected_files = st.multiselect("Select files to delete", file_names)

            if selected_files:
                st.write("Files to be deleted:")
                for file in selected_files:
                    file_type = "🖼️" if is_image_file(file) else "📄"
                    st.write(f"• {file_type} {file}")

                confirm_delete = st.checkbox(
                    "I understand that this action cannot be undone"
                )

                if confirm_delete and st.button(
                    "🗑️ Delete Selected Files", type="primary"
                ):
                    deleted_count = 0
                    errors = []
                    for file in selected_files:
                        try:
                            if st.session_state.s3_manager.delete_file(
                                BUCKET_NAME, file
                            ):
                                deleted_count += 1
                        except Exception as e:
                            errors.append(f"Error deleting {file}: {str(e)}")

                    if deleted_count == len(selected_files):
                        st.success(f"✅ Successfully deleted {deleted_count} file(s)")
                    else:
                        st.warning(
                            f"⚠️ Deleted {deleted_count} out of {len(selected_files)} files"
                        )
                        for error in errors:
                            st.error(error)

                    st.rerun()  # Fixed: changed from st.experimental_rerun()
        else:
            st.info("No files available for deletion")
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")


# Main application
def main():
    st.set_page_config(page_title="AWS S3 Bucket Manager", page_icon="☁️", layout="wide")
    st.title("☁️ AWS S3 Bucket Manager")
    st.markdown(f"Managing bucket: **{BUCKET_NAME}**")

    initialize_session_state()

    if not st.session_state.get("aws_connected", False):
        st.error(
            "❌ Failed to connect to AWS. Please check your credentials and environment variables."
        )
        st.info("Make sure your .env file contains: ACCESS_KEY and SECRET_ACCESS_KEY")
        return

    st.success("✅ Connected to AWS successfully!")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 View Files", "⬆️ Upload", "⬇️ Download", "🗑️ Delete"]
    )

    with tab1:
        render_view_files_tab()
    with tab2:
        render_upload_tab()
    with tab3:
        render_download_tab()
    with tab4:
        render_delete_tab()


if __name__ == "__main__":
    main()
