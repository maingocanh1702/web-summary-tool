
SUMMARY_MESSAGES = [
    ("system","Bạn là một thư ký cho tổng giám đốc. Luôn luôn sử dụng nội dung tiếng Việt cho mọi câu trả lời. "),
    ("user","""Tóm tắt ngắn gọn và xúc tích nội dung bài viết dưới đây trong không quá 200 từ (hoặc một phần tư trang giấy). Nội dung bài viết như sau:[{content}]. 
    
    Hãy trả lời dưới dạng HTML trong đó các thông tin về tên riêng, thời gian, số liệu, tiền, và các thông tin tài chính khác luôn là những thông tin quan trọng cần phải highlight bằng màu đỏ như ví dụ format của nội dung quan trọng:
---------
Số tiền đầu tư lên đến <strong style="color: red;"> 10 triệu đô </strong> 
---------""")
]


GET_KEYPOINTS_MESSAGES = [
    ("system","Bạn là một trợ lý cho tổng giám đốc với khả năng tổ chức thông tin có cấu trúc và dễ hiểu."),
    ("user","""Hãy tổ chức lại thông tin dưới đây một cách ngắn gọn, cấu trúc và thân thiện với người đọc: {content} """)
]

