import pandas as pd


def split_tiktok_txt(filename):
    with open(filename, 'r', encoding='utf8') as f:
        lines = [line.strip().split('---') for line in f.readlines()]
    temp_dict = {
        'username': [],
        'password': [],
        'email': [],
        'email_password': [],
        'cookie': []
    }
    for line in lines:
        county = 0
        for i in temp_dict:
            try:
                temp_dict[i].append(line[county].split('：')[1])
            except:
                temp_dict[i].append(line[county])
            county += 1
    df = pd.DataFrame(temp_dict)
    print(df)
    df.to_csv('10_tiktok.csv', index=False)  # index=False 表示不写入索引列


def generate_import_template():
    ip_list = pd.read_csv('20个IP美国.csv', encoding='utf8')
    account_list = pd.read_csv('10_tiktok.csv', encoding='utf8')

    template_dict = {
        'name': ['' for _ in range(len(ip_list))],  # 浏览器环境名称
        'remark': ['' for _ in range(len(ip_list))],  # 浏览器环境备注
        'tab': ['' for _ in range(len(ip_list))],  # 默认打开标签页
        'platform': ['' for _ in range(len(ip_list))],  # 平台域名
        'username': ['' for _ in range(len(ip_list))],  # 账号用户名
        'password': ['' for _ in range(len(ip_list))],  # 密码
        'fakey': ['' for _ in range(len(ip_list))],  # F2A二次验证码
        'cookie': ['' for _ in range(len(ip_list))],  # cookie
        'proxytype': ['http' for _ in range(len(ip_list))],  # 代理类型
        'ipchecker': ['' for _ in range(len(ip_list))],  # IP查询渠道
        'proxy': ['' for _ in range(len(ip_list))],  # 代理参数 例子:192.168.0.1:8000:myproxy:password
        'proxyurl': ['' for _ in range(len(ip_list))],  # 移动代理的刷新url 仅用于移动代理
        'proxyid': ['' for _ in range(len(ip_list))],  # 代理管理中的代理ID
        'ip': ['' for _ in range(len(ip_list))],  # 填写匹配动态代理地区的IP。例子:192.168.0.1
        'countrycode': ['' for _ in range(len(ip_list))],  # 填写动态代理的国家/地区。例子:us
        'regioncode': ['' for _ in range(len(ip_list))],  # 填写动态代理的州/省。例子:ak
        'citycode': ['' for _ in range(len(ip_list))],  # 填写动态代理的城市。例子:adak
        'ua': ['' for _ in range(len(ip_list))],  # 填写浏览器UA
        'resolution': ['' for _ in range(len(ip_list))]  # 填写浏览器分辨率
    }

    for count in range(len(ip_list)):
        # 网页设置
        template_dict['tab'][count] = 'https://www.tiktok.com'
        template_dict['platform'][count] = 'tiktok.com'

        # 账号数据
        template_dict['username'][count] = account_list['username'][count]

        template_dict['password'][count] = account_list['password'][count]
        template_dict['cookie'][count] = account_list['cookie'][count]

        # IP代理
        template_dict['proxy'][
            count] = f"{ip_list['Host'][count]}:{ip_list['Port'][count]}:{ip_list['User'][count]}:{ip_list['Pass'][count]}"

    temp_df = pd.DataFrame(template_dict)
    print(temp_df)
    temp_df.to_excel(r'C:\Users\Admin\Desktop\result.xlsx', index=False)


if __name__ == '__main__':
    # split_tiktok_txt('tiktok_30.txt')
    generate_import_template()
