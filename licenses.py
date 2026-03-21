#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys

def generate_license(author: str, emails: list) -> str:
    """生成中英交替的 FLEX License 文本（英文在前，中文在后）"""
    year = datetime.datetime.now().year
    email_lines = "\n".join(f"  - {email}" for email in emails)

    # 构建各部分的英文和中文内容（交替排列）
    sections = [
        # 标题（英文 + 中文）
        ("# FLEX License (Flexible License Edition)", "# FLEX 许可证（灵活许可版）"),
        ("", ""),  # 空行分隔
        (f"Copyright (c) {year} {author}", f"版权所有 (c) {year} {author}"),
        ("", ""),

        # 1. 定义
        ("### 1. Definitions", "### 1. 定义"),
        ("""- **“Library”** means the collection of software, code, media files, and other resources published by the Author under this License.
- **“Non-Commercial Use”** means use that does not directly or indirectly aim for commercial profit, including but not limited to personal learning, research, non-profit projects, non-commercial parts of open source projects, etc.
- **“Commercial Use”** means using the Library or its derivative works for any commercial profit scenario, including but not limited to sales, paid services, advertising revenue, or embedding in paid products.
- **“Modification”** means any adaptation, translation, optimization, feature addition, bug fix, or other alteration that changes the original content of the Library.
- **“Redistribution”** means making the original Library or modified versions available to any third party in any form (copying, network transmission, integration into other projects, etc).""",
         """- **“库”** 指由作者发布并声明适用本许可证的软件、代码、媒体文件等资源的集合。
- **“非商业使用”** 指不以直接或间接获取商业利益为目的的使用，包括但不限于个人学习、研究、非营利项目、开源项目中的非商业部分等。
- **“商业使用”** 指将库或其衍生作品用于销售、收费服务、广告收益、嵌入付费产品等任何直接或间接的商业盈利场景。
- **“修改”** 指对库进行任何形式的改编、翻译、优化、增加功能或修复错误等改变原始内容的行为。
- **“二次分发”** 指将原始库或修改后的版本以任何形式（复制、网络传输、集成至其他项目等）提供给第三方。"""),
        ("", ""),

        # 2. 非商业使用授权
        ("### 2. Non-Commercial Use Grant", "### 2. 非商业使用授权"),
        ("""Subject to the terms of this License, the Author grants any individual or organization **a free, irrevocable, worldwide non-commercial use right** to:
- Copy, display, and run the resources in the Library;
- Use the Library in non-commercial projects.

This grant does not require the user to contact the Author separately, but the copyright notice of this License must be retained.""",
         """在遵守本许可证条款的前提下，作者授予任何个人或组织**免费、不可撤销、全球范围内的非商业使用权**，允许其：
- 复制、展示、运行库中的资源；
- 将库用于非商业项目中。

该授权不要求使用者另行联系作者，但需保留本许可证的版权声明。"""),
        ("", ""),

        # 3. 商业使用、修改与二次分发
        ("### 3. Commercial Use, Modification, and Redistribution", "### 3. 商业使用、修改与二次分发"),
        (f"""**Commercial use, modification, or redistribution (including modified versions) of the Library requires explicit prior written permission from the Author.**  
Permission requests should be sent to the following email addresses:
{email_lines}

The Author may grant permission at their sole discretion and may impose additional conditions (such as attribution, revenue sharing, etc.).  
Any commercial use, modification, or redistribution without authorization is considered an infringement.""",
         f"""**商业使用、修改库、或将库（包括修改版）进行二次分发，均必须事先获得作者的明确书面授权。**  
授权请求应通过以下邮箱联系作者：
{email_lines}

作者可自行决定是否授予授权，并可附加额外条件（如署名、收益分成等）。  
未经授权的商业使用、修改或分发均视为侵权。"""),
        ("", ""),

        # 4. 与其他许可证的兼容性
        ("### 4. Compatibility with Other Licenses", "### 4. 与其他许可证的兼容性"),
        ("""This License **applies only to content that is original to the Author or that the Author is legally authorized to relicense**.  
The Library may contain resources obtained from other sources, which **retain their original licenses**. In case of conflict between this License and any third-party license, **the third-party license shall prevail**.  
Users of the Library are responsible for identifying the original license information of each component and complying with the applicable terms.""",
         """本许可证**仅适用于作者原创或经合法授权可再许可的内容**。  
库中可能包含从其他来源获取的资源，这些资源**保留其原始许可证**。若本许可证与任何第三方许可证发生冲突，**以第三方许可证为准**。  
使用者在使用库时，有义务自行识别库中各组成部分的原始许可信息，并遵守相应规定。"""),
        ("", ""),

        # 5. 版权与侵权声明
        ("### 5. Copyright Infringement", "### 5. 版权与侵权声明"),
        ("""The Author respects the intellectual property rights of others. If any rights holder believes that the Library contains infringing content, please contact the Author at the email addresses above, and the Author will remove the relevant content after verification.""",
         """作者尊重他人知识产权。若任何权利人认为库中包含侵权内容，请联系作者（邮箱同上），作者将在核实后移除相关部分。"""),
        ("", ""),

        # 6. 免责声明
        ("### 6. Disclaimer", "### 6. 免责声明"),
        ("""The Library is provided “AS IS”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.  
In no event shall the Author be liable for any direct, indirect, incidental, special, exemplary, or consequential damages arising out of the use of the Library, even if advised of the possibility of such damages.""",
         """本库“按原样”提供，作者不作任何明示或暗示的保证，包括但不限于适销性、特定用途适用性、不侵权等。  
在任何情况下，作者均不对因使用本库而产生的任何直接、间接、偶然、特殊或惩罚性损害承担责任，即使已被告知此类损害的可能性。"""),
    ]

    # 构建最终文本（英文在前，中文在后，每对之间空一行）
    lines = []
    for eng, chn in sections:
        if eng:
            lines.append(eng)
        if chn:
            lines.append(chn)
        # 每对之后添加空行（除最后）
        if eng or chn:
            lines.append("")
    # 删除末尾多余空行
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)

def main():
    print("=== FLEX License 生成器 (Bilingual Alternating) ===")
    user_input = input("请输入作者姓名和邮箱（格式：作者姓名|邮箱1|邮箱2|...）：").strip()
    if not user_input:
        print("错误：输入不能为空。")
        sys.exit(1)

    parts = [p.strip() for p in user_input.split('|')]
    author = parts[0]
    emails = parts[1:] if len(parts) > 1 else []
    if not emails:
        print("警告：未提供邮箱，授权联系部分将显示为空。")

    license_content = generate_license(author, emails)

    output_file = "LICENSE"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(license_content)

    print(f"\n许可证已生成并保存至：{output_file}")

if __name__ == "__main__":
    main()