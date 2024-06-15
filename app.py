import streamlit as st
from streamlit_option_menu import option_menu
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import newspaper
from newspaper import ArticleException

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
from bs4 import BeautifulSoup
from database.crawler_repository import WebCrawlerRepository, CrawledArticle, CrawledUrl
from utils import utils, prompt_lib

# ------------- Settings for Pages -----------
st.set_page_config(layout="wide")
if "article" not in st.session_state:
    st.session_state.article = None
# current_action = [0: Nothing, 11: Summarize news, 12: Get key points, 22: Extract web infor
SHOW_SUMMARY = "show_summary"
SHOW_KEYPOINTS = "show_keypoints"
NO_ACTION = "no_action"
if "current_action" not in st.session_state:
    st.session_state.current_action = NO_ACTION

MONGODB_CONNECTION_STRING = st.secrets["MONGODB_CONNECTION_STRING"]
repository = WebCrawlerRepository(MONGODB_CONNECTION_STRING)

# -------------------------------- 1.Init Langchain & Open AI ------------------------
env_openai_key = "OPENAI_API_KEY"
if env_openai_key not in os.environ:
    os.environ["OPENAI_API_KEY"] = st.secrets['OPENAI_API_KEY']

# Create prompts
summary_prompt = ChatPromptTemplate.from_messages(prompt_lib.SUMMARY_MESSAGES)
get_keypoints_prompt = ChatPromptTemplate.from_messages(prompt_lib.GET_KEYPOINTS_MESSAGES)

llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=st.secrets['OPENAI_API_KEY'])
llm.temperature = 0.5
output_parser = StrOutputParser()

# Create chain
summary_chain = summary_prompt | llm | output_parser
get_keypoints_chain = get_keypoints_prompt | llm | output_parser


# -------------------------------- 2, Working with Page content ------------------------
# Keep text only
@st.cache_data(ttl=3600)
def get_website_content(url):
    driver = None
    try:
        # Using on Local
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Chạy trình duyệt ở chế độ headless (không hiển thị giao diện)
        options.add_argument('--disable-gpu')  # Vô hiệu hóa GPU (nếu chạy headless)
        options.add_argument('--window-size=1920,1200')  # Đặt kích thước cửa sổ trình duyệt
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        st.write(f"DEBUG:DRIVER:{driver}")
        driver.get(url)
        time.sleep(7)
        html_doc = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup.get_text()
    except Exception as e:
        st.write(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    finally:
        if driver is not None: driver.quit()
    return None


# 1: Summary the content in maximum of X words
# 2: Get Key points only
def invoke_chatgpt(content, action_type=1, params=None):
    # Summary
    # print(f"DEBUG:OPTION:{option}:REQUEST:{content}")
    if action_type == 1:
        summary = summary_chain.invoke({"content": content, "summary_length": params[0]})
        # print(f"DEBUG:CHATGPT_RESPONSE:{summary}")
    elif action_type == 2:
        summary = get_keypoints_chain.invoke({"content": content})
        # print(f"DEBUG:CHATGPT_KEYPOINTS_RESPONSE:{summary}")
    # remove ```html
    summary = utils.remove_markdown_code(summary)
    return summary

# ---------------- Display the results ------------------------
def show_summary(article, content):
    summary_html = f"""<div style="padding: 10px; border-radius: 5px;">
                                        <p> Nội dung tóm tắt của bài viết: </p>
                                        <h4 style="color: darkgreen;">{article.title}</h4>
                                        <p> Ngày xuất bản:{article.publish_date}</p>
                                        <p> {content}</p>
                                        </div>"""
    st.markdown(summary_html, unsafe_allow_html=True)

def gen_summary_content(article,regen = False):
    if (article.summary == "" or regen == True):
        with st.spinner("Summarizing..."):
            summary = invoke_chatgpt(article.description + "\n" + article.content, 1, params=[300])
            article.summary = summary
            repository.save_article(article)  # update database


def gen_keypoints_content(article,regen = False):
    if (article.keypoints == "" or regen == True):
        with st.spinner("Getting key points..."):
            keypoints = invoke_chatgpt(article.description + "\n" + article.content, 2)
            article.keypoints = keypoints
            repository.save_article(article)  # update database

# ---------------- Page & UI/UX Components ------------------------
# Horizontal Navigation Menu
def main_sidebar():
    options = ["1.Tóm tắt Tin tức", "2.Lọc nội dung chính của Website bất kì "]
    selected_menu = option_menu(None, options, icons=["book", "cup-hot"], menu_icon="cast", orientation="horizontal",
                                default_index=0)
    if selected_menu == options[0]:
        news_summmary_page()
    elif selected_menu == options[1]:
        site_extraction_page()


def site_extraction_page():
    SAMPLE_URL = "https://www.vib.com.vn/vn/the-tin-dung/vib-financial-free"
    url = st.text_input(label="Website URL", placeholder="https://example.com",
                        value=SAMPLE_URL)

    p_content = """Hãy tổ chức lại thông tin dưới đây một cách ngắn gọn, cấu trúc và thân thiện với người đọc: {content}"""

    col1, col2 = st.columns([7, 3])
    with col1:
        prompt_content = st.text_area(
            label="You can change the prompt! Remember: keep {content} as input variable ",
            placeholder="No prompt", value=p_content)
        extract_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Bạn là một trợ lý cho tổng giám đốc với khả năng tổ chức thông tin có cấu trúc và dễ hiểu. Luôn luôn sử dụng nội dung tiếng Việt cho mọi câu trả lời. "),
            ("user", prompt_content)
        ])
        extract_chain = extract_prompt | llm | output_parser
    with col2:
        clicked = st.button("Extract information", type="primary")

    if clicked:
        content_col1, content_col2 = st.columns([5, 5])
        with content_col1:
            with st.container(border=True):
                with st.spinner("Đang tải nội dung website..."):
                    content = get_website_content(url)
                    st.write(content)
        with content_col2:
            if content is not None:
                with st.container(border=True):
                    with st.spinner("Đang tổ chức lại thông tin..."):
                        summary_content = extract_chain.invoke({"content": content})
                        st.write(summary_content)


def news_summmary_page():
    # Cliked button demo
    SAMPLE_URL = "https://cafef.vn/goc-nhin-chuyen-gia-thi-truong-chung-khoan-se-som-vuot-dinh-mot-so-nhom-co-phieu-co-the-xuat-hien-song-nganh-188240609124744797.chn"

    INPUT_URL = st.text_input(label="News URL: ", placeholder="https://example.com/info.html", value=SAMPLE_URL)
    if INPUT_URL != "":
        URL = utils.remove_query_string(INPUT_URL)  # cleaned URL
    else:
        st.warning("Please input the URL")

    clicked = st.button("Extract Content", type="primary")
    if clicked:
        st.session_state.working_url = URL
        st.session_state.current_action = NO_ACTION
        try:
            # Check article is existing or not
            article = repository.get_article(URL)
            if article is None:
                news = newspaper.article(URL)
                article = CrawledArticle(url=URL, title=news.title, description=news.meta_description,
                                         publish_date=news.publish_date, source=utils.get_domain_name(URL),
                                         content=news.text, summary="", keypoints="", keywords=news.meta_keywords)
                repository.save_article(article)
            st.session_state.article = article
        except ArticleException as e:
            st.session_state.article = None
            st.warning(f"Extract Failed: {e}")

    if st.session_state.article is not None:
        article = st.session_state.article
        col1, col2, col3 = st.columns([5, 1, 5])
        with col1:  # Show content
            with st.spinner("Loading..."):
                with st.container(border=True):
                    article_html = f"""<div style="padding: 10px; border-radius: 5px;">
                                                                <h4 style="color: darkgreen;">{article.title}</h4>
                                                                <p> Publish Date:{article.publish_date}</p>
                                                                <p> {article.description}</p>
                                                                <p> {article.content}</p>
                                                                </div>
                                                                """
                    link_button_html = f"""<a href="{URL}" target="_blank">
                                                                <button style='color: white; background-color: #008080; border:none; padding:10px 20px; border-radius:5px;'>
                                                                    Original Link!
                                                                </button>
                                                            </a>"""
                    st.markdown(link_button_html, unsafe_allow_html=True)
                    st.markdown(article_html, unsafe_allow_html=True)
        with col2:
            btn_summary = st.button("Get Summary", type="primary")
            btn_key_points = st.button("Get Key Points ", type="primary")
            btn_regen = st.button("I don't like this! regenerate content", type="secondary")
        with col3:
            if btn_summary:
                st.session_state.current_action = SHOW_SUMMARY
                gen_summary_content(article)
            if btn_key_points:
                st.session_state.current_action = SHOW_KEYPOINTS
                gen_keypoints_content(article)
            if  btn_regen:
                if st.session_state.current_action == SHOW_SUMMARY:
                    gen_summary_content(article,regen=True)
                elif st.session_state.current_action == SHOW_KEYPOINTS:
                    gen_keypoints_content(article,regen=True)

            with st.container(border=True):
                if st.session_state.current_action == SHOW_SUMMARY:
                    show_summary(article, article.summary)
                elif st.session_state.current_action == SHOW_KEYPOINTS:
                    show_summary(article, article.keypoints)


if __name__ == "__main__":
    main_sidebar()
