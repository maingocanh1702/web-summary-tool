# Follow steps on the video: https://www.youtube.com/watch?v=hEPoto5xp3k&ab_channel=CodingIsFun
# pip install streamlit-option-menu
# You can find more icons from here: https://icons.getbootstrap.com/
#pip install --upgrade lxml_html_clean

import streamlit as st
from streamlit_option_menu import option_menu
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import newspaper
from newspaper import ArticleException, Article

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service
import time
import os
from bs4 import BeautifulSoup

#------------- Settings for Pages -----------
st.set_page_config(layout="wide")
if "article" not in st.session_state:
    st.session_state.article = None


#----------- Setting for Selenium -------------------------
# Old setting
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Chạy dưới dạng headless (không hiển thị trình duyệt)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -------------------------------- 1.Working with OpenAI and Langchain ------------------------
env_openai_key = "OPENAI_API_KEY"
if env_openai_key not in os.environ:
    os.environ["OPENAI_API_KEY"] = st.secrets['OPENAI_API_KEY']

prompt = ChatPromptTemplate.from_messages([
    ("system","Bạn là một chuyển gia tổng hợp báo chí. Luôn luôn sử dụng nội dung tiếng Việt cho mọi câu trả lời. "),
    ("user","""Từ nội dung bài viết tôi đưa cho bạn : {content}. Hãy tổng hợp các thông tin chính, luôn cố gắng giữ các nội dung hỗ trợ cho các thông tin chính nhiều nất có thể. Đoạn văn tổng hợp không quá {summary_length} ký tự. Câu trả lời được trả về dưới dạng HTML như trong ví dụ dưới trong đó các thông tin về tên riêng, thời gian, tiền, và các thông tin tài chính khác luôn là những thông tin quan trọng cần phải highligh bằng màu đỏ. Dưới đây là một ví dụ của bản tin trả về có thông tin được highlight:
---------
"<strong style="color: red;">Wagely</strong>, nền tảng tài chính cá nhân dành cho người lao động, đã thành công trong việc huy động <strong style="color: red;">23 triệu USD</strong> trong vòng gọi vốn mới. Điều này sẽ giúp Wagely mở rộng dịch vụ của mình và tăng cường sức mạnh tài chính.</p>
<ul>
<li>Việc huy động vốn này được dẫn đầu bởi <strong style="color: red;">QED Investors</strong> và được các nhà đầu tư hiện tại là <strong style="color: red;">Beenext, Anthemis Group và 500 Startups</strong> tsham gia.</li>
<li><strong style="color: red;">Wagely</strong> dự định sử dụng số vốn mới để mở rộng dịch vụ của mình, bao gồm việc cung cấp dịch vụ tính lương trước, hỗ trợ tài chính và quản lý tiền mặt cho người lao động.</li>
</ul>"

---------
""")
])

key_points_prompt = ChatPromptTemplate.from_messages([
    ("system","Bạn là một chuyển gia tổng hợp báo chí. Luôn luôn sử dụng nội dung tiếng Việt cho mọi câu trả lời. "),
    ("user","""Từ nội dung bài viết tôi đưa cho bạn : {content}. Hãy tóm tắt các nội dung chính ngắn gọn nhất có thể trong tối đa 10 bullet points (tuỳ thuộc vào mức độ quan trọng của thông tin). Câu trả lời được trả về dưới dạng HTML như trong ví dụ dưới trong đó các thông tin về tên riêng, thời gian, tiền, và các thông tin tài chính khác luôn là những thông tin quan trọng cần phải highligh bằng màu đỏ. Dưới đây là một ví dụ của bản tin trả về có thông tin được highlight:
---------
"<strong style="color: red;">Wagely</strong>, nền tảng tài chính cá nhân dành cho người lao động, đã thành công trong việc huy động <strong style="color: red;">23 triệu USD</strong> trong vòng gọi vốn mới. Điều này sẽ giúp Wagely mở rộng dịch vụ của mình và tăng cường sức mạnh tài chính.</p>
<ul>
<li>Việc huy động vốn này được dẫn đầu bởi <strong style="color: red;">QED Investors</strong> và được các nhà đầu tư hiện tại là <strong style="color: red;">Beenext, Anthemis Group và 500 Startups</strong> tsham gia.</li>
<li><strong style="color: red;">Wagely</strong> dự định sử dụng số vốn mới để mở rộng dịch vụ của mình, bao gồm việc cung cấp dịch vụ tính lương trước, hỗ trợ tài chính và quản lý tiền mặt cho người lao động.</li>
</ul>"

---------
""")
])
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=st.secrets['OPENAI_API_KEY'])
llm.temperature = 0.2
output_parser = StrOutputParser()
chain = prompt|llm|output_parser
keypoints_chain = key_points_prompt|llm|output_parser


# -------------------------------- 2, Working with Page content ------------------------
def get_article_content(url):
    article = newspaper.article(url)
    return article

#Keep text only
# @st.cache_data(ttl=3600)
def get_website_content(url):
    driver = None
    try:
        # Using on Local
        options = webdriver.ChromeOptions()
        # options.binary_location = '/usr/bin/chromium'
        # options.binary_location = '/Applications/Chromium.app/Contents/MacOS/Chromium'
        options.add_argument('--headless')  # Chạy trình duyệt ở chế độ headless (không hiển thị giao diện)
        options.add_argument('--disable-gpu')  # Vô hiệu hóa GPU (nếu chạy headless)
        options.add_argument('--window-size=1920,1200')  # Đặt kích thước cửa sổ trình duyệt
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)
        print(f"DEBUG:DRIVER:{driver}")
        driver.get(url)
        time.sleep(10)
        html_doc = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup.get_text()
    except Exception as e:
        print(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    finally:
        if driver is not None: driver.quit()
    return None

# 1: Summary the content in maximum of X words
# 2: Get Key points only
@st.cache_data(ttl=3600)
def get_summary(url,option=1,params=None):
    article = get_article_content(url)
    # print(f"DEBUG:ARTICLE:{article.to_json()}")
    #Summary
    if option == 1:
        summary = chain.invoke({"content": article.meta_description +"\n"+ article.text,"summary_length":params[0]})
    elif option == 2:
        summary = keypoints_chain.invoke({"content": article.meta_description+"\n"+article.text})
        #remove ```html
    start_index = summary.find("```html")
    if start_index != -1:
        end_index = summary.rfind("```")
        summary = summary[start_index + 7:end_index]
        # print(f"DEBUG:Chuỗi sau khi xử lý:{summary}")

    return {"title":article.title, "publish_date":article.publish_date, "full_content":article.text, "summary":summary,"article":article}

def show_summary(article_json):
    summary_html = f"""<div style="padding: 10px; border-radius: 5px;">
                                        <p> Nội dung tóm tắt của bài viết: </p>
                                        <h4 style="color: darkgreen;">{article_json["title"]}</h4>
                                        <p> Ngày xuất bản:{article_json["publish_date"]}</p>
                                        <p> {article_json["summary"]}</p>
                                        </div>"""
    st.markdown(summary_html, unsafe_allow_html=True)

#---------------- Page & UI/UX Components ------------------------
def main_sidebar():
    # 1.Vertical Menu
    options = ["1.Tóm tắt nội dung bài báo", "2.Trích thông tin từ web (alpha)"]

    selected_menu = option_menu(None,options,icons=["book","cup-hot"],menu_icon="cast",orientation="horizontal",default_index=0)

    if selected_menu == options[0]:
        news_summmary_page()
    elif selected_menu == options[1]:
        site_extraction_page()


def site_extraction_page():
    SAMPLE_URL = "https://www.vib.com.vn/vn/the-tin-dung/vib-financial-free"
    url = st.text_input(label="Bước 1: Nhập URL của website cần trích xuất", placeholder="https://example.com", value=SAMPLE_URL)

    p_content = """Từ nội dung trang web tôi đưa cho bạn : {content}. Hãy chọn lọc vả tổ chức lại các thông tin chính. Hiển thị câu trả lời dưới dạng thân thiện cho người đọc """

    col1, col2 = st.columns([7, 3])
    with col1:
        prompt_content = st.text_area(label="Bước 2: Chỉnh Prompt theo ý thích hoặc giữ nguyên. Chú ý giữ tên biến: {content} ", placeholder="Thông tin Prompt cần xử lý", value=p_content)
        extract_prompt = ChatPromptTemplate.from_messages([
            ("system", "Bạn là một trợ lý cho tổng giám đốc với khả năng tổ chức thông tin có cấu trúc và dễ hiểu. Luôn luôn sử dụng nội dung tiếng Việt cho mọi câu trả lời. "),
            ("user", prompt_content)
        ])
        extract_chain = extract_prompt|llm|output_parser
    with col2:
        clicked = st.button("Bước 3: Chuẩn hoá thông tin",type="primary")

    if clicked:
        content_col1, content_col2 = st.columns([5, 5])
        with content_col1:
            with st.container(border=True):
                with st.spinner("Đang tải nội dung website..."):
                    content = get_website_content(url)
                    st.write(content)
        # with content_col2:
        #     if content is not None:
        #         with st.container(border=True):
                    # with st.spinner("Đang tổ chức lại thông tin..."):
                        # summary_content = extract_chain.invoke({"content":content})
                        # st.write(summary_content)


def news_summmary_page():
    # Cliked button demo
    SAMPLE_URL = "https://cafef.vn/goc-nhin-chuyen-gia-thi-truong-chung-khoan-se-som-vuot-dinh-mot-so-nhom-co-phieu-co-the-xuat-hien-song-nganh-188240609124744797.chn"

    url = st.text_input(label="Nhập URL của bài báo cần tóm tắt: ", placeholder="https://example.com/info.html", value=SAMPLE_URL)
    clicked = st.button("Tải nội dung",type="primary")
    if clicked:
        try:
            article = get_article_content(url)
            st.session_state.article = article
        except ArticleException as e:
            st.session_state.article = None
            st.warning(f"Có lỗi xảy ra khi làm việc với URL: {e}")

    if st.session_state.article is not None:
        article = st.session_state.article
        col1, col2, col3 = st.columns([5, 1, 5])
        with col1:
            with st.spinner("Đang tải nội dung..."):
                with st.container(border=True):
                    # st.title(":rainbow[Full Content]")
                    # st.divider()

                    article_html = f"""<div style="padding: 10px; border-radius: 5px;">
                                                                <h4 style="color: darkgreen;">{article.title}</h4>
                                                                <p> Ngày xuất bản:{article.publish_date}</p>
                                                                <p> {article.meta_description}</p>
                                                                <p> {article.text}</p>
                                                                </div>
                                                                """
                    link_button_html = f"""<a href="{url}" target="_blank">
                                                                <button style='color: white; background-color: #008080; border:none; padding:10px 20px; border-radius:5px;'>
                                                                    Xem chi tiết bài viết!
                                                                </button>
                                                            </a>"""
                    st.markdown(link_button_html, unsafe_allow_html=True)
                    st.markdown(article_html, unsafe_allow_html=True)
        with col2:
            btn_300 = st.button("Tóm tắt trong 300 từ",type="secondary")
            btn_500 = st.button("Tóm tắt trong 500 từ",type="secondary")
            btn_key_points = st.button("Lọc ra các ý quan trọng ",type="secondary")
        with col3:
            if btn_300:
                with st.spinner("Tóm tắt nội dung trong 300 từ..."):
                    with st.container(border=True):
                        article_json = get_summary(url, 1, params=[300])
                        show_summary(article_json)
            if btn_500:
                with st.spinner("Tóm tắt nội dung trong 500 từ..."):
                    with st.container(border=True):
                        article_json = get_summary(url, 1, params=[500])
                        show_summary(article_json)
            if btn_key_points:
                with st.spinner("Lấy ra các ý chính..."):
                    with st.container(border=True):
                        article_json = get_summary(url, 2)
                        show_summary(article_json)




if __name__ == "__main__":
    main_sidebar()
