import random
import io
import uuid
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class VerificationCode(object):

    # 数字验证码
    @staticmethod
    def num_random_list(length):
        list = []
        for i in range(length):
            list.append(str(random.randrange(10)))

        return ''.join(list)

    # 随机验证码
    @staticmethod
    def mixture_code(length):
        code_list = []
        for i in range(0, 10):
            code_list.append(str(i))
        for i in range(65, 91):  # A-Z
            code_list.append(chr(i))
        for i in range(97, 123):  # a-z
            code_list.append(chr(i))

        myslice = random.sample(code_list, length)
        return myslice

    @staticmethod
    # 生成验证码接口
    def generate_verify_image(size=(120, 30),
                              img_type="GIF",
                              mode="RGB",
                              bg_color=(255, 255, 255),
                              fg_color=(0, 0, 255),
                              font_size=100,
                              font_type="./DejaVuSans.ttf",
                              length=4,
                              draw_lines=False,
                              n_line=(1, 2),
                              draw_points=True,
                              point_chance=2,
                              save_img=False,
                              code_length=6):
        """
        生成验证码图片
        :param size: 图片的大小，格式（宽，高），默认为(120, 30)
        :param chars: 允许的字符集合，格式字符串
        :param img_type: 图片保存的格式，默认为GIF，可选的为GIF，JPEG，TIFF，PNG
        :param mode: 图片模式，默认为RGB
        :param bg_color: 背景颜色，默认为白色
        :param fg_color: 前景色，验证码字符颜色，默认为蓝色#0000FF
        :param font_size: 验证码字体大小
        :param font_type: 验证码字体，默认为 DejaVuSans.ttf
        :param length: 验证码字符个数
        :param draw_lines: 是否划干扰线
        :param n_line: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
        :param draw_points: 是否画干扰点
        :param point_chance: 干扰点出现的概率，大小范围[0, 100]
        :param save_img: 是否保存为图片
        :return: [0]: 验证码字节流, [1]: 验证码图片中的字符串
        """

        width, height = size  # 宽， 高
        img = Image.new(mode, size, bg_color)  # 创建图形
        draw = ImageDraw.Draw(img)  # 创建画笔

        def create_lines():
            """绘制干扰线"""

            line_num = random.randint(*n_line)  # 干扰线条数

            for i in range(line_num):
                # 起始点
                begin = (random.randint(
                    0, size[0]), random.randint(0, size[1]))
                # 结束点
                end = (random.randint(0, size[0]),
                       random.randint(0, size[1]))
                draw.line([begin, end], fill=(0, 0, 0))

        def create_points():
            """绘制干扰点"""

            chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

            for w in range(width):
                for h in range(height):
                    tmp = random.randint(0, 100)
                    if tmp > 100 - chance:
                        draw.point((w, h), fill=(0, 0, 0))

        def create_strs():
            """绘制验证码字符"""

            c_chars = VerificationCode.mixture_code(code_length)
            strs = ' %s ' % ' '.join(c_chars)  # 每个字符前后以空格隔开

            # font = ImageFont.truetype(font_type, font_size)
            # font = ImageFont.truetype("arial.ttf", 15)
            # font = ImageFont.truetype('/Library/Fonts/Arial.ttf', 15)
            # print(help(ImageFont.load_default))
            font = ImageFont.load_default()
            print(help(font.font))
            font_width, font_height = font.getsize(strs)

            draw.text(((width - font_width) / 3, (height - font_height) / 3),
                      strs, font=font, fill=fg_color)

            return ''.join(c_chars)

        if draw_lines:
            create_lines()
        if draw_points:
            create_points()
        strs = create_strs()

        # 图形扭曲参数
        params = [1 - float(random.randint(1, 2)) / 100,
                  0,
                  0,
                  0,
                  1 - float(random.randint(1, 10)) / 100,
                  float(random.randint(1, 2)) / 500,
                  0.001,
                  float(random.randint(1, 2)) / 500
                  ]
        img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲

        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）

        mstream = io.BytesIO()
        img.save(mstream, img_type)
        mstream.seek(0)
        data = base64.b64encode(mstream.read()).decode()
        # data = mstream.encode('base64')

        if save_img:
            img.save("validate.gif", img_type)

        return data, strs

    @staticmethod
    def generate_uuid():
        uuid_text = uuid.uuid1()

        return str(uuid_text)
