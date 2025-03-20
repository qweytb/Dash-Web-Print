
ENABLE_IP_WHITELIST = False  # 是否启用白名单
ENABLE_IP_BLACKLIST = False  # 是否启用黑名单

# 白名单和黑名单
WHITE_IP_LIST = [
    '192.0.0.1',
    '192.168.1.0/24',  # 支持子网
    '10.0.0.0/8',     # 支持更大的IP范围
]

BLACK_IP_LIST = [
    '203.0.113.1',    # 单个黑名单 IP
    '198.51.100.0/24', # 黑名单子网
]