import streamlit as st

from llm.splitter import splitText

# list of candy-color plain backgrounds
candy_colors = [
    "linear-gradient(135deg, #f6d365 0%, #fda085 100%)",
    "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    "linear-gradient(135deg, #5ee7df 0%, #b490ca 100%)",
    "linear-gradient(135deg, #c3cfe2 0%, #c3cfe2 100%)",
    "linear-gradient(135deg, #f6d365 0%, #fda085 100%)",
    "rgb(255, 99, 132)",
    "rgb(54, 162, 235)",
    "rgb(255, 206, 86)",
    "rgb(75, 192, 192)",
    "rgb(153, 102, 255)",
]


def main():
    # Set page configuration
    st.set_page_config(layout="wide")

    # Create two vertical columns
    col1, col2 = st.columns(2)

    # File uploader in the left column
    with col1:
        st.header("File Upload")
        uploaded_file = st.file_uploader("Choose a text file", type=['txt'])

    # File content display in the right column
    with col2:
        st.header("File Content")
        if uploaded_file is not None:
            # Read and display the file content
            content = uploaded_file.getvalue().decode("utf-8")
            # st.text_area("", value=content, height=400)

            # split content into chunks
            chunks = splitText(content, context_window_size=1024)
            for chunk in chunks:
                # print each chunk with a random candy-color background
                st.html(
                    f'<div style="background: '
                    f'{candy_colors[chunk.paragraph_count % len(candy_colors)]}; padding: 10px; '
                    f'border-radius: 5px;">{chunk.text}</div>',
                )
                st.html("<div></div>")
        else:
            st.info("Please upload a file to view its content")


if __name__ == "__main__":
    main()
