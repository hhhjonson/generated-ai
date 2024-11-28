import json
from config import base_config
from openai import AzureOpenAI
from get_learn_course import MicrosoftLearnGet

class StudentCourseSelector:
    def __init__(self, student_data):
        self.student_data = student_data
        self.api_endpoint=base_config.API_ENDPOINT
        self.api_key=base_config.API_KEY
        self.model_name=base_config.MODEL_NAME
        self.api_version=base_config.API_VERSION

    # 创建函数 接收学生数据 标准化GPA格式
    def standardize_student_data(self, students):
        standardize_data = []
        for student in students:
            try:
                grade = student["Grade"]
                if isinstance(grade, str):
                    if grade.endswith("GPA"):
                        grade = float(grade.replace("GPA", "").strip())
                    else:
                        grade = float(grade.strip())
                standardize_data.append({"Name": student["Name"], "Grade": grade})
            except Exception as e:
                print(f"Error processing student data: {e}")
        return standardize_data
    
    def find_courses_by_grade(self, grade):
        learn_courses=MicrosoftLearnGet()
        courses=learn_courses.get_courses_for_grade(grade)
        return courses

    # 函数调用
    def register_openai_function(self):
        # 注册函数
        functions = [
            # 标准化学生数据
            {
                "name": "standardize_student_data",
                "description": "Standardize student data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "students": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "Name": {"type": "string"},
                                    "Grade": {"type": "string"}
                                },
                                "required": ["Name", "Grade"]
                            }
                        }
                    },
                    "required": ["students"]
                }
            },
            {
            "name": "find_courses_by_grade",
            "description": "Find courses based on student grade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "grade": {"type": "number"}
                },
                "required": ["grade"]
            }
        }
        ]
        return functions

    def get_response(self):
        # 使用openai api调用
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.api_endpoint,
            functions=self.register_openai_function(),
            function_call="auto"  # 模型会自动判断是否需要调用在请求中注册的函数，如果模型的回答需要调用某个函数，会自动生成一个function_call。如果OpenAI的响应需要调用某个函数，它会在返回的响应中包括一个function_call字段
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a course recommendation expert who helps students find suitable courses based on their grades."
                },
                {
                    "role": "user",
                    "content": "Can you standardize the student grades?",
                },
                {
                    "role": "user",
                    "content": "Based on the grades, can you also find suitable courses for the students?"
                }
            ],
            functions=[self.register_openai_function()],
            function_call="auto"
        )

        response_message = response.choices[0].message
        print("模型返回的响应：")
        print(response_message)

        if "function_call" in response_message:
            print("推荐的函数调用：")
            function_name = response_message['function_call']['name']
            function_args = json.loads(response_message['function_call']['arguments'])
            print(f"函数名称: {function_name}")
            print(f"函数参数: {function_args}")

            # 根据函数名称调用实际的 Python 函数
            available_functions = {
                "standardize_student_data": self.standardize_student_data,
                 "find_courses_by_grade": self.find_courses_by_grade
            }

            function_to_call = available_functions[function_name]
            function_response = function_to_call(**function_args)

            print("函数调用的输出：")
            print(function_response)

            # 将助手响应和函数响应添加到消息中
            messages = [
                {
                    "role": response_message['role'],
                    "function_call": {
                        "name": function_name,
                        "arguments": response_message['function_call']['arguments'],
                    },
                    "content": None
                },
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            ]

            # 发起第二次请求，获取自然语言响应
            second_response = AzureOpenAI.ChatCompletion.create(
                messages=messages,
                model=self.model_name,  
                function_call="auto",
                functions=self.register_openai_function(),
                temperature=0  # 控制随机性，设为 0 使响应更为确定
            )

            # 输出最终的自然语言响应
            print("最终的自然语言响应：")
            print(second_response.choices[0].message["content"])

if __name__ == "__main__":
    # 创建学生信息
    students = [
        {"Name": "Alice", "Grade": 3.7},
        {"Name": "Bob", "Grade": "3.7GPA"}
    ]

    # 创建对象
    standardizer = StudentCourseSelector(students)
    # 调用函数
    standardized_data = standardizer.standardize_student_data(students)
    print(standardized_data)
