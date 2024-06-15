
SUMMARY_MESSAGES = [
    ("system","Bạn là một thư ký cho tổng giám đốc. Luôn luôn sử dụng nội dung tiếng Việt cho mọi câu trả lời. "),
    ("user","""Tóm tắt ngắn gọn và xúc tích nội dung bài viết dưới đây trong không quá 200 từ (hoặc một phần tư trang giấy). Nội dung bài viết như sau:[{content}]. 
    
    Hãy trả lời dưới dạng HTML trong đó các thông tin về tên riêng, thời gian, số liệu, tiền, và các thông tin tài chính khác luôn là những thông tin quan trọng cần phải highlight bằng màu đỏ như ví dụ format của nội dung quan trọng:
---------
Số tiền đầu tư lên đến <strong style="color: red;"> 10 triệu đô </strong> 
---------""")
]

GET_KEYPOINTS_MESSAGES = [
    ("system","Bạn là một chuyển gia tổng hợp báo chí. Luôn luôn sử dụng nội dung tiếng Việt cho mọi câu trả lời. "),
    ("user","""Từ nội dung bài viết tôi đưa cho bạn : {content}. Hãy tóm tắt các nội dung chính ngắn gọn nhất có thể trong tối đa 10 bullet points (tuỳ thuộc vào mức độ quan trọng của thông tin). Hãy trả lời dưới dạng HTML trong đó các thông tin về tên riêng, thời gian, tiền, và các thông tin tài chính khác luôn là những thông tin quan trọng cần phải highlight bằng màu đỏ như ví dụ dưới:
---------
<ul>
<li>Thị trường mục tiêu bao gồm các quốc gia <strong style="color: red;">Đông Nam Á/strong>.</li>
<li>Số tiền đầu tư lên đến <strong style="color: red;">10 triệu đô</strong>.</li>
<li>Dự án dự kiến hoàn thành trong vòng <strong style="color: red;">2 năm</strong>.</li>
</ul>
---------""")
]

