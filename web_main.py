import os
import time
import gradio as gr
from RAG import RAG
from dotenv import load_dotenv

load_dotenv()
rag = RAG()

def add_text(history,text):
    print('add_text')
    history = history + [(text, None)]
    return history, gr.update(value='',interactive=True)

def upload_file(history,file):
    print('upload file')
    print(file.name)
    """
        1.上传文档
        2.文档切割
        3.文档向量话
        4.文档检索
    """
    rag.DataBase.load_dir(file.name)
    history = history + [((file.name,), None)]
    return history

def chat(history):
    print('chat')
    print("history: ", history)
    msg = history[-1][0]
    if isinstance(msg, tuple):
        ans = "文件上传成功！"
        history[-1][0] = msg[0]
    else:
        """
        1.根据用户提问，调用检索服务，获取与问题相关的本地知识库信息
        2.调用大模型对信息进行整合
        3.解析大模型结果并返回
        """
        # ans = "待调用检索服务大模型，敬请期待！"
        response = rag.as_retrieval_qa()({"query":msg})
        # response = rag.DataBase.as_reteiever()
        ans = '' 
        try:
            print(response)
            ans = response['result']
        except Exception as err:
            print("error: {}, response: {}".format(err, response))
        
    history[-1][1] = ''
    print("history: ", history)
    for ch in ans:
        history[-1][1] += ch
        time.sleep(0.01)
        yield history[-1:]
    return history

with gr.Blocks() as demo:
    with gr.Tab("RAG文本对话"):
        model_list = ["百度零一34b大模型", "ChatGLM3"]
        input_model_list = gr.Dropdown(choices=model_list, label="模型选择")

        chatbot = gr.Chatbot(
            [],
            elem_id='chatbot',
            bubble_full_width=False,
        ).style(height=400, width=600)

        # 自定义 CSS 样式，添加头像，控制气泡最大宽度
        demo.css = """
            .message.bot, .message.user {
                max-width: 400px;  /* 控制气泡的最大宽度 */
            }
        """

        with gr.Row():
            txt = gr.Textbox(
                scale=4,
                show_label=False,
                placeholder='输入文本并回车，或者上传本地文件',
                container=False
            )
            btn_send = gr.Button("发送", size="sm")
            btn = gr.UploadButton("文件", file_types=["folder"])

        txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
            chat, chatbot, chatbot
        )

        # 绑定发送按钮的点击事件
        btn_send.click(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
            chat, chatbot, chatbot
        )

        file_msg = btn.upload(upload_file, [chatbot, btn], [chatbot], queue=False).then(
            chat, chatbot, chatbot
        )

demo.queue()

if __name__ == '__main__':
    demo.launch()
